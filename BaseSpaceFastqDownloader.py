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

print nsamples

hreflist = []
namelist = []

for sampleindex in range(nsamples):
  sample_id = json_sample_list['Response']['Items'][sampleindex]['Id']
  sample_json_obj = bs.file_list_request(sample_id)
  nfiles = len(sample_json_obj['Response']['Items'])

  for fileindex in range(nfiles):
    hreflist.append(sample_json_obj['Response']['Items'][fileindex]['Href'])
    namelist.append(sample_json_obj['Response']['Items'][fileindex]['Name'])

print "Downloading %s files" %(len(hreflist))
for index in range(len(hreflist)): 
  print 'downloading %s' %(namelist[index]) 
  bs.file_request(hreflist[index], namelist[index])
