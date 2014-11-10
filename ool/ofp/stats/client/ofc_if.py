"""
Created on 2014/11/4

@author: Shuya Nakama @ OOL
"""

import httplib2
import unirest
import json

from django.conf import settings
from oslo.config import cfg

from ool.ofp.stats.common import log

LOG = log.getLogger(__name__)

stats_opts = [
				cfg.StrOpt('ofc_url', default=''),
				cfg.StrOpt('ofc_desc_stats_url', default=''),
				cfg.StrOpt('ofc_port_stats_url', default=''),
				cfg.StrOpt('ofc_port_desc_stats_url', default=''),
				cfg.StrOpt('ofc_flow_stats_url', default='')
			]
stats_cfg = cfg.ConfigOpts()
stats_cfg.register_cli_opts(stats_opts)
stats_cfg(args=['--config-file', settings.BASE_DIR + '/stats/conf/stats.conf'])

class OfcClient:
	def __init__(self, base_url):
		self._base_url = base_url
	
	def ofc_desc_stats_request(self, req):
		header = {'Content-type':'application/json'}
		try:
			res = unirest.post(stats_cfg.ofc_url + stats_cfg.ofc_desc_stats_url, headers=header, params=req, callback=self.__http_response__)
		except e:
			LOG.exception(e.message)
		return res

	def ofc_port_stats_request(self, req):
		header = {'Content-type':'application/json'}
		try:
			res = unirest.post(stats_cfg.ofc_url + stats_cfg.ofc_port_stats_url, headers=header, params=req, callback=self.__http_response__)
		except e:
			LOG.exception(e.message)
		return res

	def ofc_port_desc_stats_request(self, req):
		header = {'Content-type':'application/json'}
		try:
			res = unirest.post(stats_cfg.ofc_url + stats_cfg.ofc_port_desc_stats_url, headers=header, params=req, callback=self.__http_response__)
		except e:
			LOG.exception(e.message)
		return res

	def ofc_flow_stats_request(self, req):
		header = {'Content-type':'application/json'}
		try:
			res = unirest.post(stats_cfg.ofc_url + stats_cfg.ofc_flow_stats_url, headers=header, params=req, callback=self.__http_response__)
		except e:
			LOG.exception(e.message)
		return res

	def __http_request__(self, url, method, header, body=None):
		LOG.debug(" : url = " + url + ", method = " + method + ", header = " + str(header) + ", body = " + str(body))

		resp, content = self._http_client.request(url, method, headers=header, body=body)
		LOG.info(' : Request Result = %s', str(content))
		return resp, content

	def __http_response__(self, res):
		LOG.info("Response status = " + str(res.code) + ", body = " + str(res.body))

