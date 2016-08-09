#!/usr/bin/env python
#
###############################################################################
#
#  cleanup-packer-aws-resources.py    Written by Farley <farley@neonsurge.com>
#
# Packer when used on an AWS account from tools like Jenkins or Rundeck, often
# leaves reminants of its existance such as  instances running, security groups, 
# and SSH keys.  This script scans all regions of AWS for leftover packer 
# resources and removes them.
#
# This script can be run on the command-line standalone or ideally put into packer
# and run via cloudwatch scheduled events like once a day or so
#
# This is from Farley's AWS missing tools
#    https://github.com/AndrewFarley/farley-aws-missing-tools/
#
###############################################################################
#
from __future__ import print_function

# For AWS
import boto3
# For pretty-print
from pprint import pprint
from datetime import datetime
import calendar

# The maximum age (in seconds) of a packer instance before we terminate it
# 86400 == 1 day
# 21600 == 6 hours
# 10800 == 3 hours
#  3600 == 1 hour
max_age = 21600

# Whether or not to output debug info as it does things
debug = False

# Our AWS regions, we'll call the AWS API to get the list of regions, so this is always up to date
ec2 = boto3.client('ec2', region_name='us-west-1')
regions = []
awsregions = ec2.describe_regions()['Regions']
for region in awsregions:
    regions.append(region['RegionName']) 
del ec2, awsregions

# Helper to convert datetime with TZ to Unix time
def dt2ts(dt):
    return calendar.timegm(dt.utctimetuple())

# Helper to convert seconds to a sexy format "x hours, x minutes, x seconds" etc
def display_time(seconds, granularity=2):
    intervals = (
        ('months', 18144000), # 60 * 60 * 24 * 7 * 30 (roughly)
        ('weeks', 604800),    # 60 * 60 * 24 * 7
        ('days', 86400),      # 60 * 60 * 24
        ('hours', 3600),      # 60 * 60
        ('minutes', 60),
        ('seconds', 1),
        )
    
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

# Get instances from AWS from all regions that...
#    #1: Are currently running
#    #2: Have the name "Packer Builder"
#    #3: 
def get_zombie_packer_instances(regions, maximum_age):
    global debug
    output = {}
    
    # Get our "now" timestamp for knowing how long ago instances were launched
    utc_now = datetime.now()
    utc_now_ts  = int(utc_now.strftime("%s"))

    for region in regions:
        regionoutput = []
        if debug is True:
            print("Scanning region " + region + " for instances")

        # Create our EC2 Handler
        ec2 = boto3.client('ec2', region_name=region)

        response = ec2.describe_instances(
            MaxResults=1000
        )

        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                
                if debug is True:
                    print("Found instance: " + instance['InstanceId'])
                if instance['State']['Name'] == "running":
                    if debug is True:
                        print("  Instance is currently running")
                else:
                    if debug is True:
                        print("  Instance is not currently running, skipping...")
                    continue
                
                packerNameTagMatched = False
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name' and tag['Value'] == 'Packer Builder':
                            if debug is True:
                                print("  Instance is a packer builder")
                            packerNameTagMatched = True
                            break
                        elif tag['Key'] == 'Name':
                            if debug is True:
                                print("  Instance is NOT a packer building, skipping...")
                            break
                
                if packerNameTagMatched is False:
                    continue
                    
                if debug is True:
                    print("    Found packer instance: " + instance['InstanceId'])
                launched_at = dt2ts(instance['LaunchTime'])
                if debug is True:
                    print("    Instance started " + display_time(utc_now_ts - launched_at) + " ago ")
                # if (utc_now_ts - launched_at) > 86400:
                if (utc_now_ts - launched_at) > maximum_age:
                    if debug is True:
                        print("    Instance started more than a day ago, should be marked for termination")
                    regionoutput.append({
                        "region": region, 
                        "instance_id": instance['InstanceId'],
                        "keyname": instance['KeyName'],
                        "security_groups": instance['SecurityGroups']
                    })
                else:
                    if debug is True:
                        print("    Instance is too new to be terminated")                    
                    
        output[region] = regionoutput
    return output

