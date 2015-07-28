#!/usr/local/bin/python

from basespace_comm import BasespaceRestAPI
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

options = arg_parser()

project_id = options.projid
run_id = options.runid
access_token = options.accesstoken

bs = BasespaceRestAPI(access_token)

if project_id != None:
  print project_id
  json_sample_list = bs.project_request(project_id)
elif run_id != None:
  json_sample_list = bs.run_request(run_id)

print json_sample_list
nsamples = len(json_sample_list['Response']['Items'])

hreflist = []
namelist = []
samplenamelist = []
readtypelist = []

sample_dict = dict()

#
# For every sample ID, get a list of all the associated fastq files
#

for sampleindex in range(nsamples):
  file_id    = json_sample_list['Response']['Items'][sampleindex]['Id']
  sample_id  = json_sample_list['Response']['Items'][sampleindex]['SampleId']
  paired_end = json_sample_list['Response']['Items'][sampleindex]['IsPairedEnd']

  if sample_id not in sample_dict:
    #
    # hreflist
    # namelist
    # readtypelist
    #
    sample_dict[sample_id] = [ list(), list(), list() ]

    sample_json_obj = bs.file_list_request(file_id)
    nfiles = len(sample_json_obj['Response']['Items'])

#
# TODO: Make this more object oriented so that it is clearer. Need to work out how to handle
# single end vs paired end reads. Also need to check to see what happens when there are 
# multiple files for a single library in a lane.
#
    if paired_end:
      sample_dict[sample_id][0].append(sample_json_obj['Response']['Items'][0]['Href'])
      sample_dict[sample_id][1].append(sample_json_obj['Response']['Items'][0]['Name'])
      sample_dict[sample_id][2].append(1)
      sample_dict[sample_id][0].append(sample_json_obj['Response']['Items'][1]['Href'])
      sample_dict[sample_id][1].append(sample_json_obj['Response']['Items'][1]['Name'])
      sample_dict[sample_id][2].append(2)
  
print "Samples: \n%s" % ("\n".join(sample_dict.keys()))

for (sample, data) in sample_dict.iteritems():
  for fileindex in range(len(data[0])):
    print 'downloading %s' % data[1][fileindex]
    bs.file_request(data[0][fileindex], data[1][fileindex])
