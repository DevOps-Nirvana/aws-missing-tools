#!/usr/local/bin/fish
#
###############################################################################
#
#    aws-choose-profile.fish         Written by Farley <farley@neonsurge.com>
#
# This helper scans for profiles defined in ~/.aws/credentials and in 
# ~/.aws/config and asks you to choose one of them, and then sets the 
# AWS_PROFILE and AWS_DEFAULT_PROFILE environment variables.  This is ONLY
# possible if you `source` this program in the `fish` shell, for other
# shell wrappers, see the other files with different extensions, if you don't
# see a shell you want, ask me and I'll add it!
#
# Usage example: 
#    source aws-choose-profile
# or
#    . aws-choose-profile
# 
# If you do not source it, this script will detect this state
# and warn you about it, and not allow you to choose (since it's)
# useless
#
# I recommend you symlink this into your user or system bin folder
# Please note: if you choose to install (aka cp) this, you must also install
# the file "aws-choose-profile-helper.py" along side it, which has the the 
# aws profile selection logic
#
###############################################################################

# Get actual full file path of this script
set -l SCRIPTNAME (status -f)
# If our path is a full path already, don't prefix with pwd when figuring out our directory
if [ (string sub --start 1 -l 1 $SCRIPTNAME) = '/' ] 
    set DIR (dirname (fish_realpath (status -f)))
else
    set DIR (dirname (fish_realpath (pwd)/(status -f)))
end

# Always print our current profile
if [ $AWS_DEFAULT_PROFILE ]
    echo "Current AWS Profile: $AWS_DEFAULT_PROFILE"
else
    echo "Current AWS Profile: none"
end


# Simple check if we are sourced
set -l result (status -t) 
switch "$result"
    case '*sourcing*'
        # If we were caught here then COOL, we are "sourced"
    case '*'
        echo "ERROR: Not sourced, please run source " (status -f)
        exit 1
end

# Now do the magic...
eval unlink /tmp/aws-choose-profile.temp 2> /dev/null
eval $DIR/aws-choose-profile-helper.py /tmp/aws-choose-profile.temp
set -l CHOSEN_PROFILE (tail -n1 /tmp/aws-choose-profile.temp 2>/dev/null)

# Remove our temp file
eval unlink /tmp/aws-choose-profile.temp 2>/dev/null

# Always set our environment variables if the user said to
if [ $CHOSEN_PROFILE ]
     echo "Chosen Profile: $CHOSEN_PROFILE"
     set -x AWS_DEFAULT_PROFILE $CHOSEN_PROFILE
     set -x AWS_PROFILE $CHOSEN_PROFILE
     echo "Exported AWS_PROFILE and AWS_DEFAULT_PROFILE to $CHOSEN_PROFILE"
     exit 0
else
     echo "No profile chosen, so no profile set"
     exit 1
end
