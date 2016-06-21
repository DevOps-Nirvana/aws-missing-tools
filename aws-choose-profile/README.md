# AWS Choose Profile, bash + python

aws-choose-profile is a bash script that scans for profiles defined in ~/.aws/credentials and in ~/.aws/config and asks you to choose one of them, and then sets the AWS_PROFILE and AWS_DEFAULT_PROFILE environment variables for you from the chosen profile.  This is ONLY
possible if you `source` this program (due to the way shell environments work).

If you do not source it, this script will detect this state and warn you about it, and not allow you to choose (since it's useless)

## Installation:
I recommend you symlink this into your user or system bin folder.  NOTE: if you choose to "install" this, you must also install
the file "aws-choose-profile-helper.py" along side it, which has the the actual profile selection logic since mangling arrays and managing data is difficult in bash alone.  So

### Installation Examples:

```
# Desired, symlink in place, so you can "git pull" and update this command from time to time
ln -s $(pwd)/aws-choose-profile /usr/local/bin/
```
or copying it into place with...
```
# Not desired, but possible depending on your preference
cp -a aws-choose-profile* /usr/local/bin/
```

## Directions For Use:
![Demo of aws-choose-profile](https://raw.githubusercontent.com/AndrewFarley/farley-aws-missing-tools/master/aws-choose-profile/demo.png "Demo of AWS Choose Profile helper")

```
source aws-choose-profile
```
or even shorter with...
```
. aws-choose-profile
```

## Potential Use:
For sysadmins and geeks who manage more than one AWS-based client and/or have multiple accounts to manage with consolidated billing, this script helps wranggle your local credentials to manage those various AWS accounts.


## Todo:
If you'd like to help contribute (or when the author is bored) there are some features that could be added...
- Add ability to also set AWS_DEFAULT_REGION automatically based on the profile selected if that profile has a default region
- Add another "wrapper" besides bash-based for use in powershell/windows?  Any windows geeks interested?
- Others?  Submit feature requests as a bug in Github


## Additional Information:
- Author(s): Farley farley@neonsurge.com
- First Published: 2016-06-11
- Version 0.0.1
- License Type: MIT
