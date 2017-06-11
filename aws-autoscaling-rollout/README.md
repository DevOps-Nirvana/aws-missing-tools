# AWS Autoscaling Rollout

## Introduction:
aws-autoscaling-rollout allows the high-availability / no downtime replacement of all EC2 Instances in an Auto Scaling Group (that can be attached to an Elastic Load Balancer).  It does this in a "rolling" fashion, one server at a time.  This script supports BOTH Application Load Balancers (ALB) and the "Classic" Load Balancers (CLB) from Amazon, but does **NOT currently support ECS**.

## Potential Use:
Some potential uses for aws-autoscaling-rollout are listed below:

1. Delivery of new code or application logic, typically an autoscaler will be changed to launch a new launch configuration (eg: terraform).  Utilization of this script will cause the termination of EC2 instances in order to release new code in a High-Availability fashion without incurring any downtime.
1. To rotate and refresh your instances to a fresh/vanilla state, all older EC2 instances can be replaced with newer EC2 instances.  This can help reset your instances incase logs or temporary files have filled up your instance, or your application has consumed all available RAM/Disk resources.

## Directions For Use:
`AWS_DEFAULT_REGION=us-east-1 aws-autoscaling-rollout -a my-scaling-group`



## Simplified Logic Walkthrough:

1. _(pre-logic)_ Check if this autoscaler name is valid
1. _(pre-logic)_ (if not --force) Check that this autoscaler has no bad suspended processes
1. _(pre-logic)_ Wait for the autoscaler to "settle" (in-case it's mid-scaling activity)
1. _(pre-logic)_ (if not --force) Check that every instance of the autoscaler is healthy on whatever CLB/ALBs its associated with
1. _(pre-logic)_ Suspend various autoscaling processes so things like alarms or scheduled actions won't interrupt this deployment
1. _(pre-logic)_ (if the desired capacity == max capacity) Scale up the max capacity by one
1. _(main-loop)_ Wait for the number of servers on the autoscaler to equal the number of healthy servers on the CLB/ALBs
1. _(main-loop)_ Scale up the desired capacity by one, and wait for the autoscaler to show the new server as healthy (in the autoscaler)
1. _(main-loop)_ (if not --skip-elb-health-check) Wait for the new server to get healthy in all attached CLB/TGs
1. _(main-loop)_ (if --check-if-new-server-is-up-command ) Run the specified command every 10 seconds until it returns retval of 0
1. _(main-loop)_ Detach one of the old instances from all attached CLB/TGs
1. _(main-loop)_ Wait for the old instance to fully detach from all attached CLB/TGs (waits for connection draining and autoscaling detachment hooks)
1. _(main-loop)_ (if --run-before-server-going-down-command) Run the specified command before terminating, it must return a retval of 0
1. _(main-loop)_ (if --wait-for-seconds) Wait for --wait-for-seconds number of seconds before continuing
1. _(main-loop)_ Terminate the old instance
1. _(main-loop)_ (if --run-after-server-going-down-command) Run the specified command after terminating, it must return a retval of 0
1. _(main-loop)_ Jump to the start of the main loop and repeat until all old instances are replaced
1. _(cleanup)_ (if we changed the max capacity above) Shrink the max capacity by one
1. _(cleanup)_ Un-suspend the suspended autoscaling processes
1. **Profit / Success!**



## Script options:

There are various options you can pass to aws-autoscaling-rollout to tweak its logic slightly to fit your deployment pattern, use-case, etc.  These have all been added based on various environments' needs to support their use-cases.  If there's a use-case that isn't handed in an option, perhaps submit a Github bug/feature request and I'll add it.  Or implement it yourself, and get me a Pull Request.  The current options are...

### --force
  If specified, then we want to force this deployment by skipping health pre-checks, and will ignore and reset currently suspended processes.  NOTE: This will NOT skip the external health check commands or wait for seconds options if you specify them.  This is to help deploy against
  a environment which is currently unhealthy, down, or is having issues (eg: a few servers are unhealthy in an ELB but a few are healthy, you want to just push this rotation through to try to
  move things ahead).

### --skip-elb-health-check
  If specified this script will skip the ELB health check of new instances as they come up (often used with --force.  Force above merely skips checking the CURRENT instances, not newly scaled up instances.  Warning: with --force and this option specified, your environment may go down, thus it won't be as "HA" as you might like.  This can be useful to deploy to a development environment
  which may not be very stable in nature.

### --wait-for-seconds
  The number of extra seconds to wait in-between instance terminations (0 by default to disable).  This can be helpful if your instances need some time to cache or be "more" healthy after being marked healthy in a ELB.  Note: --force does NOT override this.

### --check-if-new-server-is-up-command
  This allows you to specify a custom one-liner shell command which can do an external health check against your newly created instance to verify a new instance is healthy before continuing deployment.  This should be a valid 'shell' command that can run on this server, it can include pipes to be able to run multiple commands.  This command supports _simple_ templating in the form of string replacing NEW_INSTANCE_ID, NEW_INSTANCE_PRIVATE_IP_ADDRESS, NEW_INSTANCE_PUBLIC_IP_ADDRESS.  Often used to do custom health checks when an autoscaler is not attached to an ELB, or to check that a new server joined a cluster properly before continuing (eg: Zookeeper, Kafka, Consul, etc).  This feature could also be used to add ECS support with a little creativity.  When this command returns a retval of 0 then the deployment continues

### --run-before-server-going-down-command
  This allows you to run an external command right before a server goes down, this is run BEFORE the wait-for-seconds (if provided).  This should be a valid 'shell' command that can run on this server.  This command supports _simple_ templating in the form of string replacing OLD_INSTANCE_ID, OLD_INSTANCE_PRIVATE_IP_ADDRESS, OLD_INSTANCE_PUBLIC_IP_ADDRESS.  Often used to do stuff like pull a server out of a cluster (eg: to force-leave a cluster, or to remove from a monitoring system).  This feature could also be used to add ECS support with a little creativity.  This command MUST return a retval of 0 otherwise this deployment will halt

### --run-after-server-going-down-command
  This is an external command that will run after the server gets sent the terminate command.  **WARNING**: Due to possible delays in Amazon's API and other factors it is not guaranteed that the server will be completely down when this command is run.  This should be a valid 'shell' command that can run on this server.  This command supports _simple_ templating in the form of string replacing OLD_INSTANCE_ID, OLD_INSTANCE_PRIVATE_IP_ADDRESS, OLD_INSTANCE_PUBLIC_IP_ADDRESS.  Often used to do stuff like pull a server out of a custom monitoring system (eg: Zabbix/Nagios).  This command MUST return a retval of 0 otherwise this deployment will hal


## Detailed Description:
This script does a rollout of an autoscaling group gradually, while waiting/checking
that whatever Elastic Load Balancer (ELB) it is attached to is healthy before
continuing (if attached).  This applies to both Classic ELBs (CLB) and Application Load Balancers (ALBs).

This script is written in python and requires a python interpreter, and it heavily leverages boto3, you will likely need to install boto3 with `pip install boto3`.  **NOTE:** Same as the AWS cli utilities, there is no option to set the AWS region or credentials in this script.  Boto automatically reads from typical AWS environment variables/profiles so to set the region/profile/credentials please use the typical aws cli methods to do so.  Eg:

```
AWS_DEFAULT_PROFILE=client_name AWS_DEFAULT_REGION=us-east-1 aws-autoscaling-rollout.py -a autoscalername
```

**WARNING:** This script does NOT work (yet) for doing rollouts of autoscaled groups that are
         attached to ALBs that are used in an ECS cluster.  That's a WHOLE other beast,
         that I would love for this script to handle one day... but alas, it does not yet.
         If you try to use this script against an autoscaler that is used in an ECS cluster
         it will have unexpected and most likely undesired results.  So be warned!!!!!!!

Pieces of logic in this script are loosely based on (but intended to replace) the
now abandoned ["aws-ha-release"](https://github.com/colinbjohnson/aws-missing-tools/tree/master/aws-ha-release) tool from Colin Johnson

This tool is also based on AWS deployment code pieces from numerous deployments scripts in
bits and pieces I have written over the years, refactored/improved to add ALB support and unify
the logic into a single rollout script.

## Installation:
I recommend you symlink this into your user or system bin folder

### Installation Examples:

Symlink into place, so you can "git pull" from where you cloned this to update this command from time to time
```
ln -s $(pwd)/aws-autoscaling-rollout.py /usr/local/bin/
```
or install as a super-user into your /usr/local/bin folder, depending on your preference
```
sudo cp -a aws-autoscaling-rollout.py /usr/local/bin/
```

## Todo:
* Implement a max-timeout feature, so you know when this script fails
* Implement a check-interval feature, and use it script-wide to know how often to re-check on the status of things
* Support instances that are hosting ECS containers that are attached to an ALB
* Implement the old (Farley/internal) deploy-servers sexy-CLI output so people are in awe
  * Move all the "debug" output to a --verbose argument to clean the output up


## Additional Information:
- Author(s): Farley farley@neonsurge.com / farley@olindata.com
- First Published: 24-06-2016
- Last Updated: 11-06-2017
- Version 1.0.0
- License Type: MIT
