#!/bin/bash
#!/bin/bash
USER=$1
DT=`date --iso-8601=minutes`
mkdir -p targeting
pipenv run twint -u $USER -o targeting/$USER-$DT.json --json >/dev/null 2>targeting/$USER-$DT.log
