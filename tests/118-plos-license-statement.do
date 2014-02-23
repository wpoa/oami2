#!/bin/sh
# Tests if the CC BY 4.0 License used by PLOS is picked up by OAMI.
echo 10.1371/journal.pbio.1001781 | \
  ../oa-get download-metadata pmc_doi && \
  ../oa-cache find-media pmc_doi
LICENSE="$(
  sqlite3 $(../oa-cache print-database-path pmc_doi) \
  'select * from model_article' | cut -d'|' -f10
)"
test "$LICENSE" = "http://creativecommons.org/licenses/by/4.0/"
