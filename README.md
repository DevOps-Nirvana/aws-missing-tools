# Farley's AWS Missing Tools
Random tools and helpers I've written that come in handy that are generally missing in the Amazon CLI Tools.  These tools all extend/expand on the Amazon AWS CLI tools which must be installed for any of these to work.

# aws-choose-profile
A bash script that scans for profiles defined in ~/.aws/credentials and in ~/.aws/config and asks you to choose one of them, and then sets the AWS_PROFILE and AWS_DEFAULT_PROFILE environment variables for you from the chosen profile.  Great for sysadmins/devs that manage more than one AWS account via command-line based tools.

# ec2-metadata
A amazon-written helper that should really be automatically installed on every instance automatically IMHO to query the metadata.  It is easy enough to do on your own via curl, but it comes in handy to have a helper as well.

# aws-push-cloudwatch-instance-metrics
This helper, intended to be run from cron every minute, pushes memory and disk usage to cloudwatch.  If this server is part of an autoscaling group, it also pushes against that dimension (within the EC2 namespace) to be able to query the autoscaler's combined memory & disk usage.

## Contributing
Feel free to contribute a tool you wrote that is missing in AWS via a pull request, or fix a bug in one of mine!
