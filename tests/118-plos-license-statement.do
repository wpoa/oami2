#!/bin/sh
# Tests if the CC BY 4.0 License used by PLOS is picked up by OAMI.
../oa-cache clear-database pmc_doi
PMCIDS_CC40_LEGALCODE="
10.1371/journal.pone.0087649
"

PMCIDS_CC40="
10.1371/journal.pone.0087644
10.1371/journal.pone.0087661
10.1371/journal.pone.0087662
10.1371/journal.pone.0087663
10.1371/journal.pone.0088014
10.1371/journal.pone.0088782
10.1371/journal.pone.0088810
10.1371/journal.pone.0089000
10.1371/journal.pbio.1001781
10.1371/journal.pcbi.1003447
"

echo "$PMCIDS_CC40" "$PMCIDS_CC40_LEGALCODE" | ../oa-get download-metadata pmc_doi
../oa-cache find-media pmc_doi

check_license() {
  SQL="select license_url from model_article where doi == '$1';"
  LICENSE="$(sqlite3 $(../oa-cache print-database-path pmc_doi) "$SQL")"
  test "$LICENSE" = "$2" || (printf '%s\nexpected <%s>\nfound <%s>\n' \
    "$SQL" "$2" "$LICENSE" >&2 && false)
}

for PMCID in $PMCIDS_CC40; do
  check_license "$PMCID" "http://creativecommons.org/licenses/by/4.0/"
done

for PMCID in $PMCIDS_CC40_LEGALCODE; do
  check_license "$PMCID" "http://creativecommons.org/licenses/by/4.0/legalcode"
done
