#!/bin/bash

TIMEOUTFILE=timeout_pmcid.txt

# clear cache
./oa-cache clear-database pmc_pmcid

for pmcid in $(./oa-pmc-ids --from $(date +"%F" -d '3 days ago') --until $(date +"%F")); do
  date
  timeout 6h sh -c "echo $pmcid | ./oami_pmc_pmcid_import"
  if [[ $? == 124 ]]; then 
	echo "------------------ Timed out! --------------------"
	echo $pmcid >> "$TIMEOUTFILE"
  fi
  ./oa-cache clear-database pmc_pmcid 
done;


