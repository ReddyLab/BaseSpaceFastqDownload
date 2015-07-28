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
    parser.add_option( '-p', dest='projid', help='Project ID: Run or Project ID required')
    parser.add_option( '-r', dest='runid', help='Run ID: Run or Project ID required')
    parser.add_option( '-a', dest='accesstoken', help='Access Token: required')
    ( options, args ) = parser.parse_args()
   
    try:
       if (options.projid == None) == (options.runid == None):   # for bool is the equivalent of !(XOR)
             raise Exception
       if options.accesstoken == None:
	     raise Exception

    except Exception:
	    print("Usage: BaseSpaceFastqDownloader.py (-p <ProjectID> XOR -r <RunID>) -a <AccessToken>")
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
                if e.code in (400, 401, 402, 403, 404):
                  print "Exiting."
                  sys.exit()
		downloadrestrequest(rawrequest,name)


	except socket.error:
		print 'Got a socket error: retrying'
		outfile.close()
		downloadrestrequest(rawrequest,name)
		

options = arg_parser()

ProjID = options.projid
RunID = options.runid
AccessToken = options.accesstoken

if ProjID != None:
  request = 'http://api.basespace.illumina.com/v1pre3/projects/%s/samples?Limit=500&access_token=%s' %(ProjID,AccessToken)
elif RunID != None:
  request = 'http://api.basespace.illumina.com/v1pre3/runs/%s/samples?Limit=500&access_token=%s' %(RunID,AccessToken)

project_json_obj = restrequest(request)
nsamples = len(project_json_obj['Response']['Items'])

hreflist = []
namelist = []
samplenamelist = []
readtypelist = []

sample_dict = dict()

#
# For every sample ID, get a list of all the associated fastq files
#

for sampleindex in range(nsamples):
        SampleId = project_json_obj['Response']['Items'][sampleindex]['SampleId'] 
        PairedEnd = project_json_obj['Response']['Items'][sampleindex]['IsPairedEnd']

        if SampleId not in sample_dict:
          #
          # hreflist
          # namelist
          # readtypelist
          #
          sample_dict[SampleId] = [ list(), list(), list() ]

	Id = project_json_obj['Response']['Items'][sampleindex]['Id']
	request = 'https://api.basespace.illumina.com/v1pre3/samples/%s/files?access_token=%s' %(Id,AccessToken)
	sample_json_obj = restrequest(request)
        #print sample_json_obj
	nfiles = len(sample_json_obj['Response']['Items'])

        #print 'Paired End? %s'%(PairedEnd)

#
# TODO: Make this more object oriented so that it is clearer. Need to work out how to handle
# single end vs paired end reads. Also need to check to see what happens when there are 
# multiple files for a single library in a lane.
#

        if(PairedEnd):
		sample_dict[SampleId][0].append(sample_json_obj['Response']['Items'][0]['Href'])
		sample_dict[SampleId][1].append(sample_json_obj['Response']['Items'][0]['Name'])
                sample_dict[SampleId][2].append(1)
		sample_dict[SampleId][0].append(sample_json_obj['Response']['Items'][1]['Href'])
		sample_dict[SampleId][1].append(sample_json_obj['Response']['Items'][1]['Name'])
                sample_dict[SampleId][2].append(2)

print "Samples: \n%s" % ("\n".join(sample_dict.keys()))
for (sample, data) in sample_dict.iteritems():
    for fileindex in range(len(data[0])):
	request = 'http://api.basespace.illumina.com/%s/content?access_token=%s' % (data[0][fileindex], AccessToken)
	print 'downloading sample %s file %s'%(data[0][fileindex], data[1][fileindex]) 
	downloadrestrequest(request, data[1][fileindex])
