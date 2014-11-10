"""
Created on 2014/11/4

@author: Shuya Nakama @ OOL
"""
import threading
import time
import datetime
import json

from django.conf import settings

from ool.ofp.stats.client.ofc_if import OfcClient
from ool.ofp.stats.common import log
from oslo.config import cfg

stats_opts = [
				cfg.ListOpt('dpid',
						default=[]),
				cfg.IntOpt('req_interval_time',
						default=60)
				]
stats_cfg = cfg.ConfigOpts()
stats_cfg.register_cli_opts(stats_opts)
stats_cfg(args=['--config-file', settings.BASE_DIR + '/stats/conf/stats.conf'])

LOG = log.getLogger(__name__)

class StatsRequestThread():
	
	thread = None

	def __init__(self):
		self.stop_event = threading.Event()

		self.thread = threading.Thread(target = self.target)
		self.thread.setDaemon(True)
		self.thread.start()

	def target(self):
		ofc_client = OfcClient("")
		for dpid in stats_cfg.dpid: 
			bodyData = {'dpid':dpid}
			body = json.dumps(bodyData, ensure_ascii=True, sort_keys=True)
			ofc_client.ofc_desc_stats_request(body)
			LOG.debug("ofc_client.ofc_desc_stats_request(" +  body + ")")
		while not self.stop_event.is_set():
			for dpid in stats_cfg.dpid: 
				bodyData = {'dpid':dpid}
				body = json.dumps(bodyData, ensure_ascii=True, sort_keys=True)
				ofc_client.ofc_port_stats_request(body)
				time.sleep(0.1)
				ofc_client.ofc_port_desc_stats_request(body)
				time.sleep(0.1)
				ofc_client.ofc_flow_stats_request(body)
				time.sleep(0.1)

			for i in range(stats_cfg.req_interval_time):
				time.sleep(1)
				if self.stop_event.is_set():
					break

	def stop(self):
		self.stop_event.set()
		self.thread.join()
