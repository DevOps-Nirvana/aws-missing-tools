# AWS Autoscaling Rollout

aws-autoscaling-rollout is a Python script to perform a rotation of servers in an autoscaling group, although 
currently very simplified, this is a placeholder for the "final" version that I have yet to migrate to Python 
and open source.  I will do this soon, I promise!

Loosely based on and inspired by the "aws-ha-release" tool from Colin Johnson - colinbjohnson
https://github.com/colinbjohnson/aws-missing-tools/tree/master/aws-ha-release 



## Installation:
I recommend you symlink this into your user or system bin folder

### Installation Examples:

```
# Desired, symlink in place, so you can "git pull" and update this command from time to time
ln -s $(pwd)/aws-autoscaling-rollout.py /usr/local/bin/
```
or copying it into place with...
```
# Not desired, but possible depending on your preference
cp -a aws-autoscaling-rollout.py /usr/local/bin/
```

## Directions For Use:
```
./aws-autoscaling-rollout.py -a autoscaler_name
```

## Potential Use:
Once an autoscaler has been changed to a new launch configuration, this script helps perform a "rolling" deploy of that autoscaling group, one by one shutting down and starting up new instances of the new launch configuration.


## Todo:
Don't submit patches yet until I've got the "final" version created here


## Additional Information:
- Author(s): Farley farley@neonsurge.com
- First Published: 2016-06-24
- Version 0.0.1
- License Type: MIT
