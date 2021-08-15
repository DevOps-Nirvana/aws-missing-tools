# IAM Require MFA - Allow Self Service

## Introduction:
This is a simple / example profile that uses Amazon's base profile, but fills in a lot of gaps to allow self management.  See [Amazon's Official MFA Self-Manage Profile Here](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_iam_mfa-selfmanage.html).  It is recommended to apply this to all users which are actual users (aka, not service users) to mandate that they use 2FA.

This combos nicely with the [AWSCLI Login Virtual MFA Script](../aws-mfa-login)
