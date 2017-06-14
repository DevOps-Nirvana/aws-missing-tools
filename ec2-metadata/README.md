# EC2 Metadata - bash

## Introduction:
ec2-metadata - A simple bash script that uses curl to query the EC2 instance Metadata from within a running EC2 instance.

This helper came out a long while ago.  This is NOT written by me, but is used a lot by me so I put it in my toolkit.  The originally is from...
https://aws.amazon.com/code/1825
and
http://s3.amazonaws.com/ec2metadata/ec2-metadata

## Installation:
This script never changes, and is typically installed on EVERY AWS-based instance I manage, typically done via a packer/ansible/chef/puppet script, usually auto-downloaded from "http://s3.amazonaws.com/ec2metadata/ec2-metadata"


### Installation Example:

```
curl http://s3.amazonaws.com/ec2metadata/ec2-metadata > /usr/local/bin/ec2-metadata
```
or from here incase that disappears...
```
curl https://raw.githubusercontent.com/AndrewFarley/farley-aws-missing-tools/master/ec2-metadata/ec2-metadata > /usr/local/bin/ec2-metadata
```

## Directions For Use:

```
ec2-metadata
```
