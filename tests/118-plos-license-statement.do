#!/bin/sh
# Tests if the CC BY 4.0 License used by PLOS is picked up by OAMI.
../oa-cache clear-database pmc_doi
echo \
  10.1371/journal.pbio.1001781 \
  10.1371/journal.pone.0088810 \
  10.1371/journal.pone.0088782 | \
  ../oa-get download-metadata pmc_doi && \
  ../oa-cache find-media pmc_doi
check_license() {
  set +x
  LICENSE="$(
    sqlite3 $(../oa-cache print-database-path pmc_doi) \
    "select * from model_article where doi == '$1';" | \
    cut -d'|' -f10
  )"
  test "$LICENSE" = "$2"
}
check_license "10.1371/journal.pbio.1001781" \
  "http://creativecommons.org/licenses/by/4.0/"
check_license "10.1371/journal.pone.0088810" \
  "http://creativecommons.org/licenses/by/4.0/"
check_license "10.1371/journal.pone.0088782" \
  "http://creativecommons.org/licenses/by/4.0/"
