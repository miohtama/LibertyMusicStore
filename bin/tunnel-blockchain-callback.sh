#!/bin/sh
#
# Make remote walletnotify server to notify this computer
#

# build a tunnel to the remote server which you can
# then put to blockchain.info API settings to receive
# payment notifications
ssh -g -v -R 78.47.218.165:4000:localhost:8000 moopay