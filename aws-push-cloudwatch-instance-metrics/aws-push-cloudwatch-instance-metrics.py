#!/usr/bin/env python
'''
Send memory usage metrics to Amazon CloudWatch

This is intended to run on an Amazon EC2 instance and requires an IAM
role allowing to write CloudWatch metrics. Alternatively, you can create
a boto credentials file and rely on it instead.

Original idea based on https://github.com/colinbjohnson/aws-missing-tools
modified to detect if we are under an autoscaler and then send those metrics 
to the autoscaler also

Current incarnation by: Farley <farley@neonsurge.com>
'''

import sys
import re
import datetime
import subprocess
import boto3
from pprint import pprint

def get_region():
    import urllib2   
    try:
        region = urllib2.urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone').read() 
        return region[0:-1]
    except:
        return False



def get_instance_id():
    import urllib2
    try:
        instance_id = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()
        return instance_id
    except:
        return False
           

def collect_memory_usage():
    meminfo = {}
    pattern = re.compile('([\w\(\)]+):\s*(\d+)(:?\s*(\w+))?')
    with open('/proc/meminfo') as f:
        for line in f:
            match = pattern.match(line)
            if match:
                # For now we don't care about units (match.group(3))
                meminfo[match.group(1)] = float(match.group(2))
    return meminfo


def get_root_disk_usage_percentage():
    df = subprocess.Popen(["df", "/"], stdout=subprocess.PIPE)
    output = df.communicate()[0]
    device, size, used, available, percent, mountpoint = output.split("\n")[1].split()
    return percent[0:-1]



region = get_region()
cloudwatch = boto3.client('cloudwatch', region_name=region)


def send_cloud_metrics_against_instance_and_autoscaler(instance_id, region, metrics, namespace="EC2", unit='Percent'):
    '''
    Send EC2 metrics to CloudWatch
    metrics is expected to be a map of key -> value pairs of metrics
    '''
    
    # First push all our metrics against our instance id dimension
    for key, metric in metrics.iteritems():
        # print(" key " + key + " metric " + str(metric))
        cloudwatch.put_metric_data(
            Namespace=namespace, 
            MetricData=[
                {
                    'MetricName': key,
                    'Dimensions': [{
                        'Name': 'InstanceId',
                        'Value': instance_id
                    }],
                    'Timestamp': datetime.datetime.now(),
                    'Value': float(metric),
                    'Unit': unit
                }
            ]
        )
          
    autoscaling = boto3.client('autoscaling', region_name=region)
    autoscalers = autoscaling.describe_auto_scaling_instances(
        InstanceIds= [
            instance_id
        ])['AutoScalingInstances']
    for autoscaler in autoscalers:
        for key, metric in metrics.iteritems():
            # print(" key " + key + " metric " + str(metric))
            cloudwatch.put_metric_data(
                Namespace=namespace, 
                MetricData=[
                    {
                        'MetricName': key,
                        'Dimensions': [{
                            'Name': 'AutoScalingGroupName',
                            'Value': autoscaler['AutoScalingGroupName']
                        }],
                        'Timestamp': datetime.datetime.now(),
                        'Value': float(metric),
                        'Unit': unit
                    }
                ]
            )

if __name__ == '__main__':
    instance_id = get_instance_id()
    mem_usage = collect_memory_usage()
    mem_free = mem_usage['MemFree'] + mem_usage['Buffers'] + mem_usage['Cached']
    mem_used = mem_usage['MemTotal'] - mem_free
    if mem_usage['SwapTotal'] != 0 :
        swap_used = mem_usage['SwapTotal'] - mem_usage['SwapFree'] - mem_usage['SwapCached']
        swap_percent = swap_used / mem_usage['SwapTotal'] * 100
    else:
        swap_percent = 0
    disk_usage = get_root_disk_usage_percentage()
    
    metrics = {'MemUsage': mem_used / mem_usage['MemTotal'] * 100,
               'SwapUsage': swap_percent,
               'DiskUsage': disk_usage }

    result = send_cloud_metrics_against_instance_and_autoscaler(instance_id, region, metrics)

    print str(datetime.datetime.now()) + ": sent metrics (" + instance_id + ": " + str(metrics) + ") to CloudWatch"
