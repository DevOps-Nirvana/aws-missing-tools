# Libraries
import boto3
import time
#from pprint import pprint

# Instances of libraries
elb = boto3.client('elb')
autoscaling = boto3.client('autoscaling')
ec2 = boto3.client('ec2')

######################
# Helpers
######################


# Get a load balancer
def get_load_balancer( loadbalancer_name ):
    try:
        fetched_data = elb.describe_load_balancers(
            LoadBalancerNames=[
                loadbalancer_name,
            ],
            PageSize=1
        )

        if len(fetched_data['LoadBalancerDescriptions']) > 0:
            # print "DEBUG: '" + loadbalancer_name + "' seems to be a valid load balancer..."
            return fetched_data['LoadBalancerDescriptions'][0]
    except:
        ignoreme=1
    # print "DEBUG: '" + loadbalancer_name + "' is NOT a valid load balancer"
    return False

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

# Get a autoscaling group
def get_all_autoscaling_groups( ):
    #try:
    fetched_data = autoscaling.describe_auto_scaling_groups(
        MaxRecords=100
    )

    if len(fetched_data['AutoScalingGroups']) > 0:
        # print "DEBUG: '" + autoscaling_group_name + "' seems to be a valid autoscaling group..."
        return fetched_data['AutoScalingGroups']
#    except:
#        ignoreme=1
    # print "DEBUG: '" + autoscaling_group_name + "' is NOT a valid autoscaling group"
    return False

# Gets the suspended processes for an autoscaling group (by name or predefined to save API calls)
def get_suspended_processes( autoscaling_group_name_or_definition ):
    if type(autoscaling_group_name_or_definition) is str:
        autoscaling_group = get_autoscaling_group( autoscaling_group_name_or_definition )
    else:
        autoscaling_group = autoscaling_group_name_or_definition

    output = []
    for item in autoscaling_group['SuspendedProcesses']:
        output.append(item['ProcessName'])

    return output

