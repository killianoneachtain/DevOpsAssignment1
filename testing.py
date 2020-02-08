#!/usr/bin/env python3
import boto3
import sys
import subprocess

instanceID = sys.argv[1]


#------- Status Checking Routine -----------
# We will not proceed to SSH into the instance until the Status Checks
# are complete and both have been passed.
#-----------------------------------------

status_check_cmd = 'aws ec2 describe-instance-status --instance-id %s | egrep \'ok|passed\' | wc -l' % (instanceID)

checkCount = ""

while checkCount != "b\'4\\n\'" :
		try:
				process = subprocess.run(status_check_cmd, shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
				output = str(process.stdout)
				print ("Output is : \"" + output + "\"")
				
				if output == "b\'4\\n\'":
					print ("EXITING THE LOOP")
					break
		except Exception as error:
				print (error)		

#process = subprocess.run(status_check_cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
#output = str(process.stdout)
#print ("Output is : \"" + output + "\"")

