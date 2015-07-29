import requests
import json
import sys

class BasespaceRestAPI:
  session = None
  json_params = dict()

  basespace_url = 'http://api.basespace.illumina.com'

  def __init__(self, access_token):
    self.session = requests.Session()
    self.session.params.update({'access_token': access_token})
    self.json_params.update({'Limit': 500})

  def __del__(self):
    self.session.close()

  def project_request(self, project_id):
    relative_addr = '/v1pre3/projects/%s/samples' % project_id
    return self._json_rest_request(relative_addr)

  def run_request(self, run_id):
    relative_addr = '/v1pre3/runs/%s/samples' % run_id
    return self._json_rest_request(relative_addr)

  def file_list_request(self, sample_id):
    relative_addr = '/v1pre3/samples/%s/files' % sample_id
    return self._json_rest_request(relative_addr)

  def file_request(self, name, files):
    self._file_download(files[0], name)
    for f in files[1::]:
      self._file_download(f, name, 'ab')
  
  def _file_download(self, file_id, name, mode = 'wb'):
    relative_addr = '/v1pre3/files/%s/content' % file_id
    try:
      response = self._rest_request(relative_addr)
    except requests.exceptions.Timeout, e:
      print "Timeout."
      self.file_request(relative_addr, name)
    with open(name, mode) as fd:
      for chunk in response.iter_content(1048576):
        fd.write(chunk)

  def _json_rest_request(self, relative_addr):
    try:
      response = self._rest_request(relative_addr, self.json_params)
      json_response = response.json()
    except ValueError, e:
      print 'JSON error: %s' % e
      sys.exit()
    return json_response

  def _rest_request(self, relative_addr, params = None):
    try:
      response = self.session.get(self.basespace_url + relative_addr, params=params, stream=True)
      response.raise_for_status()
    except requests.exceptions.HTTPError, e:
      print 'HTTP Error (%s): %s' % (response.url, e)
      sys.exit()
    return response