# Gets the suspended processes for an autoscaling group (by name or predefined to save API calls)
def suspend_processes( autoscaling_group_name, processes_to_suspend ):

    response = autoscaling.suspend_processes(
        AutoScalingGroupName=autoscaling_group_name,
        ScalingProcesses=processes_to_suspend
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        # print "DEBUG: Executed okay"
        return True
    else:
        print "ERROR: Unable to suspend_processes on '" + autoscaling_group_name + "'"
        return False

# Gets the suspended processes for an autoscaling group (by name or predefined to save API calls)
def resume_processes( autoscaling_group_name, processes_to_resume ):

    response = autoscaling.resume_processes(
        AutoScalingGroupName=autoscaling_group_name,
        ScalingProcesses=processes_to_resume
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        # print "DEBUG: Executed okay"
        return True
    else:
        print "ERROR: Unable to resume_processes on '" + autoscaling_group_name + "'"
        return False




def wait_for_no_scaling_activity( autoscaling_group_name ):
    while True:
        print "DEBUG: Checking if autoscaler '" + autoscaling_group_name + "' has scaling activity..."
        if check_if_autoscaler_is_scaling(autoscaling_group_name):
            # print "DEBUG: Autoscaler is currently scaling..."
            ignoreme=1
        else:
            # print "DEBUG: Autoscaler is NOT currently scaling..."
            return

        print "INFO: Waiting for 10 seconds to try again..."
        time.sleep(10)


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



def attach_load_balancer_to_autoscaling_group( autoscaling_group_name, loadbalancer_name ):
    print "DEBUG: Attach autoscaler '" + autoscaling_group_name + "' to the load balancer '" + loadbalancer_name + "'..."

    response = autoscaling.attach_load_balancers(
        AutoScalingGroupName=autoscaling_group_name,
        LoadBalancerNames=[
            loadbalancer_name,
        ]
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print "DEBUG: Executed okay"
        return True
    else:
        print "ERROR: Unable to attach autoscaler '" + autoscaling_group_name + "' to the load balancer '" + loadbalancer_name
        exit(1)



def detach_load_balancer_from_autoscaling_group( autoscaling_group_name, loadbalancer_name ):
    print "DEBUG: Attach autoscaler '" + autoscaling_group_name + "' to the load balancer '" + loadbalancer_name + "'..."

    response = autoscaling.detach_load_balancers(
        AutoScalingGroupName=autoscaling_group_name,
        LoadBalancerNames=[
            loadbalancer_name,
        ]
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print "DEBUG: Executed okay"
        return True
    else:
        print "ERROR: Unable to detach autoscaler '" + autoscaling_group_name + "' from the load balancer '" + loadbalancer_name
        exit(1)




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


def get_instance_ids_of_load_balancer( loadbalancer_name_or_definition ):
    if type(loadbalancer_name_or_definition) is str:
        loadbalancer = get_load_balancer( loadbalancer_name_or_definition )
    else:
        loadbalancer = loadbalancer_name_or_definition

    output = []
    for instance in loadbalancer['Instances']:
        output.append(instance['InstanceId'])
    return output


#def get_loadbalancer_instance_health( instances_array ):
#    temp = []
#    for instance in instances:
#        temp.append({})
#

def flatten_instance_health_array_from_loadbalancer( input_instance_array ):
    output = []
    for instance in input_instance_array:
        output.append(instance['InstanceId'])
    return output


def flatten_instance_health_array_from_loadbalancer_only_healthy( input_instance_array ):
    output = []
    for instance in input_instance_array:
        if instance['State'] == 'InService':
            output.append(instance['InstanceId'])

    return output




def wait_for_complete_loadbalancer_autoscaler_attachment( loadbalancer_name, autoscaling_group_name ):
    print "DEBUG: Waiting for lb/asg attachment of lb:" + loadbalancer_name + " to asg:" + autoscaling_group_name

    while True:
        # Get instances from load balancer
        print "DEBUG: Getting load balancer"
        loadbalancer = get_load_balancer(loadbalancer_name)

        # Get instance ids from load balancer
        print "DEBUG: Getting instance ids from load balancer"
        temptwo = get_instance_ids_of_load_balancer(loadbalancer)

        # Get their healths (on the ELB)
        print "DEBUG: Getting instance health on the load balancer"
        instance_health = elb.describe_instance_health(
            LoadBalancerName=loadbalancer_name,
            Instances=loadbalancer['Instances']
        )
        instance_health = instance_health['InstanceStates']
        # pprint(instance_health)

        # Put it into a flat array so we can check "in" it
        instance_health_flat = flatten_instance_health_array_from_loadbalancer_only_healthy(instance_health)
        # pprint(instance_health_flat)

        # Get our healthy instances from our autoscaler
        print "DEBUG: Getting healthy instances on our autoscaler"
        as_instances = get_autoscaler_healthy_instances( autoscaling_group_name )

        successes = 0
        for instance in as_instances:
            if instance['InstanceId'] in instance_health_flat:
                print "DEBUG: SUCCESS - Instance " + instance['InstanceId'] + " is healthy in our ELB"
                successes = successes + 1
            else:
                print "DEBUG: FAIL - Instance " + instance['InstanceId'] + " is unhealthy or not present in our ELB"

        # print "DEBUG: We need " + str(len(as_instances)) + " healthy instances and we have " + str(successes)

        if successes >= len(as_instances):
            print "DEBUG: We have at least " + str(successes) + " healthy instances on the elb from the new ASG..."
            break
        else:
            print "WAIT: Found " + str(successes) + " healthy instances on the elb from the ASG " + str(len(as_instances)) + " to continue.  Waiting 10 seconds..."

        time.sleep( 10 )



def get_autoscalers_on_loadbalancer( loadbalancer_name ):
    # Get all our autoscalers...
    output = []
    autoscalers = get_all_autoscaling_groups()
    for autoscaler in autoscalers:
        #print "Checking A "
        #print autoscaler
        for loadbalancer in autoscaler['LoadBalancerNames']:
            #print "Checking B "
            #print loadbalancer
            if loadbalancer == loadbalancer_name:
                output.append(autoscaler['AutoScalingGroupName'])
    return output
