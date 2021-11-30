# AWS Missing Tools
Random tools and helpers I've written that come in handy that are generally missing in the Amazon CLI Tools.  These tools all extend/expand on the Amazon AWS CLI tools which must be installed for any of these to work.

# [aws-choose-profile](https://github.com/DevOps-Nirvana/aws-missing-tools/tree/master/aws-choose-profile)
A bash/fish script that scans for profiles defined in ~/.aws/credentials and in ~/.aws/config and asks you to choose one of them, and then sets the AWS_PROFILE and AWS_DEFAULT_PROFILE environment variables for you from the chosen profile.  Great for sysadmins/devs that manage more than one AWS account via command-line based tools.

# [aws-mfa-login](https://github.com/DevOps-Nirvana/aws-missing-tools/tree/master/aws-mfa-login)
A bash script that allows you to login to an virtual MFA (2FA) for an cli access key or assume into an role via 2FA.  This makes it so you don't need to be so paranoid about having access/secret keys on your employee laptops or worry about them leaking to Github.  It allows you to skip having to setup complex client-side systems for your employees such as [AWS Vault](https://github.com/99designs/aws-vault) to try to encrypt your devs credentials on every computer.

# [aws-autoscaling-rollout](https://github.com/DevOps-Nirvana/aws-missing-tools/tree/master/aws-autoscaling-rollout)
Performs a zero-downtime rolling deploy of servers in an autoscaling group.  Very loosely based on the "aws-ha-release" tool from colinbjohnson combined with a tool I wrote back in 2009 and has been pending open-sourcing forever.  This is currently in use at a dozen places that I know of that I engineered their CI/CD Pipelines.

# [aws-iam-require-mfa-allow-self-service](https://github.com/DevOps-Nirvana/aws-missing-tools/tree/master/aws-iam-require-mfa-allow-self-service)
A "best-practice" IAM Profile which ideally is assigned to an IAM Role which is assigned to all your users to ensure/guarantee all users use 2FA constantly.

# [ec2-metadata](https://github.com/DevOps-Nirvana/aws-missing-tools/tree/master/ec2-metadata)
A amazon-written helper that should really be automatically installed on every instance automatically IMHO to query the metadata.  It is easy enough to do on your own via curl, but it comes in handy to have a helper as well.

# [aws-push-cloudwatch-instance-metrics](https://github.com/DevOps-Nirvana/aws-missing-tools/tree/master/aws-push-cloudwatch-instance-metrics)
This helper, intended to be run from cron every minute, pushes memory and disk usage to cloudwatch.  If this server is part of an autoscaling group, it also pushes against that dimension (within the EC2 namespace) to be able to query the autoscaler's combined memory & disk usage.

# [cleanup-packer-aws-resources](https://github.com/DevOps-Nirvana/aws-missing-tools/tree/master/cleanup-packer-aws-resources)
This performs a cleanup of packer resources.  Sometimes packer dies, horribly, and leaves instances and/or keys and/or security groups laying around.  This script goes through every region and cleans them up (after they are 24 hours old).  This can be very useful to be installed in a Lambda with the right permissions and run every day or so.

## Contributing
Feel free to contribute a tool you wrote that is missing in AWS via a pull request, or fix a bug in one of mine!

*NOTE*: This repository is a always a constant work in progress.
