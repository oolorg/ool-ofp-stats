"""
Created on 2014/10/20

@author: Shuya-Nakama@OOL
"""
import datetime
import json
import threading
import time
import datetime

from django.db import models as django_models
from django.db.models import Max
from django.conf import settings
from django.core import serializers
from django.utils import simplejson
from rest_framework.response import Response
from oslo.config import cfg

from ool.ofp.stats.common import log
from ool.ofp.stats.json.response import ResponseMapper, BaseResponse
from ool.ofp.stats.model.models import Device, PortStats, PortDescStats, FlowStats
from ool.ofp.stats.conf.define import OfpStatsDefine
from ool.ofp.stats.business.stats_request_business import StatsRequestThread
from ool.ofp.stats.client.ofc_if import OfcClient

stats_opts = [
				cfg.ListOpt('dpid',
						default=[])
				]
stats_cfg = cfg.ConfigOpts()
stats_cfg.register_cli_opts(stats_opts)
stats_cfg(args=['--config-file', settings.BASE_DIR + '/stats/conf/stats.conf'])

LOG = log.getLogger(__name__)

def encode_myway(obj):
	if isinstance(obj, django_models.Model):
		return obj.encode()
	elif isinstance(obj, QuerySet):
		return list(obj)
	else:
		raise TypeError(repr(obj) + " is not JSON serializable")

