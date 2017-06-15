# Farley's AWS Missing Tools
Random tools and helpers I've written that come in handy that are generally missing in the Amazon CLI Tools.  These tools all extend/expand on the Amazon AWS CLI tools which must be installed for any of these to work.

*NOTE*: This repository is a constant work in progress, I am slowly migrating all my personal code into Python and open-sourcing it because of numerous requests/demands for this.  Feel free to watch this repo for updates as all the tools come in.

# aws-choose-profile
A bash/fish script that scans for profiles defined in ~/.aws/credentials and in ~/.aws/config and asks you to choose one of them, and then sets the AWS_PROFILE and AWS_DEFAULT_PROFILE environment variables for you from the chosen profile.  Great for sysadmins/devs that manage more than one AWS account via command-line based tools.

# ec2-metadata
A amazon-written helper that should really be automatically installed on every instance automatically IMHO to query the metadata.  It is easy enough to do on your own via curl, but it comes in handy to have a helper as well.

# aws-push-cloudwatch-instance-metrics
This helper, intended to be run from cron every minute, pushes memory and disk usage to cloudwatch.  If this server is part of an autoscaling group, it also pushes against that dimension (within the EC2 namespace) to be able to query the autoscaler's combined memory & disk usage.

# aws-autoscaling-rollout
Performs a gradual rollout of servers in an autoscaling group, although currently very simplified and hacked together, this is a placeholder for the "final" version that I have yet to migrate to Python (from shitty PHP) and open source.  I will do this soon, I promise!  People will proabably say that this is loosely based on the "aws-ha-release" tool from colinbjohnson, although the original took I wrote back in 2009 and has been pending open-sourcing forever

# cleanup-packer-aws-resources
This performs a cleanup of packer resources.  Sometimes packer dies, horribly, and leaves instances and/or keys and/or security groups laying around.  This script goes through every region and cleans them up (after they are 24 hours old)

## Contributing
Feel free to contribute a tool you wrote that is missing in AWS via a pull request, or fix a bug in one of mine!
