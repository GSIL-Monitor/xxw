from flask import jsonify


class MsgCode:
    MISSING_FIELD = "1004021011"  # 缺少数据字段
    DATA_TYPE_ERROR = "1004021012"  # 数据类型不匹配
    NOT_UNIQUE = "1004021013"  # 重复提交
    UNKNOWN = "1004021099"  # 未知错误
    SUCCESS = "0"  # 成功
    PARA_ERROR = "-1"  # 参数错误

    @classmethod
    def to_msg(cls, code):
        return _MAP[code]


_MAP = {
    MsgCode.MISSING_FIELD: "缺少数据字段",
    MsgCode.DATA_TYPE_ERROR: "数据类型不匹配",
    MsgCode.NOT_UNIQUE: "重复提交",
    MsgCode.SUCCESS: "成功",
    MsgCode.UNKNOWN: "未知错误",
    MsgCode.PARA_ERROR: "参数错误",
}


def MessageResponse(code=MsgCode.SUCCESS, msg=None, data=None):
    if not msg:
        msg = MsgCode.to_msg(code)
    return {"code": code, "msg": msg, "data": data}


def ListMessageResponse(current_page, page_size, page_total, code=MsgCode.SUCCESS, msg=None, data=""):
    if not msg:
        msg = MsgCode.to_msg(code)

    data["page"] = {"current_page": current_page, "page_size": page_size, "page_total": page_total}
    return {"code": code, "msg": msg, "data": data}


MESSAGE = {
    0: "成功",
    1014000000: '未知错误',
    1014010001: '参数错误, 参数缺失或类型错误',
    1014010002: '参数错误, 参数校验失败',
    1014010003: '参数错误, 未知参数',
    1014010004: "参数错误，参数传入不正确",
    1014020001: "数据库错误，数据库操作失败",
}
