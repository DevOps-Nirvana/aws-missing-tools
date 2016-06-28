# AWS Push Cloudwatch Instance Metrics

aws-push-cloudwatch-instance-metrics.py is a python script that grabs metrics about this instance including memory usage, swap usage, and disk usage, and pushes them to CloudWatch against our EC2 instance.  If this server is part of an autoscaling group, it also pushes against that dimension (within the EC2 namespace)


## Installation:
I recommend you symlink this into your user or system bin folder

### Installation Examples:

```
# Desired, symlink in place, so you can "git pull" and update this command from time to time
ln -s $(pwd)/aws-push-cloudwatch-instance-metrics.py /usr/local/bin/
```
or copying it into place with...
```
# Not desired, but possible depending on your preference
cp -a aws-push-cloudwatch-instance-metrics.py /usr/local/bin/
```

## Directions For Use:
```
./aws-push-cloudwatch-instance-metrics.py
```

Intended to be used via cron...
```
# Every minute
* * * * * /usr/local/bin/aws-push-cloudwatch-instance-metrics.py >> /var/log/aws-push-cloudwatch-instance-metrics.py.log
# or every 5 minutes
*/5 * * * * /usr/local/bin/aws-push-cloudwatch-instance-metrics.py >> /var/log/aws-push-cloudwatch-instance-metrics.py.log
```

## Potential Use:
For getting useful EC2 metrics into cloudwatch which you can set alarms for and react accordingly, including setting alarms with automatic autoscaling actions.


## Todo:
If you'd like to help contribute (or when the author is bored) there are some features that could be added...
- Others?  Submit feature requests as a bug in Github


## Additional Information:
- Author(s): Farley farley@neonsurge.com
- First Published: 2016-06-20
- Version 0.0.1
- License Type: MIT
