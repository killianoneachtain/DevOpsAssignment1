#!/usr/bin/env python3
import boto3
import botocore
import subprocess

ec2 = boto3.resource('ec2')
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
		
#------- SSH Routine -----------
# We proceed to SSH into the instance and perform update commands
# as a root(SUDO) user. We exit on completion.
#-----------------------------------------

print ("Applying update and install commands via SSH...")


ssh_command = 'ssh -o StrictHostKeyChecking=no -i %s.pem ec2-user@%s \'sudo ' % (keyName, instanceIP)

cmdList = ["yum update -y'", "yum install httpd -y'", "systemctl enable httpd'", "systemctl start httpd'", "chmod  o+w /var/www/html'", "echo \"<h2>Test page</h2>Instance ID: \" > /var/www/html/index.html'", "curl --silent http://169.254.169.254/latest/meta-data/instance-id/ >> /var/www/html/index.html'", "echo \"<br>Availability zone: \" >> /var/www/html/index.html'", "curl --silent http://169.254.169.254/latest/meta-data/placement/availability-zone/ >> /var/www/html/index.html'", "echo \"<br>IP address: \" >> /var/www/html/index.html'", "curl --silent http://169.254.169.254/latest/meta-data/public-ipv4 >> /var/www/html/index.html'"]

for index in range(len(cmdList)):
		try:	
				print ("\nSubprocess is : " + ssh_command + cmdList[index] )
				subprocess.run(ssh_command + cmdList[index] , shell=True, stdout=subprocess.PIPE)
				print ("\n" + cmdList[index] + "\nCompleted!")
		except Exception as error:
				print (error)


url = 'http://' + instanceIP

#subprocess.call('firefox '+ url, shell=True)
subprocess.call('firefox '+url, shell=True)



	












