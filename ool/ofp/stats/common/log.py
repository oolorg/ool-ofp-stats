import logging
#import logging.config import logging.handlers
import os
import traceback

from oslo.config import cfg

log_opts = [
				cfg.StrOpt('logging_default_format_string',
						default='%(asctime)s.%(msecs)03d %(process)d [%(levelname)s] '
								'%(name)s [-] %(message)s'),
				cfg.StrOpt('logging_debug_format_suffix',
						default='%(funcName)s %(pathname)s:%(lineno)d'),
				cfg.BoolOpt('debug',default='True'),
				cfg.StrOpt('log_dir',default='/var/log/ool-ofp-stats'),
				cfg.StrOpt('log_file',default='ofp-stats.log'),
				cfg.StrOpt('logging_level',default='debug'),
]

CONF = cfg.CONF
CONF.register_opts(log_opts)

def _get_log_file_path():
	logfile = CONF.log_file
	logdir = CONF.log_dir

	if logfile and not logdir:
		return logfile

	if logfile and logdir:
		return os.path.join(logdir, logfile)

	return None

def _set_logger_cfg(log_root):
	_fmt = CONF.logging_default_format_string
	if (CONF.debug and CONF.logging_debug_format_suffix):
		_fmt += ' ' + CONF.logging_debug_format_suffix
	logpath = _get_log_file_path()
	if logpath:
		filelog = logging.handlers.WatchedFileHandler(logpath)
		filelog.setFormatter(logging.Formatter(fmt=_fmt))
		log_root.addHandler(filelog)
	if CONF.debug:
		log_root.setLevel(logging.DEBUG)
	elif CONF.verbose:
		log_root.setLevel(logging.INFO)
	else:
		log_root.setLevel(logging.WARNING)
	return log_root

def getLogger(name='ncs'):
	return _set_logger_cfg(logging.getLogger(name))