class StatsBusiness():
	
	#def __init__(self):

	th = None

	def stats_req_start(self):
		LOG.debug("stats_req_start()")
		self.th = StatsRequestThread()
		if self.th is None:
			LOG.error("thread is None")
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : thread is None")

		return Response(status=OfpStatsDefine.HTTP_STATUS_SUCCESS, data=OfpStatsDefine.SUCCESS_MSG)

	def stats_req_stop(self):
		LOG.debug("stats_req_stop()")
		if self.th is None:
			LOG.error("thread is None")
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : thread is None")

		self.th.stop()
		return Response(status=OfpStatsDefine.HTTP_STATUS_SUCCESS, data=OfpStatsDefine.SUCCESS_MSG)

	def stats_req(self, req):
		LOG.debug("stats_req()")
		
		ofc_client = OfcClient("")
		
		dpid = None
		if 'dpid' in req:
			dpid = str(hex(int(req['dpid'], 16)))
			LOG.debug("dpid = " + dpid)

		#for dp in stats_cfg.dpid:
		#	LOG.debug("dp = " + dp)

		if dpid is not None:
			if dpid not in stats_cfg.dpid:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : Bad dpid.")

			bodyData = {'dpid':dpid}
			body = json.dumps(bodyData, ensure_ascii=True, sort_keys=True)
			ofc_client.ofc_desc_stats_request(body)
			time.sleep(0.1)
			ofc_client.ofc_port_stats_request(body)
			time.sleep(0.1)
			ofc_client.ofc_port_desc_stats_request(body)
			time.sleep(0.1)
			ofc_client.ofc_flow_stats_request(body)
			time.sleep(0.1)	
		else:
			for datapath_id in stats_cfg.dpid:
				bodyData = {'dpid':datapath_id}
				body = json.dumps(bodyData, ensure_ascii=True, sort_keys=True)
				ofc_client.ofc_port_stats_request(body)
				time.sleep(0.1)
				ofc_client.ofc_port_desc_stats_request(body)
				time.sleep(0.1)
				ofc_client.ofc_flow_stats_request(body)
				time.sleep(0.1)

		return Response(status=OfpStatsDefine.HTTP_STATUS_SUCCESS, data=OfpStatsDefine.SUCCESS_MSG)

	def desc_stats(self, dpid):
		LOG.debug("desc_stats() dpid = " + str(dpid))
		res_data = None

		if dpid is not None:
			if dpid not in stats_cfg.dpid:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : Bad dpid.")

			dev = Device.objects.filter(dpid=dpid)
			device = {
					'dpid':str(dev[0].dpid),
					'sw_desc':str(dev[0].sw_desc),
					'hw_desc':dev[0].hw_desc,
					'dp_desc':dev[0].dp_desc,
					'serial_num':dev[0].serial_num,
					'mfr_desc':dev[0].mfr_desc
					}
			res_data = device;
		else:
			devlist = []
			#json_serializer = serializers.get_serializer("json")()
			for datapath_id in stats_cfg.dpid:
				dev = Device.objects.filter(dpid=datapath_id)
				device = {
						'dpid':str(dev[0].dpid),
						'sw_desc':str(dev[0].sw_desc),
						'hw_desc':dev[0].hw_desc,
						'dp_desc':dev[0].dp_desc,
						'serial_num':dev[0].serial_num,
						'mfr_desc':dev[0].mfr_desc
						}
				devlist.append(device)
				#LOG.debug(str(datapath_id))
				#LOG.debug("dev[" + datapath_id + "] = " + str(dev))

			LOG.debug("devlist = " + str(devlist))
			res_data = devlist

		return Response(status=OfpStatsDefine.HTTP_STATUS_SUCCESS, data=res_data)

	def port_stats(self, dpid):
		LOG.debug("port_stats() dpid = " + str(dpid))
		
		devlist = []

		if dpid is not None:
			if dpid not in stats_cfg.dpid:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : Bad dpid.")

			portlist = []
			date_time = PortStats.objects.filter(device__dpid = dpid).aggregate(Max('date'))
			port_list_data = PortStats.objects.filter(date=date_time["date__max"])#.values()
			for port in port_list_data:
				port_data = {
						'port_no' : port.port_no,
						'rx_bytes' : port.rx_bytes,
						'rx_packets' : port.rx_packets,
						'rx_crc_err' : port.rx_crc_err,
						'rx_dropped' : port.rx_dropped,
						'rx_errors' : port.rx_errors,
						'rx_frame_err' : port.rx_frame_err,
						'rx_over_err' : port.rx_over_err,
						'tx_bytes' : port.tx_bytes,
						'tx_packets' : port.tx_packets,
						'tx_dropped' : port.tx_dropped,
						'tx_errors' : port.tx_errors,
						'collisions' : port.collisions,
						'duration_nsec' : port.duration_nsec,
						'duration_sec' : port.duration_sec,
						'date' : port.date.strftime("%Y-%m-%d %H:%M:%S")
						}
				portlist.append(port_data)

			device = {
				'dpid' : dpid,
				'port_list' : portlist
				}

			devlist.append(device)

		else:
			for datapath_id in stats_cfg.dpid:
				LOG.debug(str(datapath_id))

				portlist = []
				date_time = PortStats.objects.filter(device__dpid = datapath_id).aggregate(Max('date'))
				port_list_data = PortStats.objects.filter(date=date_time["date__max"])#.values()
				for port in port_list_data:
					port_data = {
							'port_no' : port.port_no,
							'rx_bytes' : port.rx_bytes,
							'rx_packets' : port.rx_packets,
							'rx_crc_err' : port.rx_crc_err,
							'rx_dropped' : port.rx_dropped,
							'rx_errors' : port.rx_errors,
							'rx_frame_err' : port.rx_frame_err,
							'rx_over_err' : port.rx_over_err,
							'tx_bytes' : port.tx_bytes,
							'tx_packets' : port.tx_packets,
							'tx_dropped' : port.tx_dropped,
							'tx_errors' : port.tx_errors,
							'collisions' : port.collisions,
							'duration_nsec' : port.duration_nsec,
							'duration_sec' : port.duration_sec,
							'date' : port.date.strftime("%Y-%m-%d %H:%M:%S")
							}
					portlist.append(port_data)

				device = {
					'dpid' : datapath_id,
					'port_list' : portlist
					}

				devlist.append(device)

		res_data = json.dumps(devlist, ensure_ascii = False, sort_keys = True)#, indent=4)

		#LOG.debug(res_data)
		return Response(status=OfpStatsDefine.HTTP_STATUS_SUCCESS, data=res_data)

	def port_desc_stats(self, dpid):
		LOG.debug("port_desc_stats() dpid = " + str(dpid))
		
		devlist = []

		if dpid is not None:
			if dpid not in stats_cfg.dpid:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : Bad dpid.")

			port_desc_list = []
			date_time = PortDescStats.objects.filter(device__dpid = dpid).aggregate(Max('date'))
			port_desc_list_data = PortDescStats.objects.filter(date=date_time["date__max"])#.values()
			for port_desc in port_desc_list_data:
				port_desc_data = {
						'port_no' : port_desc.port_no,
						'name' : port_desc.name,
						'hw_addr' : port_desc.hw_addr,
						'config' : port_desc.config,
						'state' : port_desc.state,
						'curr' : port_desc.curr,
						'curr_speed' : port_desc.curr_speed,
						'max_speed' : port_desc.max_speed,
						'peer' : port_desc.peer,
						'supported' : port_desc.supported,
						'advertised' : port_desc.advertised,
						'date' : port_desc.date.strftime("%Y-%m-%d %H:%M:%S")
						}
				port_desc_list.append(port_desc_data)

			device = {
				'dpid' : dpid,
				'port_desc_list' : port_desc_list
				}

			devlist.append(device)

		else:
			for datapath_id in stats_cfg.dpid:
				LOG.debug(str(datapath_id))

				port_desc_list = []
				date_time = PortDescStats.objects.filter(device__dpid = datapath_id).aggregate(Max('date'))
				port_desc_list_data = PortDescStats.objects.filter(date=date_time["date__max"])#.values()
				for port_desc in port_desc_list_data:
					port_desc_data = {
							'port_no' : port_desc.port_no,
							'name' : port_desc.name,
							'hw_addr' : port_desc.hw_addr,
							'config' : port_desc.config,
							'state' : port_desc.state,
							'curr' : port_desc.curr,
							'curr_speed' : port_desc.curr_speed,
							'max_speed' : port_desc.max_speed,
							'peer' : port_desc.peer,
							'supported' : port_desc.supported,
							'advertised' : port_desc.advertised,
							'date' : port_desc.date.strftime("%Y-%m-%d %H:%M:%S")
							}
					port_desc_list.append(port_desc_data)

				device = {
					'dpid' : datapath_id,
					'port_desc_list' : port_desc_list
					}

				devlist.append(device)

		res_data = json.dumps(devlist, ensure_ascii = False, sort_keys = True)#, indent=4)

		#LOG.debug(res_data)
		return Response(status=OfpStatsDefine.HTTP_STATUS_SUCCESS, data=res_data)

	def flow_stats(self, dpid):
		LOG.debug("flow_stats() dpid = " + str(dpid))
		
		devlist = []

		if dpid is not None:
			if dpid not in stats_cfg.dpid:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : Bad dpid.")

			flow_list = []
			date_time = FlowStats.objects.filter(device__dpid = dpid).aggregate(Max('date'))
			flow_list_data = FlowStats.objects.filter(date=date_time["date__max"])#.values()
			for flow in flow_list_data:
				flow_data = {
						'flow_data' : json.loads(flow.flow_data),
						'date' : flow.date.strftime("%Y-%m-%d %H:%M:%S")
						}
				flow_list.append(flow_data)

			device = {
				'dpid' : dpid,
				'flow_list' : flow_list
				}

			devlist.append(device)

		else:
			for datapath_id in stats_cfg.dpid:
				LOG.debug(str(datapath_id))


				devlist.append(device)

		res_data = str(json.dumps(devlist, ensure_ascii = False, sort_keys = True))#, indent=4)

		LOG.debug(res_data)
		return Response(status=OfpStatsDefine.HTTP_STATUS_SUCCESS, data=res_data)

	def set_desc_stats(self, req):
		dpid = None
		if 'dpid' in req:
			dpid = req['dpid']#int(req['dpid'], 16)
			if dpid is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : dpid is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : dpid is nothing")

		OFPDescStatsReply = None
		if 'OFPDescStatsReply' in req:
			OFPDescStatsReply = req['OFPDescStatsReply']
			if OFPDescStatsReply is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPDescStatsReply is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPDescStatsReply is nothing")

		body = None
		if 'body' in OFPDescStatsReply:
			body = OFPDescStatsReply['body']
			if body is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : body is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : body is nothing")

		OFPDescStats = None
		if 'OFPDescStats' in body:
			OFPDescStats = body['OFPDescStats']
			if OFPDescStats is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPDescStats is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPDescStats is nothing")

		sw_desc = None
		if 'sw_desc' in OFPDescStats:
			sw_desc = OFPDescStats['sw_desc']
			if sw_desc is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : sw_desc is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : sw_desc is nothing")

		hw_desc = None
		if 'hw_desc' in OFPDescStats:
			hw_desc = OFPDescStats['hw_desc']
			if hw_desc is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : hw_desc is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : hw_desc is nothing")

		dp_desc = None
		if 'dp_desc' in OFPDescStats:
			dp_desc = OFPDescStats['dp_desc']
			if dp_desc is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : dp_desc is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : dp_desc is nothing")

		serial_num = None
		if 'serial_num' in OFPDescStats:
			serial_num = OFPDescStats['serial_num']
			if serial_num is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : serial_num is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : serial_num is nothing")

		mfr_desc = None
		if 'mfr_desc' in OFPDescStats:
			mfr_desc = OFPDescStats['mfr_desc']
			if mfr_desc is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : mfr_desc is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : mfr_desc is nothing")

		try:
			dev = Device.objects.filter(dpid=dpid)
			if dev:
				dev.update(sw_desc = sw_desc,
						hw_desc = hw_desc,
						dp_desc = dp_desc,
						serial_num = serial_num,
						mfr_desc = mfr_desc)
			else:
				dev = Device(dpid = dpid,
						sw_desc = sw_desc,
						hw_desc = hw_desc,
						dp_desc = dp_desc,
						serial_num = serial_num,
						mfr_desc = mfr_desc)
				dev.save()

		except Exception as e:
			LOG.exception(e.message)
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : exception")

		#LOG.debug('request: %s' % str(req))
		return Response(status=OfpStatsDefine.HTTP_STATUS_SUCCESS, data=OfpStatsDefine.SUCCESS_MSG)

	def set_port_stats(self, req):
		date = datetime.datetime.now()

		dpid = None
		if 'dpid' in req:
			dpid = str(hex(int(req['dpid'], 16)))
			if dpid is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : dpid is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : dpid is nothing")

		OFPPortStatsReply = None
		if 'OFPPortStatsReply' in req:
			OFPPortStatsReply = req['OFPPortStatsReply']
			if OFPPortStatsReply is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPPortStatsReply is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPPortStatsReply is nothing")

		body = None
		if 'body' in OFPPortStatsReply:
			body = OFPPortStatsReply['body']
			if body is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : body is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : body is nothing")
	
		for PortStats in body:
			OFPPortStats = None
			if 'OFPPortStats' in PortStats:
				OFPPortStats = PortStats['OFPPortStats']
				if OFPPortStats is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPPortStats is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPPortStats is nothing")
			
			port_no = None
			if 'port_no' in OFPPortStats:
				port_no = OFPPortStats['port_no']
				if port_no is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : port_no is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : port_no is nothing")

			rx_bytes = None
			if 'rx_bytes' in OFPPortStats:
				rx_bytes = OFPPortStats['rx_bytes']
				if rx_bytes is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_bytes is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_bytes is nothing")

			rx_packets = None
			if 'rx_packets' in OFPPortStats:
				rx_packets = OFPPortStats['rx_packets']
				if rx_packets is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_packets is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_packets is nothing")

			rx_crc_err = None
			if 'rx_crc_err' in OFPPortStats:
				rx_crc_err = OFPPortStats['rx_crc_err']
				if rx_crc_err is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_crc_err is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_crc_err is nothing")

			rx_dropped = None
			if 'rx_dropped' in OFPPortStats:
				rx_dropped = OFPPortStats['rx_dropped']
				if rx_dropped is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_dropped is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_dropped is nothing")

			rx_errors = None
			if 'rx_errors' in OFPPortStats:
				rx_errors = OFPPortStats['rx_errors']
				if rx_errors is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_errors is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_errors is nothing")

			rx_frame_err = None
			if 'rx_frame_err' in OFPPortStats:
				rx_frame_err = OFPPortStats['rx_frame_err']
				if rx_frame_err is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_frame_err is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_frame_err is nothing")

			rx_over_err = None
			if 'rx_over_err' in OFPPortStats:
				rx_over_err = OFPPortStats['rx_over_err']
				if rx_over_err is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_over_err is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : rx_over_err is nothing")

			tx_bytes = None
			if 'tx_bytes' in OFPPortStats:
				tx_bytes = OFPPortStats['tx_bytes']
				if tx_bytes is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : tx_bytes is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : tx_bytes is nothing")

			tx_packets = None
			if 'tx_packets' in OFPPortStats:
				tx_packets = OFPPortStats['tx_packets']
				if tx_packets is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : tx_packets is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : tx_packets is nothing")

			tx_dropped = None
			if 'tx_dropped' in OFPPortStats:
				tx_dropped = OFPPortStats['tx_dropped']
				if tx_dropped is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : tx_dropped is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : tx_dropped is nothing")

			tx_errors = None
			if 'tx_errors' in OFPPortStats:
				tx_errors = OFPPortStats['tx_errors']
				if tx_errors is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : tx_errors is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : tx_errors is nothing")

			collisions = None
			if 'collisions' in OFPPortStats:
				collisions = OFPPortStats['collisions']
				if collisions is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : collisions is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : collisions is nothing")

			duration_nsec = None
			if 'duration_nsec' in OFPPortStats:
				duration_nsec = OFPPortStats['duration_nsec']
				if duration_nsec is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : duration_nsec is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : duration_nsec is nothing")

			duration_sec = None
			if 'duration_sec' in OFPPortStats:
				duration_sec = OFPPortStats['duration_sec']
				if duration_sec is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : duration_sec is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : duration_sec is nothing")

			try:
				dev = Device.objects.get(dpid=dpid)
				if dev:
					port = dev.portstats_set.create(
								date = date,
								port_no = int(port_no),
								rx_bytes = int(rx_bytes),
								rx_packets = int(rx_packets),
								rx_crc_err = int(rx_crc_err),
								rx_dropped = int(rx_dropped),
								rx_errors = int(rx_errors),
								rx_frame_err = int(rx_frame_err),
								rx_over_err = int(rx_over_err),
								tx_bytes = int(tx_bytes),
								tx_packets = int(tx_packets),
								tx_dropped = int(tx_dropped),
								tx_errors = int(tx_errors),
								collisions = int(collisions),
								duration_nsec = int(duration_nsec),
								duration_sec = int(duration_sec))
					#port.save()
				else:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : Device not found.")

			except Exception as e:
				LOG.exception(e.message)
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : exception")

		return Response(status=OfpStatsDefine.HTTP_STATUS_SUCCESS, data=OfpStatsDefine.SUCCESS_MSG)

	def set_port_desc_stats(self, req):
		date = datetime.datetime.now()

		dpid = None
		if 'dpid' in req:
			#dpid = int(req['dpid'], 16)
			dpid = str(hex(int(req['dpid'], 16)))
			if dpid is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : dpid is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : dpid is nothing")

		OFPPortDescStatsReply = None
		if 'OFPPortDescStatsReply' in req:
			OFPPortDescStatsReply = req['OFPPortDescStatsReply']
			if OFPPortDescStatsReply is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPPortDescStatsReply is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPPortDescStatsReply is nothing")

		body = None
		if 'body' in OFPPortDescStatsReply:
			body = OFPPortDescStatsReply['body']
			if body is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : body is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : body is nothing")
	
		for PortDescStats in body:
			OFPPort = None
			if 'OFPPort' in PortDescStats:
				OFPPort = PortDescStats['OFPPort']
				if OFPPort is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPPort is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPPort is nothing")
			
			port_no = None
			if 'port_no' in OFPPort:
				port_no = int(OFPPort['port_no'])
				if port_no is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : port_no is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : port_no is nothing")
				
			name = None
			if 'name' in OFPPort:
				name = OFPPort['name']
				if name is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : name is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : name is nothing")

			hw_addr = None
			if 'hw_addr' in OFPPort:
				hw_addr = OFPPort['hw_addr']
				if name is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : hw_addr is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : hw_addr is nothing")

			config = None
			if 'config' in OFPPort:
				config = int(OFPPort['config'])
				if config is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : config is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : config is nothing")

			state = None
			if 'state' in OFPPort:
				state = int(OFPPort['state'])
				if state is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : state is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : state is nothing")

			curr = None
			if 'curr' in OFPPort:
				curr = int(OFPPort['curr'])
				if curr is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : curr is nothing")

			curr_speed = None
			if 'curr_speed' in OFPPort:
				curr_speed = int(OFPPort['curr_speed'])
				if curr_speed is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : curr_speed is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : curr_speed is nothing")

			max_speed = None
			if 'max_speed' in OFPPort:
				max_speed = int(OFPPort['max_speed'])
				if max_speed is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : max_speed is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : max_speed is nothing")

			peer = None
			if 'peer' in OFPPort:
				peer = int(OFPPort['peer'])
				if peer is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : peer is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : peer is nothing")

			supported = None
			if 'supported' in OFPPort:
				supported = int(OFPPort['supported'])
				if port_no is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : supported is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : supported is nothing")

			advertised = None
			if 'advertised' in OFPPort:
				advertised = int(OFPPort['advertised'])
				if advertised is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : advertised is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : advertised is nothing")

			try:
				dev = Device.objects.get(dpid=dpid)
				if dev:
					port_desc_stats = dev.portdescstats_set.create(
								date = date,
								port_no = port_no,
								name = name,
								hw_addr = hw_addr,
								config = config,
								state = state,
								curr = curr,
								curr_speed = curr_speed,
								max_speed = max_speed,
								peer = peer,
								supported = supported,
								advertised = advertised)
				else:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : Device not found.")
			
			except Exception as e:
				LOG.exception(e.message)
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : exception")

		#LOG.debug()
		return Response(status=OfpStatsDefine.HTTP_STATUS_SUCCESS, data=OfpStatsDefine.SUCCESS_MSG)

	def set_flow_stats(self, req):
		date = datetime.datetime.now()

		dpid = None
		if 'dpid' in req:
			#dpid = int(req['dpid'], 16)
			dpid = str(hex(int(req['dpid'], 16)))
			if dpid is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : dpid is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : dpid is nothing")

		OFPFlowStatsReply = None
		if 'OFPFlowStatsReply' in req:
			OFPFlowStatsReply = req['OFPFlowStatsReply']
			if OFPFlowStatsReply is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPFlowStatsReply is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPFlowStatsReply is nothing")

		body = None
		if 'body' in OFPFlowStatsReply:
			body = OFPFlowStatsReply['body']
			if body is None:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : body is None")
		else:
			return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : body is nothing")

		for FlowStats in body:
			OFPFlowStats = None
			if 'OFPFlowStats' in FlowStats:
				OFPFlowStats = FlowStats['OFPFlowStats']
				if OFPFlowStats is None:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPFlowStats is None")
			else:
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : OFPFlowStats is nothing")
			
			flow_data = json.dumps(OFPFlowStats, ensure_ascii=True, sort_keys=True)

			try:
				dev = Device.objects.get(dpid=dpid)
				if dev:
					flow = dev.flowstats_set.create(
								date = date,
								flow_data = flow_data)
				else:
					return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : Device not found.")

			except Exception as e:
				LOG.exception(e.message)
				return Response(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data= OfpStatsDefine.ERR_MSG_BAD_REQUEST + " : exception")

		return Response(status=OfpStatsDefine.HTTP_STATUS_SUCCESS, data=OfpStatsDefine.SUCCESS_MSG)


class StatsDesc():
	def __init__(self):
		pass


