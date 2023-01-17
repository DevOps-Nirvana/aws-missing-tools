#!/usr/bin/env bash
BACKUPFILE="/tmp/backup-env-vars"
env | grep AWS_ | grep -v _PROFILE > $BACKUPFILE
# echo 'export PS1="$(echo $PS1)"' # >> $BACKUPFILE
# Set the export up
sed -i -e 's/^/export /' $BACKUPFILE
echo "cd $PWD" >> $BACKUPFILE
cat $BACKUPFILE | pbcopy
rm -f $BACKUPFILE || true
