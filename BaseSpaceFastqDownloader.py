#!/usr/local/bin/python

from basespace_comm import BasespaceRestAPI
from basespace_sample_list import BasespaceFile,BasespaceSample,BasespaceSampleList
from collections import defaultdict
import json
import pprint
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


pp = pprint.PrettyPrinter(indent=4)
options = arg_parser()

project_id = options.projid
run_id = options.runid
access_token = options.accesstoken

bs = BasespaceRestAPI(access_token)

if project_id != None:
  json_sample_list = bs.project_request(project_id)
elif run_id != None:
  json_sample_list = bs.run_request(run_id)

bs_samples = dict()
for x in json_sample_list['Response']['Items']:
  sample = BasespaceSample(x)
  sample.set_files(bs.file_list_request(sample.uid))

  if sample.sample_id not in bs_samples:
    bsl = BasespaceSampleList(sample.sample_id, sample.is_paired_end)
    bs_samples[sample.sample_id] = bsl

  bs_samples[sample.sample_id].add_sample(sample)
   
#
# For every sample ID, get a list of all the associated fastq files
#
for sample_id, sample_list in bs_samples.iteritems():
  print "Downloading %s (%s and %s files for read1 and read2)" % (sample_id, len(sample_list.read_1_files), len(sample_list.read_2_files))
  read1_filename = '%s_R1.fastq.gz' % sample_id;
  read2_filename = '%s_R2.fastq.gz' % sample_id;
  
  bs.file_request(read1_filename, sample_list.read_1_files)
  bs.file_request(read2_filename, sample_list.read_2_files)
