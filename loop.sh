#!/bin/bash

PATH=/python/danawa

if [ -z "$PRODUCT_CODES" ]; then
   echo "PRODUCT_CODES is empty"
   exit 1
fi

for pcode in $PRODUCT_CODES
do
    /usr/local/bin/python ${PATH}/DanawaProduct.py $pcode
    /bin/sleep 1
done

