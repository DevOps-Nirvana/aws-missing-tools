#!/usr/bin/env python
##########################################################################################
#
# This script does a rollout, very simplified, this is a placeholder for the "final" version
# that I have yet to migrate to Python and open source.  I will do this soon, I promise!
#
# Loosely based on and inspired by the "aws-ha-release" tool from Colin Johnson - colinbjohnson
# https://github.com/colinbjohnson/aws-missing-tools/tree/master/aws-ha-release 
#
# Written by Farley <farley@neonsurge.com>
#
##########################################################################################

# Libraries 
import time
import boto3
from pprint import pprint
from optparse import OptionParser

# Instances of libraries 
elb = boto3.client('elb')
autoscaling = boto3.client('autoscaling')
ec2 = boto3.client('ec2')

# Usage and CLI opts handling
usage = "usage: %prog -a autoscaler"
parser = OptionParser(usage=usage)
parser.add_option("-a", "--autoscaler",
                  dest="autoscaler",
                  default="",
                  help="Autoscaler to rollout",
                  metavar="lb-name")
(options, args) = parser.parse_args()

# Libraries/helpers, pulled from my python_aws_helpers.py

# Get a autoscaling group
def get_autoscaling_group( autoscaling_group_name ):
    try:
        fetched_data = autoscaling.describe_auto_scaling_groups(
            AutoScalingGroupNames=[
                autoscaling_group_name,
            ],
            MaxRecords=1
        )

        if len(fetched_data['AutoScalingGroups']) > 0:
            # print "DEBUG: '" + autoscaling_group_name + "' seems to be a valid autoscaling group..."
            return fetched_data['AutoScalingGroups'][0]
    except:
        ignoreme=1
    # print "DEBUG: '" + autoscaling_group_name + "' is NOT a valid autoscaling group"
    return False

# Get the number of healthy instances from the autoscaling group definition
def get_number_of_autoscaler_healthy_instances( autoscaler_description ):
    return len(get_autoscaler_healthy_instances( autoscaler_description ))

# Get the healthy instances from the autoscaling group definition or name
def get_autoscaler_healthy_instances( autoscaling_group_name_or_definition ):
    if type(autoscaling_group_name_or_definition) is str:
        autoscaler_description = get_autoscaling_group( autoscaling_group_name_or_definition )
    else:
        autoscaler_description = autoscaling_group_name_or_definition

    healthy_instances = []
    for instance in autoscaler_description['Instances']:
        if instance['HealthStatus'] == 'Healthy':
            healthy_instances.append(instance)
    return healthy_instances

# Check if an autoscaler is currently performing a scaling activity
def check_if_autoscaler_is_scaling( autoscaling_group_name ):
    # print "DEBUG: Checking if autoscaler is scaling: " + autoscaling_group_name

    # Get the autoscaling group
    autoscaler = autoscaling.describe_auto_scaling_groups(
        AutoScalingGroupNames=[
            autoscaling_group_name,
        ],
        MaxRecords=1
    )

    # Quick error checking
    if len(autoscaler['AutoScalingGroups']) != 1:
        print "ERROR: Unable to get describe autoscaling group: " + autoscaling_group_name
        exit(1)
    autoscaler = autoscaler['AutoScalingGroups'][0]

    # print "DEBUG: Got data"
    # pprint(autoscaler)

    # Check if our healthy instance count matches our desired capacity
    healthy_instance_count = get_number_of_autoscaler_healthy_instances( autoscaler )
    # print "DEBUG: Healthy instances " + str(healthy_instance_count)
    if healthy_instance_count != autoscaler['DesiredCapacity']:
        print "INFO: Our autoscaler must be scaling, desired " + str(autoscaler['DesiredCapacity']) + ", healthy instances " + str(healthy_instance_count)
        return True

    # Also check our last auto-scaling history item
    autoscaling_activities = autoscaling.describe_scaling_activities(
        AutoScalingGroupName=autoscaling_group_name,
        MaxRecords=1,
    )
    autoscaling_activities = autoscaling_activities['Activities']
    for activity in autoscaling_activities:
        # print "DEBUG: Status " + activity['StatusCode'];
        if activity['StatusCode'] == 'Successful' or activity['StatusCode'] == 'Cancelled':
            # print "DEBUG: Activity is successful or cancelled"
            ignoreme=1
        else:
            print "INFO: Our autoscaler is currently scaling or having problems, the last activity status code is " + activity['StatusCode']
            return True

    return False

# Set desired capacity
def set_desired_capacity( autoscaling_group_name, desired_capacity ):
    print "DEBUG: Setting desired capacity of '" + autoscaling_group_name + "' to '" + str(desired_capacity) + "'..."
    response = autoscaling.set_desired_capacity(
        AutoScalingGroupName=autoscaling_group_name,
        DesiredCapacity=desired_capacity,
        HonorCooldown=False
    )

    # Check if this executed okay...
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print "DEBUG: Executed okay"
        return True
    else:
        print "ERROR: Unable to set_desired_capacity on '" + autoscaling_group_name + "'"
        exit(1)

# Startup simple checks...
if options.autoscaler is None:           
    print "ERROR: You MUST specify the autoscaler with -a"   
    parser.print_usage()
    exit(1)

# Verify/get our load balancer
print "Ensuring this is a valid autoscaler..."
result = get_autoscaling_group(options.autoscaler)
if result is False:
    print "ERROR: '" + options.autoscaler + "' is NOT a valid autoscaler, exiting..."
    parser.print_usage()
    exit(1)

print "Ensuring that we have the right number of instances..."
healthy_instance_count = int(get_number_of_autoscaler_healthy_instances( result ))
desired_capacity = int(result['DesiredCapacity'])
instance_count = desired_capacity

if desired_capacity != healthy_instance_count:
    print "WARNING: We have a potential mismatch we should sleep and wait for probably..."
    print "Desired capacity: " + str(healthy_instance_count)
    print "Number instances: " + str(desired_capacity)
elif check_if_autoscaler_is_scaling(options.autoscaler):
    print "WARNING: We are currently performing some autoscaling, we should wait..."
    

print "Performing rollout..."
while instance_count > 0:

    print "Increasing desired capacity by one from " + str(desired_capacity) + " to " + str(desired_capacity + 1)
    set_desired_capacity( options.autoscaler, desired_capacity + 1 )
    print "waiting for a second..."
    time.sleep(3)
    while True:
        if check_if_autoscaler_is_scaling(options.autoscaler):
            print "We are still scaling up, waiting another 10 seconds..."
            time.sleep(10)
        else:
            print "We're done with scaling up..."
            break

    print "Decreasing desired capacity by one from " + str(desired_capacity + 1) + " to " + str(desired_capacity)
    set_desired_capacity( options.autoscaler, desired_capacity )
    print "waiting for 15 seconds..."
    time.sleep(15)
        
    instance_count = instance_count - 1
    
exit(0)