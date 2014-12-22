"""
Created on 2014/10/20

@author: Shuya-Nakama@OOL
"""

import json
from oslo.config import cfg

from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.decorators import renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.conf import settings
from oslo.config import cfg

from ool.ofp.stats.business.stats_business import StatsBusiness
from ool.ofp.stats.common import log
from ool.ofp.stats.conf.define import OfpStatsDefine
from ool.ofp.stats.client.ofc_if import OfcClient

stats_opts = [
				cfg.ListOpt('dpid',
						default=[])
				]
stats_cfg = cfg.ConfigOpts()
stats_cfg.register_cli_opts(stats_opts)
stats_cfg(args=['--config-file', settings.BASE_DIR + '/stats/conf/stats.conf'])

LOG = log.getLogger(__name__)
biz = StatsBusiness()

@api_view(['POST'])
@parser_classes((JSONParser,))
@renderer_classes((JSONRenderer,))
def set_desc_stats(request, path=None):
	x = Response(status=OfpStatsDefine.HTTP_STATUS_INTL_SRV_ERR, data=OfpStatsDefine.ERR_MSF_INT_SRV_ERR)
	try:
		req = json.loads(request.body)
	except ValueError as e:
		LOG.exception(e.message)
		return Respinse(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data=OfpStatsDefine.ERR_MSG_BAD_REQUEST)

	try:
		x = biz.set_desc_stats(req)
	except Exception as e:
		LOG.exception(e.message)
	return x

@api_view(['POST'])
@parser_classes((JSONParser,))
@renderer_classes((JSONRenderer,))
def set_port_stats(request, path=None):
	x = Response(status=OfpStatsDefine.HTTP_STATUS_INTL_SRV_ERR, data=OfpStatsDefine.ERR_MSF_INT_SRV_ERR)
	try:
		req = json.loads(request.body)
	except ValueError as e:
		LOG.exception(e.message)
		return Respinse(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data=OfpStatsDefine.ERR_MSG_BAD_REQUEST)

	try:
		x = biz.set_port_stats(req)
	except Exception as e:
		LOG.exception(e.message)

	return x

@api_view(['POST'])
@parser_classes((JSONParser,))
@renderer_classes((JSONRenderer,))
def set_port_desc_stats(request, path=None):
	x = Response(status=OfpStatsDefine.HTTP_STATUS_INTL_SRV_ERR, data=OfpStatsDefine.ERR_MSF_INT_SRV_ERR)
	try:
		req = json.loads(request.body)
	except ValueError as e:
		LOG.exception(e.message)
		return Respinse(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data=OfpStatsDefine.ERR_MSG_BAD_REQUEST)

	try:
		x = biz.set_port_desc_stats(req)
	except Exception as e:
		LOG.exception(e.message)
	return x

@api_view(['POST'])
@parser_classes((JSONParser,))
@renderer_classes((JSONRenderer,))
def set_flow_stats(request, path=None):
	x = Response(status=OfpStatsDefine.HTTP_STATUS_INTL_SRV_ERR, data=OfpStatsDefine.ERR_MSF_INT_SRV_ERR)
	try:
		req = json.loads(request.body)
	except ValueError as e:
		LOG.exception(e.message)
		return Respinse(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data=OfpStatsDefine.ERR_MSG_BAD_REQUEST)

	try:
		x = biz.set_flow_stats(req)
	except Exception as e:
		LOG.exception(e.message)
	return x

@api_view(['GET'])
def datapathid_list(request, path=None):
	body = {'dpid':stats_cfg.dpid}
	x = Response(status=OfpStatsDefine.HTTP_STATUS_SUCCESS, data=body)
	return x

@api_view(['POST'])
@parser_classes((JSONParser,))
@renderer_classes((JSONRenderer,))
def stats_req(request, path=None):
	x = Response(status=OfpStatsDefine.HTTP_STATUS_INTL_SRV_ERR, data=OfpStatsDefine.ERR_MSF_INT_SRV_ERR)
	try:
		req = json.loads(request.body)
	except ValueError as e:
		LOG.exception(e.message)
		return Respinse(status=OfpStatsDefine.HTTP_STATUS_BAD_REQUEST, data=OfpStatsDefine.ERR_MSG_BAD_REQUEST)
	
	try:
		x = biz.stats_req(req)
	except Exception as e:
		LOG.exception(e.message)
	return x

@api_view(['GET'])
def desc(request, dpid=None):
	x = Response(status=OfpStatsDefine.HTTP_STATUS_INTL_SRV_ERR, data=OfpStatsDefine.ERR_MSF_INT_SRV_ERR)
	try:
		x = biz.desc_stats(dpid)
	except Exception as e:
		LOG.exception(e.message)
	return x

@api_view(['GET'])
def port(request, dpid=None):
	x = Response(status=OfpStatsDefine.HTTP_STATUS_INTL_SRV_ERR, data=OfpStatsDefine.ERR_MSF_INT_SRV_ERR)
	try:
		x = biz.port_stats(dpid)
	except Exception as e:
		LOG.exception(e.message)
	return x

@api_view(['GET'])
def port_desc(request, dpid=None):
	x = Response(status=OfpStatsDefine.HTTP_STATUS_INTL_SRV_ERR, data=OfpStatsDefine.ERR_MSF_INT_SRV_ERR)
	try:
		x = biz.port_desc_stats(dpid)
	except Exception as e:
		LOG.exception(e.message)
	return x

@api_view(['GET'])
def flow(request, dpid=None):
	x = Response(status=OfpStatsDefine.HTTP_STATUS_INTL_SRV_ERR, data=OfpStatsDefine.ERR_MSF_INT_SRV_ERR)
	try:
		x = biz.flow_stats(dpid)
	except Exception as e:
		LOG.exception(e.message)
	return x

@api_view(['POST'])
@parser_classes((JSONParser,))
@renderer_classes((JSONRenderer,))
def stats_req_start(request, path=None):
	x = Response(status=OfpStatsDefine.HTTP_STATUS_INTL_SRV_ERR, data=OfpStatsDefine.ERR_MSF_INT_SRV_ERR)
	try:
		x = biz.stats_req_start()
	except Exception as e:
		LOG.exception(e.message)
	return x

@api_view(['POST'])
@parser_classes((JSONParser,))
@renderer_classes((JSONRenderer,))
def stats_req_stop(request, path=None):
	x = Response(status=OfpStatsDefine.HTTP_STATUS_INTL_SRV_ERR, data=OfpStatsDefine.ERR_MSF_INT_SRV_ERR)
	try:
		x = biz.stats_req_stop()
	except Exception as e:
		LOG.exception(e.message)
	return x

