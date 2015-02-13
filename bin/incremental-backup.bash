#!/bin/bash
#
# Backup site SQL + media files to S3
#
# http://www.janoszen.com/2013/10/14/backing-up-linux-servers-with-duplicity-and-amazon-aws/
# http://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteEndpoints.html
#
# Installation in Python 2.7 virtualenv
#
#    virtualenv -p python2.7 duplicity-venv
#    source duplicity-venv/bin/activate
#    apt-get install -y librsync-dev
#    pip install https://launchpad.net/duplicity/0.7-series/0.7.01/+download/duplicity-0.7.01.tar.gz
#    pip install boto
#
# Initialize SSL certificate database for Duplicity (Mozilla's copy):
#
#     mkdir /etc/duplicity
#     curl ~/.duplicity/cacert.pem http://curl.haxx.se/ca/cacert.pem > /etc/duplicity/cacert.pem
#
#     bin/incremental-backup.bash
#
# Note: The user running this script must have sudo -u postgres acces to run pg_dump
#
# Note: This script is safe to run only on a server where you have 100% control and there are no other UNIX users who could see process command line or environment
#
# Note: Do **not** use AWS Frankfurt region - it uses unsupported authentication scheme - https://github.com/s3tools/s3cmd/issues/402
#
# # s3-us-west-2.amazonaws.com/liberty-backup3/liberty-backup

set -e

# Assume we are /srv/django/mysite
PWD=`pwd`
SITENAME=`basename $PWD`

# Need to access:
source duplicity-venv/bin/activate

DUPLICITY_TARGET=s3://s3-us-west-2.amazonaws.com/liberty-backup3/$SITENAME

# Tell credentials to Boto
export AWS_ACCESS_KEY_ID=$1
export AWS_SECRET_ACCESS_KEY=$2
export BACKUP_ENCRYPTION_KEY=$3

if [ -z "$BACKUP_ENCRYPTION_KEY" ]; then
    echo "You must give AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and BACKUP_ENCRYPTION_KEY on the command line"
    exit 1
fi

# Create daily dump of the database
sudo -u postgres pg_dump tatianastore_production | bzip2 | gpg --batch --symmetric --passphrase $BACKUP_ENCRYPTION_KEY > backups/$SITENAME-dump-$(date -d "today" +"%Y%m%d").sql.bzip2.gpg

# http://duplicity.nongnu.org/duplicity.1.html
# Incrementally backup all files, inc. just generated SQL dump, media files and source code.
# Our media files are not sensitive, so those are not encrypted.
#duplicity -v9 --ssl-no-check-certificate --s3-use-new-style --s3-european-buckets --s3-use-rrs --s3-use-multiprocessing --exclude=`pwd`/logs --exclude=`pwd`/.git --exclude=`pwd`/venv --exclude=`pwd`/duplicity-venv --no-encryption --full-if-older-than 1M `pwd` $DUPLICITY_TARGET

duplicity --s3-use-rrs --exclude=`pwd`/logs --exclude=`pwd`/.git --exclude=`pwd`/venv --exclude=`pwd`/duplicity-venv --no-encryption --full-if-older-than 1M `pwd` $DUPLICITY_TARGET


# Clean up old backups
duplicity remove-older-than 3M $DUPLICITY_TARGET