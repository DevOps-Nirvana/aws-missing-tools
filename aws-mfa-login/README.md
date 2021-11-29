# AWS MFA Login

## Introduction:
This script logs in an AWS Access Key / Secret Key via 2FA on your CLI.

OR

This script allows assuming into an role via 2FA if the environment variable ASSUME_ROLE_ARN is set

This script assumes you're already having a working AWS CLI and profile.  If you are using AWS CLI profiles, make sure you set your profile before running this script with eg: `export SOURCE_PROFILE=mycompany` which is the same name you used to `aws configure --profile mycompany`.

For a helper for this, see: https://github.com/DevOps-Nirvana/aws-missing-tools/tree/master/aws-choose-profile

OR...

## Enable 2FA on an Access/Secret Key

```bash
# First, try this command (replace mycompany with your awscli profile name and the name of your aws account alias or company name)
AWS_DEFAULT_PROFILE=mycompany ASSUME_ROLE_LABEL=mycompany aws-mfa-login

# And if that works, you have to check which shell you are using.  The default since recently on OS-X is (annoyingly) zsh, so we'll have instructions for zsh/bash
echo $SHELL

# If $SHELL has "bash" in it, you'll do the following...
#   #1: make an alias in your ~/.bash_profile like this...
echo "alias mycompany_aws_2fa='AWS_DEFAULT_PROFILE=mycompany-aws-root ASSUME_ROLE_LABEL=mycompany aws-mfa-login'" >> ~/.bash_profile
#   #2:  begin using it instantly
source ~/.bash_profile

# OR If $SHELL has "zsh" in it, you'll do the following...
#   #1: make an alias in your ~/.zshrc like this...
echo "alias mycompany_aws_2fa='AWS_DEFAULT_PROFILE=mycompany-aws-root ASSUME_ROLE_LABEL=mycompany aws-mfa-login'" >> ~/.zshrc
#   #2:  begin using it instantly
source ~/.zshrc

# then run it with...
mycompany_aws_2fa
```

## Assume into another role with 2FA

```bash
# First, try this command (replace the values below, similar to above, but add the ASSUME_ROLE_ARN with the ARN you want to assume)
AWS_DEFAULT_PROFILE=mycompany ASSUME_ROLE_LABEL=my_role_name_here ASSUME_ROLE_ARN=arn:aws:iam::1231231234:role/role_name_here aws-mfa-login

# If you get an error about invalid session duration (defaults to 12h) lower it to 1h (3600 seconds) with the following...
AWS_DEFAULT_PROFILE=mycompany ASSUME_ROLE_LABEL=my_role_name_here ASSUME_ROLE_ARN=arn:aws:iam::1231231234:role/role_name_here SESSION_DURATION=3600 aws-mfa-login

# And if that works, similar as above you have to check which shell you are using.  The default since recently on OS-X is (annoyingly) zsh, so we'll have instructions for zsh/bash
echo $SHELL

# If $SHELL has "bash" in it, you'll do the following...
#   #1: make an alias in your ~/.bash_profile like this...
echo "alias my_other_company_role_aws_2fa='AWS_DEFAULT_PROFILE=mycompany ASSUME_ROLE_LABEL=my_role_name_here ASSUME_ROLE_ARN=arn:aws:iam::1231231234:role/role_name_here aws-mfa-login'" >> ~/.bash_profile
#   #2:  begin using it instantly
source ~/.bash_profile

# OR If $SHELL has "zsh" in it, you'll do the following...
#   #1: make an alias in your ~/.zshrc like this...
echo "alias my_other_company_role_aws_2fa='AWS_DEFAULT_PROFILE=mycompany ASSUME_ROLE_LABEL=my_role_name_here ASSUME_ROLE_ARN=arn:aws:iam::1231231234:role/role_name_here aws-mfa-login'" >> ~/.zshrc
#   #2:  begin using it instantly
source ~/.zshrc

# then run it with...
mycompany_aws_2fa
```


This combos nicely with the [AWS IAM Require MFA Allow Self Service Profile](../aws-iam-require-mfa-allow-self-service) which is an IAM Profile which enforces 2FA for AWS IAM Access Keys which makes them inherently less sensitive.  This would prevent a potential security/privacy leak in your organization if someone accidentally committed their access/secret keys somewhere (like Github).

This allows you to skip having to setup complex client-side systems for your employees such as [AWS Vault](https://github.com/99designs/aws-vault) to try to encrypt your dev credentials, instead leveraging industry-standard 2FA on top of your existing Access/Secret credential pairs.
