#####################################################
#
# Read seult submission DB and creates public 
# JSON to show in web.
#
# Usage: python create_public_results.py result_db.json
#
# Final structure would be something like this
#
#   public_json = {
#   	"<uuid>" : {
#
#   		"deviceInfo" : {
#               "uuid": <uuid>,
#               "deviceName": "GeForce GT 650M",
#               "deviceVersion": "OpenCL 1.2",
#               "driverVersion": "8.24.9 310.40.25f01",
#               "openCLCVersion": "OpenCL C 1.2",
#               "platformName": "Apple"
#           },
#
#   		"results" : { 
#             "2014-04-09T22:45:47+03:00" : {
#                   "date" : "2014-04-09T22:45:47+03:00",
#   				"tests" : [
#   					{
#   						"test" : "kernel/cast_and_do_arithmetics_with_local_pointer.cl",
#   						"result": "PASS",
#   						"output": "N/A"
#   					}
#   				]
#             }
#   	    }
#   	}
#   }
#

import json
import copy
import fileinput
import sys

print >>sys.stderr,"Usage: create_public_results.py < result_db.json"
results = json.loads("".join(fileinput.input()))

# dictionary of all test results in db organized by device.
devices = {}

def read_output(output_msg):
	# TODO: get test name and status and set output if exist... 
	#       use some cencorship logic to find basepath 
	#       e.g. from /<cencored>/tools/ocl-tester/ocl-tester and 
	#                 /<cencored>/tests
	return "N/A"

def resolve_device_struct(report, device_id):
	selected_device = None
	for device in report['message']['devices']['deviceIdentifiers']:
		platform_and_device = device['platformName'] + " / " + device['deviceName']
		if platform_and_device in device_id:
			selected_device  = device
			break

	if selected_device is None:
		raise Exception("Could not find corresponding device from report:" + device_id)

	result_device_dict = copy.deepcopy(selected_device)
	del result_device_dict['id']
	device_hash = abs(hash(json.dumps(result_device_dict, sort_keys=True)))
	result_device_dict['uuid'] = device_hash
	return result_device_dict

# Go through result DB and order all results by platform / driver infos
for hash_code,report in results.iteritems():
	for test in report['message']['tests']:
		device_id,test_name = test['name'].split(" :: ", 1)
		device_struct = resolve_device_struct(report, device_id)

		device_data = devices.get(device_struct['uuid'], { 
			'deviceInfo' : device_struct,
			'results' : {}
		})
		devices[device_struct['uuid']] = device_data

		result_date = report['sender']['received_at']

		test_result = { 
			'test': test_name, 
			'result': test['code'], 
			'output': read_output(test['output'])
		}

		result_entry = device_data['results'].get(result_date, { 'date' : result_date, 'tests' : [] })
		result_entry['tests'].append(test_result)
		device_data['results'][result_date] = result_entry


# print "JSON_CALLBACK(" + json.dumps(devices, indent=2) + ");"
# print json.dumps(devices, indent=2)
print "window.raw_test_data = " + json.dumps(devices, indent=2) + ";"
