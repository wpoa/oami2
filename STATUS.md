What has been done:
-Updated Code of oa-cache, oa-put, oa-get | helpers and sources folders


Status Dummy File:
- python .\oa-get download-metadata pmc_doi | works with dois added in download_metadata function
- python .\oa-get download-metadata dummy   | Download of test files works if file url is a direct link to the file, metadata is not being downloaded
- python .\oa-get download-media [dummy/pmc_doi] | results with "0" no media files are downloaded
- python .\oa-cache find-media dummy |  works by changing how dummy works
- python .\oa-put upload-media dummy | doesnt work yet because it uses old elixir functions (.query) which have to be replaced with new ones


to-do: 
 - elixir equivalent (Elixir replacement has to be found especially for .query function in code)
 - oa-cache convert-media ffmpeg config
 - sqllite database
 - sqllite format might be malformed due to fields in the model.py (Article) might not exist in PMC anymore or might be named differently
