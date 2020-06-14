#!/bin/bash
  
for user in `cat $1` ; do
  ./fetch-user.sh $user
done
