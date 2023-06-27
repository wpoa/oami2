======
oa-get
======

----------------------------------------------
Open Access Media Importer download operations
----------------------------------------------

:Author: Nils Dagsson Moskopp <nils@dieweltistgarnichtso.net>
:Date: 2014-02-20
:Manual section: 1

SYNOPSIS
========

oa-get {detect-duplicates | download-metadata | download-media |
       update-mimetypes} [source]

DESCRIPTION
===========

oa-get can download metadata and media of resources indexed with the
Open Access Media Importer (OAMI), which are usually supplementary
materials of scientific papers. oa-get can also update the internet
media types of resources, as media types stored in the OAMI database
might not correspond to the actual media type of resources.

All oa-get sub-commands need internet access.

detect-duplicates
    detect-duplicates is used to find out if resources in the OAMI
    database are already uploaded to the MediaWiki given in the OAMI
    configuration.

    For each resource in the OAMI database, oa-get outputs an entry of
    the form "MARKER DOI TITLE LABEL" to standard error, where MARKER
    is "[X]" if a resource has been found on the MediaWiki and "[ ]"
    if a resource has not been found on the MediaWiki, DOI is the
    Digital Object Identifier of the resource, TITLE is the title of
    the resource and LABEL is the LABEL of the resource.

download-metadata
    download-metadata is used to download information about resources
    indexed in the OAMI database. oa-get outputs progress on standard
    error.

download-media
    download-media is used to download resources indexed in the OAMI
    database. oa-get only downloads audio and video resources with a
    free license that are not already uploaded to the MediaWiki given
    in the OAMI configuration. oa-get outputs progress on standard
    error.

update-mimetypes
    update-mimetypes is used to update the internet media types stored
    in the OAMI database. For each resource, oa-get fetches the first
    12 bytes using HTTP range requests and then tries to infer its
    type using magic(5). oa-get outputs progress on standard error.

    If oa-get detects an "application/msword" media type, oa-get
    guesses the media type based on the extension: If a resource's URL
    ends with "ppt" or "PPT", the resource is considered to have a
    media type of "application/vnd.ms-powerpoint"; if a resource's URL
    ends with "xls" or "XLS", the resource is considered to have a
    media type of "application/vnd.ms-excel".

    If oa-get detects an "application/octet-stream" media type, it
    does not change the media type stored in the OAMI database.

    For each update of a media type in the OAMI database, oa-get
    outputs a message to standard error.

EXAMPLES
========

The following invocations of oa-get and oa-cache(1) work with the
supplementary materials of the paper "Self-organizing Mechanism for
Development of Space-filling Neuronal Dendrites" published in PLOS
Computational Biology with DOI 10.1371/journal.pcbi.0030212).

Invocation of oa-cache(1) is necessary to extract information from
files retrieved by oa-get and put it into the OAMI database. Indexing
is implemented as a separate task and does not happen automatically
because it can take a very long time to parse several GB of XML files.

::

    echo 10.1371/journal.pcbi.0030212 | oa-get download-metadata pmc_doi

    oa-cache find-media pmc_doi

    oa-get update-mimetypes pmc_doi

    oa-get download-media pmc_doi

BUGS
====

When OAMI has no materials indexed in the database, functions
outputting a progress bar crash with a ZeroDivisionError.

SEE ALSO
========

oa-cache(1), oa-put(1)
