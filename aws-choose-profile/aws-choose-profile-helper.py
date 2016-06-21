#!/usr/bin/env python
#
###############################################################################
#
#    aws-choose-profile-helper.py    Written by Farley <farley@neonsurge.com>
#
# This script does the actual scanning of the aws config files and asking the
# user for their selection.  Please see more detailed description and info
# in the parent script, aws-choose-profile
#
###############################################################################

# Libraries
# Config parsing
import ConfigParser
Config = ConfigParser.ConfigParser()
# For homedir and isfile
import os
home_dir = os.path.expanduser("~")
# For argv handling
import sys

###################
# Globals helpers #
###################
def contains_value(array, string):
    for item in array:
        if string == item:
            return True
    return False

def represents_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
###################

# If we want to print debug information along with running this
debug_output = False
write_output_to_file = False
if debug_output:
    print "Starting up..."

# Check for CLI args (used to determine where to write the output/result)
if len(sys.argv) >= 2:
    write_output_to_file = sys.argv.pop(1)
    if debug_output:
        print "Writing chosen profile to: " + temp
    if os.path.isfile(write_output_to_file):
        if debug_output:
            print "Removing chosen profile temp file"
        os.remove(write_output_to_file)
else:
    if debug_output:
        print "Echoing out chosen profile to screen"

# We always have a "default" profile
profiles = []
profiles.append('default')

# Read our credentials file
if os.path.isfile(home_dir + "/.aws/credentials"):
    if debug_output:
        print "Reading from " + home_dir + "/.aws/credentials..."
    Config.read(home_dir + "/.aws/credentials")
    
    # Debug output
    if debug_output:
        print "Got the following profiles..."
        print Config.sections()

    for item in Config.sections():
        if not contains_value(profiles, item):
            profiles.append(item)
else:
    if debug_output:
        print "No file to read from at " + home_dir + "/.aws/credentials"

# Read our config file
if os.path.isfile(home_dir + "/.aws/credentials"):
    if debug_output:
        print "Reading from " + home_dir + "/aws/config..."
    Config.read(home_dir + "/.aws/config")
    
    # Debug output
    if debug_output:
        print "Got the following profiles..."
        print Config.sections()

    for item in Config.sections():
        # First, cleanse our "profile " prefix
        cleanitem = item.replace("profile ", "")
        if not contains_value(profiles, cleanitem):
            profiles.append(cleanitem)
else:
    print "No file to read from at " + home_dir + "/.aws/config"

# Finally sort alphabetically
sorted(profiles, key=str.lower)
# And remove and re-insert "default" to make sure it's always first on the list
profiles.remove('default')
profiles.insert(0, 'default')
if debug_output:
    print(profiles)

# Print profiles available
print "==============================="
print " Profiles available"
print "==============================="
count = 1
for profile in profiles:
    print str(count) + ". " + profile
    count = count + 1
print "==============================="
count = count - 1

# Ask the user to choose a profile infinitely
while True:
    var = raw_input("Choose a profile number: [1-" + str(count) + "]: ")

    if represents_int(var) and int(var) > 0 and int(var) <= count:
        break;
    else:
        print "Invalid input"
var = str(int(var) - 1)

# Take the chosen profile and print or write it to a file
chosen = profiles.pop(int(var))
if debug_output:
    print "You chose: " + chosen
if write_output_to_file == False:
    if debug_output:
        print "Printing to screen"
    print chosen
else:
    print "Writing output to file " + write_output_to_file
    text_file = open(write_output_to_file, "w")
    text_file.write(chosen)
    text_file.close()

exit(0)