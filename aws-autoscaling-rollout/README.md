# AWS Autoscaling Rollout

This script does a rollout of an autoscaling group gradually, while waiting/checking
that whatever Elastic Load Balancer (ELB) it is attached to is healthy before
continuing (if attached).  This applies to both Classic ELBs (CLB) and Application Load Balancers (ALBs).

This script heavily leverages boto3, you will likely need to install boto3.  **NOTE:** Same as the AWS cli utilities, there is no option to set the AWS region or credentials in this script.  Boto automatically reads from typical AWS environment variables/profiles so to set the region/profile/credentials please use the typical aws cli methods to do so.  Eg:

```AWS_DEFAULT_PROFILE=client_name AWS_DEFAULT_REGION=us-east-1 aws-autoscaling-rollout.py -a autoscalername```

**WARNING:** This script does NOT work (yet) for doing rollouts of autoscaled groups that are
         attached to ALBs that are used in an ECS cluster.  That's a WHOLE other beast,
         that I would love for this script to handle one day... but alas, it does not yet.
         If you try to use this script against an autoscaler that is used in an ECS cluster
         it will have unexpected and most likely undesired results.  So be warned!!!!!!!

Pieces of logic in this script are loosely based on (but intended to replace) the
now abandoned "aws-ha-release" tool from Colin Johnson - colinbjohnson

https://github.com/colinbjohnson/aws-missing-tools/tree/master/aws-ha-release

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

## Directions For Use:
```
aws-autoscaling-rollout.py -a autoscaler_name
```

## Potential Use:
Once an autoscaler has been changed to a new launch configuration (eg via Terraform) this script helps perform a "rolling" deploy of that autoscaling group, one by one starting up a new instance, waiting for it to get health, and then shutting down an old one.  When this script is done running, all the instances that were in the autoscaling group will have been terminated and replaced with all new instances of whatever launch configuration is set for the autoscaling group.


## Todo:
* Implement a max-timeout feature, so you know when this script fails
* Implement a check-interval feature, and use it script-wide to know how often to re-check on the status of things
* Support instances that are hosting ECS containers that are attached to an ALB
* Implement the old (Farley/internal) deploy-servers sexy-CLI output so people are in awe
  * Move all the "debug" output to a --verbose argument to clean the output up


## Additional Information:
- Author(s): Farley farley@neonsurge.com
- First Published: 24-06-2016
- Last Updated: 11-06-2017
- Version 1.0.0
- License Type: MIT
