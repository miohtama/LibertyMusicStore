#!/bin/bash
#
# Backup site PSQL + uploads to Mega.co.cz
#
# Installation
#    apt-get install duplicity
#    pip install mega.py
#

set -e

SITENAME=basename `pwd`

# Need to access:
source venv/bin/activate

# MEGA_USER + MEGA_PASSWORD
MEGA_USER=$1
MEGA_PASSWORD=$2

DUPLICITY_TARGET=mega://$MEGA_USER:$MEGA_PASSWORD@mega.co.nz/$SITENAME-backups

sudo -u postgres pg_dump tatianastore_production | bzip2 | > backups/$SITENAME-backup-$(date -d "today" +"%Y%m%d").sql.bzip2

# http://duplicity.nongnu.org/duplicity.1.html
duplicity --asynchronous-upload --full-if-older-than 1M `pwd` $DUPLICITY_TARGET

duplicity remove-older-than 6M $DUPLICITY_TARGET