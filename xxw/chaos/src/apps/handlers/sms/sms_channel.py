from flask_restful import Resource

from src.comm.sms_utils import SMSSender


class SMSChannelAPI(Resource):
    def get(self):
        return {"results": SMSSender.channel_list}
