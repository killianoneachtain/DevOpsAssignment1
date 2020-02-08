#!/usr/bin/env python3
import os
import boto3
import botocore
import subprocess

import sys
import time
from datetime import datetime

# Function to get current date:time format
def get_datetime():
    # Use current date/time to get a jpg file name format (day month year Hour Minute Second)
    now = datetime.now()    
    current = now.strftime("%d%m%y%H%M%S")
    return current

# Function to copy image to local directory
def copy_image():
		try:
				process = subprocess.run('curl http://devops.witdemo.net/image.jpg > test.jpg', shell=True, stdout=subprocess.PIPE)
		except Exception as error:
				print (error)
		object_name = 'test.jpg'
		return object_name


ec2 = boto3.resource('ec2')
s3 = boto3.resource("s3")


instance = ec2.create_instances(
    ImageId='ami-0713f98de93617bb4',
    KeyName='kon_keypair',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.nano',
	TagSpecifications=[
		{
			'ResourceType': 'instance',

		    'Tags': [
			    {
			        'Key': 'Killian O\'Neachtain',
			        'Value': 'Assignment 1'
			    },
			]
		},
	],
    SecurityGroupIds=['sg-0b197ada8975ee0c9'])

print ("The instance ID is : " + instance[0].id)

instanceID = instance[0].id

instance = ec2.Instance(instanceID)

print ("Waiting for Instance to begin 'running'. \nPlease Allow 30 seconds.")
instance.wait_until_running(
		Filters=[
			{
				'Name': 'instance-id', 
				'Values': [ instanceID ]
 			}
		],
		DryRun=False,		
)

print ("\nInstance Status : RUNNING")

keyName = instance.key_name
instanceIP = instance.public_ip_address

#------- Status Checking Routine -----------
# We will not proceed to SSH into the instance until the Status Checks
# are complete and both have been passed.
#-----------------------------------------

print ("\n\n Waiting for AWS Status Checks to Pass...\n\n")

status_check_cmd = 'aws ec2 describe-instance-status --instance-id %s | egrep \'ok|passed\' | wc -l' % (instanceID)

checkCount = ""

while checkCount != "b\'4\\n\'" :
		try:
				process = subprocess.run(status_check_cmd, shell=True, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
				output = str(process.stdout)
				if output == "b\'4\\n\'":
					print ("\n2/2 AWS Checks Have Passed.\n\n")
					break
		except Exception as error:
				print (error)		


#------- Create S3 Bucket with an image -----
# Unblock all the permissions and allow image to be referenced in EC2 instance web site
#-----------------

bucket_name = 'killian'+ get_datetime()
print ("\nThe bucket_name is : " + bucket_name +"\n")
object_name = copy_image()


# create bucket here
try:
		response = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'}, ACL='public-read-write')
except Exception as error:
		print (error)

time.sleep(18)
print("\nWaiting for the S3 Bucket to be set up. \nPlease allow 15 seconds.\n")


# put image in the bucket here

try:
    	response = s3.Object(bucket_name, object_name).put(ACL='public-read', Body=open(object_name, 'rb'))
    	print (response)
except Exception as error:
    	print (error)

location = boto3.client('s3').get_bucket_location(Bucket=bucket_name)['LocationConstraint']

url = "https://%s.s3-%s.amazonaws.com/%s" % (bucket_name,location, object_name)

	
#------- SSH Routine -----------
# We proceed to SSH into the instance and perform update commands
# as a root(SUDO) user. We exit on completion.
#-----------------------------------------

print ("Applying update and install commands via SSH...")


ssh_command = 'ssh -o StrictHostKeyChecking=no -i %s.pem ec2-user@%s \'sudo ' % (keyName, instanceIP)

image_code = "echo \"<img src=" + url + ">\" >> /var/www/html/index.html'"

cmdList = ["yum update -y'", "yum install httpd -y'", "systemctl enable httpd'", "systemctl start httpd'", "chmod o+w /var/www/html'", "echo \"<h2>Test page</h2>Instance ID: \" > /var/www/html/index.html'", "curl --silent http://169.254.169.254/latest/meta-data/instance-id/ >> /var/www/html/index.html'", "echo \"<br>Availability zone: \" >> /var/www/html/index.html'", "curl --silent http://169.254.169.254/latest/meta-data/placement/availability-zone/ >> /var/www/html/index.html'", "echo \"<br>IP address: \" >> /var/www/html/index.html'", "curl --silent http://169.254.169.254/latest/meta-data/public-ipv4 >> /var/www/html/index.html'", "echo \"<hr>Here is an image that I have stored on S3: <br>\" >> /var/www/html/index.html'", image_code]

for index in range(len(cmdList)):
		try:	
				print ("\nSubprocess is : " + ssh_command + cmdList[index] )
				subprocess.run(ssh_command + cmdList[index] , shell=True, stdout=subprocess.PIPE)
				print ("\n" + cmdList[index] + "\nCompleted!")
		except Exception as error:
				print (error)



url = 'http://' + instanceIP
subprocess.call('firefox '+ url, shell=True)
#subprocess.call('firefox '+url, shell=True)

os.remove("test.jpg")







	