def get_zombie_packer_keys(regions):
    global debug
    output = {}
    for region in regions:
        regionoutput = []
        if debug is True:
            print("Scanning region " + region + " for keys")

        # Create our EC2 Handler
        ec2 = boto3.client('ec2', region_name=region)

        response = ec2.describe_key_pairs(
            Filters=[
                {
                    'Name': 'key-name',
                    'Values': ['packer *'],
                },
            ]
        )
        
        for pair in response['KeyPairs']:
            regionoutput.append(pair['KeyName'])
        
        output[region] = regionoutput
    return output
    
    
def get_zombie_packer_security_groups(regions):
    global debug
    output = {}
    for region in regions:
        regionoutput = []
        if debug is True:
            print("Scanning region " + region + " for security groups")

        # Create our EC2 Handler
        ec2 = boto3.client('ec2', region_name=region)

        response = ec2.describe_security_groups(
            Filters=[
                {
                    'Name': 'group-name',
                    'Values': ['packer *'],
                },
            ]
        )
            
        # NOTE:
        # Checking for stales doesn't seem to work, so we'll just try to delete without checking stale
        # # Get our VPCs
        # vpcs = ec2.describe_vpcs()['Vpcs']
        # # Get all stale sgs in every vpc
        # for vpc in vpcs:
        #     stale = ec2.describe_stale_security_groups(VpcId=vpc['VpcId'])['StaleSecurityGroupSet']
        #     pprint(stale)
            
        
        for pair in response['SecurityGroups']:
            regionoutput.append(pair['GroupName'])
        
        #if len(regionoutput) > 0:
        #    stalegroups = ec2.describe_security_groups
        #    for groupname in regionoutput:
                
        output[region] = regionoutput
    return output

def lambda_handler(event, context):
    global regions, max_age
    
    print("Scanning " + str(len(regions)) + " AWS regions for zombie packer instances...")

    zombies = get_zombie_packer_instances(regions, max_age)
    for region,instances in zombies.iteritems():
        if len(instances) == 0:
            print("Found NO zombie instances in " + region + ", skipping...")
            continue

        print("Found " + str(len(instances)) + " zombie packer instances in " + region + ", now terminating...")
        ec2 = boto3.client('ec2', region_name=region)
    
        instance_ids = []
        for instance in instances:
            instance_ids.append(instance['instance_id'])
    
        try:
            response = ec2.terminate_instances(
                InstanceIds=instance_ids
            )
            print("Successfully terminated instances")
        except:
            print("ERROR: Unable to terminate some or all resources")
    
    print("Scanning " + str(len(regions)) + " AWS regions for zombie packer keys...")
    
    zombies = get_zombie_packer_keys(regions)
    for region,keynames in zombies.iteritems():
        if len(keynames) == 0:
            print("Found NO zombie keys in " + region + ", skipping...")
            continue
    
        print("Found " + str(len(keynames)) + " zombie packer keys in " + region + ", now deleting...")
        ec2 = boto3.client('ec2', region_name=region)
    
        for keyname in keynames:
            try:
                print("Deleting key " + keyname)
                response = ec2.delete_key_pair(
                    KeyName=keyname
                )
                print("Deleted")
            except:
                print("Error while trying to terminate resources")


    print("Scanning " + str(len(regions)) + " AWS regions for zombie packer security groups...")

    zombies = get_zombie_packer_security_groups(regions)
    for region,security_groups in zombies.iteritems():
        if len(security_groups) == 0:
            print("Found NO zombie security groups in " + region + ", skipping...")
            continue
    
        print("Found " + str(len(security_groups)) + " zombie security groups in " + region + ", now terminating...")
        ec2 = boto3.client('ec2', region_name=region)
    
        for security_group in security_groups:
            try:
                print("Deleting security group " + security_group)
                response = ec2.delete_security_group(
                    GroupName=security_group
                )
                print("Deleted")
            except:
                print("Error while trying to terminate resources")



    # TODO: Delete all the packer security groups?

# NOTE: REMOVE THIS BELOW FOR RUNNING ON LAMBDA otherwise spinning this lambda
#       up will already run its main logic.  Which is okay, but not really intended
#       If anyone knows how to detect running on Lambda please add this feature!  :P
lambda_handler({}, "test")
