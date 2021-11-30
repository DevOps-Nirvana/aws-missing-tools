# AWS MFA Login

## Introduction:
This script makes an AWS Access Key / Secret Key login via 2FA on your CLI, or assume into an role via 2FA.

* Allows you to login to 2FA via the CLI for an existing Access/Secret key
* Allows you to assume into an role on the same or different AWS account
* Preserves your region if set on the source role/account
* Currently only supports the Virtual MFA, send a PR if you wish to add others
* Prevents potential huge security issues leaking because of accidentally committed access/secret keys to SCM/Git
  * _**NOTE:** When combined with [AWS IAM Require MFA Allow Self Service Profile](#example-user-with-mandatory-2fa)_
* Allows you to ensure better/best security practices on AWS, making all your roles mandatory 2FA to assume into them.
  * _**NOTE:** See [example below](#example-role-with-mandatory-2fa) for roles with mandatory 2FA on them_

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

## Example: User with Mandatory 2FA

This combos nicely with the [AWS IAM Require MFA Allow Self Service Profile](../aws-iam-require-mfa-allow-self-service/) which is an IAM Profile which enforces 2FA for AWS IAM Access Keys which makes them inherently less sensitive.  This would prevent a potential security/privacy leak in your organization if someone accidentally committed their access/secret keys somewhere (like Github).

This allows you to skip having to setup complex client-side systems for your employees such as [AWS Vault](https://github.com/99designs/aws-vault) to try to encrypt your IAM access-keys/secrets, instead leveraging industry-standard 2FA on top of your existing Access/Secret credential pairs.

Below is the JSON copied from the above link for [AWS IAM Require MFA Allow Self Service Profile](../aws-iam-require-mfa-allow-self-service/) for your reference, this is an ideal and battle-tested configuration allowing a user to self-manage themselves enough with no MFA to enable it, and then allowing a standard amount of read/list operations that most users would appreciate from the get-go and to prevent a ton of errors in the AWS Console.  It's a combination of a few recommended permissions from various AWS articles.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowListUsersAllIfMFA",
            "Effect": "Allow",
            "Action": [
                "iam:ListUsers",
                "iam:ListPolicies",
                "iam:ListGroups",
                "iam:ListGroupPolicies",
                "iam:ListAttachedGroupPolicies",
                "iam:GetServiceLastAccessedDetails",
                "iam:GetPolicyVersion",
                "iam:GetGroup",
                "access-analyzer:ListPolicyGenerations"
            ],
            "Resource": "*",
            "Condition": {
                "Bool": {
                    "aws:MultiFactorAuthPresent": [
                        "true"
                    ]
                }
            }
        },
        {
            "Sid": "AllowIndividualUserToDescribeTheirOwnMFAAndSecurityObjects",
            "Effect": "Allow",
            "Action": [
                "iam:getUser",
                "iam:ResyncMFADevice",
                "iam:ListVirtualMFADevices",
                "iam:ListUserTags",
                "iam:ListUserPolicies",
                "iam:ListSigningCertificates",
                "iam:ListServiceSpecificCredentials",
                "iam:ListSSHPublicKeys",
                "iam:ListPoliciesGrantingServiceAccess",
                "iam:ListMFADevices",
                "iam:ListGroupsForUser",
                "iam:ListAttachedUserPolicies",
                "iam:ListAccessKeys",
                "iam:GetSSHPublicKey",
                "iam:GenerateServiceLastAccessedDetails",
                "iam:EnableMFADevice",
                "iam:CreateVirtualMFADevice"
            ],
            "Resource": [
                "arn:aws:iam::*:user/${aws:username}",
                "arn:aws:iam::*:mfa/${aws:username}"
            ]
        },
        {
            "Sid": "AllowIndividualUserToManageTheirOwnMFAWhenUsingMFA",
            "Effect": "Allow",
            "Action": [
                "iam:UploadSigningCertificate",
                "iam:UploadSSHPublicKey",
                "iam:UpdateSigningCertificate",
                "iam:UpdateServiceSpecificCredential",
                "iam:UpdateAccessKey",
                "iam:ResetServiceSpecificCredential",
                "iam:DeleteVirtualMFADevice",
                "iam:DeleteSigningCertificate",
                "iam:DeleteServiceSpecificCredential",
                "iam:DeleteSSHPublicKey",
                "iam:DeleteAccessKey",
                "iam:DeactivateMFADevice",
                "iam:CreateServiceSpecificCredential",
                "iam:CreateAccessKey"
            ],
            "Resource": [
                "arn:aws:iam::*:user/${aws:username}",
                "arn:aws:iam::*:mfa/${aws:username}"
            ],
            "Condition": {
                "Bool": {
                    "aws:MultiFactorAuthPresent": [
                        "true"
                    ]
                }
            }
        },
        {
            "Sid": "BlockMostAccessUnlessSignedInWithMFA",
            "Effect": "Deny",
            "NotAction": [
                "iam:getUser",
                "iam:ResyncMFADevice",
                "iam:ListVirtualMFADevices",
                "iam:ListSigningCertificates",
                "iam:ListServiceSpecificCredentials",
                "iam:ListSSHPublicKeys",
                "iam:ListMFADevices",
                "iam:ListAccessKeys",
                "iam:EnableMFADevice",
                "iam:CreateVirtualMFADevice",
                "iam:ChangePassword"
            ],
            "Resource": "*",
            "Condition": {
                "BoolIfExists": {
                    "aws:MultiFactorAuthPresent": [
                        "false"
                    ]
                }
            }
        }
    ]
}
```


## Example: Role with Mandatory 2FA

Below is the JSON for the "Trust Relationship" for an IAM role which will make MFA/2FA mandatory, ensuring users can't skip 2FA to get into the role.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowUsersToAssumeFromAccountWithMFA",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123123123123:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    }
  ]
}
```
