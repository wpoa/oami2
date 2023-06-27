#!/bin/bash

TIMEOUTFILE=timeout_pmcid.txt
SCRIPTNAME=`basename $0`
PIDFILE=/var/lock/${SCRIPTNAME}.pid

trap "killall oami_pmc_pmcid_import oa-put oa-get oa-cache; echo 'signal caught, exiting'; exit 255" SIGINT SIGTERM

# from http://stackoverflow.com/a/959511
if [[ -f ${PIDFILE} ]]; then
   #verify if the process is actually still running under this pid
   OLDPID=`cat ${PIDFILE}`
   RESULT=`ps -ef | grep ${OLDPID} | grep ${SCRIPTNAME}`  
   if [[ -n "${RESULT}" ]]; then
     echo "Script already running! Killing it!"
     kill ${OLDPID}
     sleep 2
     STILL_ALIVE=`ps -ef | grep ${OLDPID} | grep ${SCRIPTNAME}`
     if [[ -n "${STILL_ALIVE}" ]]; then
         kill -9 ${OLDPID}
         sleep 1
         STILL_STILL_ALIVE=`ps -ef | grep ${OLDPID} | grep ${SCRIPTNAME}`
         if [[ -n "${STILL_STILL_ALIVE}" ]]; then
            echo "... script is unkillable - giving up."
            exit 255
         fi
     fi
   fi
fi

#grab pid of this process and update the pid file with it
PID=`ps -ef | grep ${SCRIPTNAME} | head -n1 |  awk ' {print $2;} '`
echo ${PID} > ${PIDFILE}

# make sure that all previous processes are gone

killall oami_pmc_pmcid_import
sleep 1
killall oa-put oa-cache oa-get

STILL_RUNNING=`pgrep "(oa-get|oa-put|oa-cache)"`
if [[ -n ${STILL_RUNNING} ]]; then
   echo "OAMI processes still running despite killing them. Exiting."
   exit 255
fi

# clear cache
./oa-cache clear-database pmc_pmcid

for pmcid in $(./oa-pmc-ids --from $(date +"%F" -d '3 days ago') --until $(date +"%F")); do
  date
  timeout 6h sh -c "echo $pmcid | ./oami_pmc_pmcid_import"
  if [ $? -eq 124 ]; then 
        echo "------------------ Timed out! --------------------"
        echo $pmcid >> "$TIMEOUTFILE"
  fi
  ./oa-cache clear-database pmc_pmcid 
done;

if [ -f ${PIDFILE} ]; then
    rm ${PIDFILE}
fi
