#!/usr/bin/python

import subprocess
from datetime import datetime
import string
import sys, os

# Command line arguments for build environment

if len(sys.argv) >= 2:
    arg = sys.argv[1]
else:
    arg = "default - external/prod"

if arg == "internal":
    url = os.environ["INTERNAL"]
    local = False
    branch = "gh-pages"
elif arg == "localhost":
    url = "localhost:4000"
    local = True
    branch = ""
else:
    url = "tech.capitalone.ca"
    local = False
    branch = "master"

print "[INFO] Using build environment %s" % arg
print "[INFO] Checking URL %s" % url

# Setup
needbuild = False
now = datetime.now()

command = 'curl %s/events_feed.xml --silent | grep endDate | sed \'s#<[^>]*>##g\' | sed \'s# [+-].*$#\&#\' | xargs' % url

fetchDates = subprocess.check_output(command, shell=True)

eventDates = fetchDates.split("&")

# Check Event Dates

for d in eventDates:
    d = d.strip()
    if len(d) != 0:
        date_object = datetime.strptime(d, '%a, %d %b %Y %H:%M:%S')
        # Sample Date Format: Thu, 24 Mar 2016 20:00:00 +0000
        if now > date_object:
            print "[INFO] Event has passed"
            print "[INFO] Current Date:", now, "Event Date:", date_object
            needbuild = True
            break
        else:
            print "[INFO] Event is in the future"
            print "[INFO] Current Date:", now, "Event Date:", date_object

# Build if needed

if needbuild and not local:
    print "[INFO] There is an event that has passed. Will update RSS feeds."
    print "[INFO] Commiting to %s branch" % branch
    subprocess.call("git fetch origin")
    subprocess.call("git checkout -b %s" % branch)
    subprocess.call("git commit -m 'Rebuilding site to update RSS feeds' --allow-empty")
    print "[INFO] Pushing to remote branch %s" % branch
    subprocess.call("git push origin %s:%s" % (branch, branch))
else:
    print "[INFO] No rebuild needed. Commit was not made."
