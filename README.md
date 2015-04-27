# BaseSpaceFastqDownload
Code to download fastq files to server directly from Illumina BaseSpace

Usage:

1) You need to do a one-time configuration with your own BaseSpace account to get an access token (Step 5 in these instructions):
https://support.basespace.illumina.com/knowledgebase/articles/403618-python-run-downloader

2) Get the project id for the BaseSpace run that you want to download. This is in the project link url. For example, if the link to the project on BaseSpace is:

https://basespace.illumina.com/projects/123456789/sequencing_data

The project id is the number that comes after "projects/" -- in this case, 123456789.

3) Run the following command from within the directory where you want to download the fastq files:

BaseSpaceFastqDownloader.py -p {ProjectId} -a {AccessCode}

This may not work for old MiSeq runs, but should work for MiSeq runs moving forward (i.e. for which there is a Project)
