#!/usr/local/bin/python

from urllib2 import Request, urlopen, URLError
import json
import math
import sys
import os
import socket
import optparse

def arg_parser():
    cwd_dir = os.getcwd()
    parser = optparse.OptionParser()
    parser.add_option( '-p', dest='runid', help='Project ID: required')
    parser.add_option( '-a', dest='accesstoken', help='Access Token: required')
    ( options, args ) = parser.parse_args()
   
    try:
       if options.runid == None:
             raise Exception
       if options.accesstoken == None:
	     raise Exception

    except Exception:
	    print("Usage: BaseSpaceFastqDownloader.py -p <ProjectID> -a <AccessToken>")
	    sys.exit()
    
    return options

def restrequest(rawrequest):
	request = Request(rawrequest)

	try:
        	response = urlopen(request)
        	json_string = response.read()
        	json_obj = json.loads(json_string)

	except URLError, e:
    		print 'Got an error code:', e
		sys.exit()

	return json_obj

def downloadrestrequest(rawrequest,name):
	request = (rawrequest)
	outfile = open(name,'wb')

        try:
                response = urlopen(request,timeout=1)
		
		outfile.write(response.read())
		outfile.close()

        except URLError, e:
                print 'Got an error code:', e
		outfile.close()
		downloadrestrequest(rawrequest,path)


	except socket.error:
		print 'Got a socket error: retrying'
		outfile.close()
		downloadrestrequest(rawrequest,path)
		

options = arg_parser()

RunID = options.runid
AccessToken = options.accesstoken

request = 'http://api.basespace.illumina.com/v1pre3/projects/%s/samples?access_token=%s' %(RunID,AccessToken)

project_json_obj = restrequest(request)
nsamples = len(project_json_obj['Response']['Items'])

hreflist = []
namelist = []

for sampleindex in range(nsamples):
	SampleId = project_json_obj['Response']['Items'][sampleindex]['Id']
	request = 'https://api.basespace.illumina.com/v1pre3/samples/%s/files?access_token=%s' %(SampleId,AccessToken)
	sample_json_obj = restrequest(request)
	nfiles = len(sample_json_obj['Response']['Items'])

	for fileindex in range(nfiles):
		hreflist.append(sample_json_obj['Response']['Items'][fileindex]['Href'])
		namelist.append(sample_json_obj['Response']['Items'][fileindex]['Name'])

print "Downloading %s files" %(len(hreflist))
for index in range(len(hreflist)):
	request = 'http://api.basespace.illumina.com/%s/content?access_token=%s'%(hreflist[index],AccessToken)
	print 'downloading %s' %(namelist[index]) 
	downloadrestrequest(request, namelist[index])
