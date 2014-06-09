#!/bin/sh
#
# Simulate blockchain bitcoin deposit received notification
#
# Usage:
#
#     bin/simulate-blockchain-receive.sh 1000009 1LqJFpdPDdg6fURuiBt3aCzPiwWNEPHVJM
#
# Value in Satoshis
#
# 1 BTC = 100000009
# 0.01 BTC 1000009

wget -S --output-document="-" "http://localhost:8000/blockchain_received/?transaction_hash=x&value="$1"&address="$2
