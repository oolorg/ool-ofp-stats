from django.db import models

class Device(models.Model):
	dpid = models.CharField(max_length=255)
	sw_desc = models.CharField(max_length=255)
	hw_desc = models.CharField(max_length=255)
	dp_desc = models.CharField(max_length=255)
	serial_num = models.CharField(max_length=255)
	#serial_num = models.IntegerField()
	mfr_desc = models.CharField(max_length=255)

class PortStats(models.Model):
	device_id = models.ForeignKey(Device)
	date = models.DateTimeField()
	port_no = models.BigIntegerField()
	rx_bytes = models.BigIntegerField()
	rx_packets = models.BigIntegerField()
	rx_crc_err = models.BigIntegerField()
	rx_dropped = models.BigIntegerField()
	rx_errors = models.BigIntegerField()
	rx_frame_err = models.BigIntegerField()
	rx_over_err = models.BigIntegerField()
	tx_bytes = models.BigIntegerField()
	tx_packets = models.BigIntegerField()
	tx_dropped = models.BigIntegerField()
	tx_errors = models.BigIntegerField()
	collisions = models.BigIntegerField()
	duration_nsec = models.BigIntegerField()
	duration_sec = models.BigIntegerField()

class PortDescStats(models.Model):
	device_id = models.ForeignKey(Device)
	date = models.DateTimeField()
	port_no = models.BigIntegerField()
	name = models.CharField(max_length=255)
	hw_addr = models.CharField(max_length=255)
	config = models.BigIntegerField()
	state = models.BigIntegerField()
	curr = models.BigIntegerField()
	curr_speed = models.BigIntegerField()
	max_speed = models.BigIntegerField()
	peer = models.BigIntegerField()
	supported = models.BigIntegerField()
	advertised = models.BigIntegerField()

class FlowStats(models.Model):
	device_id = models.ForeignKey(Device)
	date = models.DateTimeField()
	flow_data = models.TextField()

