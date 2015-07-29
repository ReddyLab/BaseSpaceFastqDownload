import json
import hashlib
import itertools

class BasespaceFile:
  content_type = None
  date_created = None
  href = None
  href_content = None
  uid = None 
  name = None
  path = None
  size = None
  readnum = None
  
  def __init__(self, json_dict):
    self.content_type = json_dict['ContentType']
    self.date_created = json_dict['DateCreated']
    self.href = json_dict['Href']
    self.href_content = json_dict['HrefContent']
    self.uid  = json_dict['Id']
    self.name = json_dict['Name']
    self.path = json_dict['Path']
    self.size = json_dict['Size']

  def __str__(self):
    return self.uid


class BasespaceSample:
  date_created = None
  experiment_name = None
  href = None
  uid = None
  is_merged = None
  is_paired_end = None
  name = None
  num_reads_PF = None
  num_reads_raw = None
  read_1 = None
  read_2 = None
  sample_id = None
  status = None
  status_summary = None
  total_clusters_PF = None
  total_clusters_raw = None
  total_reads_PF = None
  total_reads_raw = None
  total_size = None

  read_1_files = None
  read_2_files = None
  
  def __init__(self, json_dict): 
    self.date_created = json_dict['DateCreated']
    self.experiment_name = json_dict['ExperimentName']
    self.href = json_dict['Href']
    self.uid = json_dict['Id']
    self.is_merged = json_dict['IsMerged']
    self.is_paired_end = json_dict['IsPairedEnd']
    self.name = json_dict['Name']
    self.num_reads_PF = json_dict['NumReadsPF']
    self.num_reads_raw = json_dict['NumReadsRaw']
    self.read_1 = json_dict['Read1']
    self.read_2 = json_dict['Read2']
    self.sample_id = json_dict['SampleId']
    self.status = json_dict['Status']
    self.status_summary = json_dict['StatusSummary']
    self.total_clusters_PF = json_dict['TotalClustersPF']
    self.total_clusters_raw = json_dict['TotalClustersRaw']
    self.total_reads_PF = json_dict['TotalReadsPF']
    self.total_reads_raw = json_dict['TotalReadsRaw']
    self.total_size = json_dict['TotalSize']
    self.used_owned_by = json_dict['UserOwnedBy']

  def __str__(self):
    return '%s: uid = %s, href = %s' % (self.sample_id, self.uid, self.href)

  def set_files(self, json_file_dict):
    items = json_file_dict['Response']['Items']
    if self.is_paired_end and len(items) % 2 == 1:
      raise ValueError("Sample is paired end but and odd number of files was provided")

    files = [BasespaceFile(x) for x in items]

    #
    # Assuming that sequential files are read1:read2 pairs
    #
    if self.is_paired_end:
      self.read_1_files = files[::2]
      self.read_2_files = files[1::2]
    else:
      self.read_1_files = files

  def files(self):
    for i in range(self.read_1_files):
      if self.is_paired_end: 
        yield (read1[i], read2[i])
      else:
        yield read1[i]

class BasespaceSampleList:
  sample_id = None
  is_paired_end = None
  num_reads_PF = 0
  num_reads_raw = 0
  total_clusters_PF = 0
  total_clusters_raw = 0
  total_reads_PF = 0
  total_reads_raw = 0
  total_size = 0

  read_1_files = None
  read_2_files = None

  def __init__(self, sample_id, paired_end):
    self.sample_id = sample_id
    self.is_paired_end = paired_end
    self.num_reads_PF = 0
    self.num_reads_raw = 0
    self.total_clusters_PF = 0
    self.total_clusters_raw = 0
    self.total_reads_PF = 0
    self.total_reads_raw = 0
    self.total_size = 0

    self.read_1_files = list();
    self.read_2_files = list();

  def add_sample(self, sample):
    if self.sample_id != sample.sample_id:
      raise ValueError('Error: samples have mismatched id. Expecting %s, got %s' % (self.sample_id, sample.sample_id))

    if self.is_paired_end != sample.is_paired_end:
      raise ValueError('Error: samples have read pairing. Expecting %s, got %s' % (self.is_paired_end, sample.is_paired_end))

    self.num_reads_PF        += sample.num_reads_PF
    self.num_reads_raw       += sample.num_reads_raw
    self.total_clusters_PF   += sample.total_clusters_PF
    self.total_clusters_raw  += sample.total_clusters_raw
    self.total_reads_PF      += sample.total_reads_PF
    self.total_reads_raw     += sample.total_reads_raw
    self.total_size          += sample.total_size

    self.read_1_files.extend(sample.read_1_files)
    self.read_2_files.extend(sample.read_2_files)
