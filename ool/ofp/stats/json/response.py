from bpmappers import Mapper, RawField


class BaseResponse(object):
	def __init__(self, status, message):
		self.__status = status
		self.__message = message

class ResponseMapper(Mapper):
	status = RawField('status')
	message = RawField('message')

