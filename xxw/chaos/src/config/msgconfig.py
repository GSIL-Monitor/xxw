#!usr/bin/env python
# coding=utf-8
"""
@author: holens
@time: 2018/09/02
@desc: 业务错误日志统一配置
"""


class Msg:
    # 通用状态码——成功类型(0 ~ 9999)
    SUCCESS = 0
    # 错误码统一 1016 开头
    # 通用状态码——失败类型(10161 开头)
    ERROR = 1016110000
    PARAMS_ERROR = 1016110002
    UNKNOW_ERROR = 1016110001

    # CHAOS公共错误码 101600
    VALIDATE_ERROR = 1016000101
    TYPE_CONVERT_ERROR = 1016000102
    METHOD_NOT_ALLOW = 1016000103
    FIELD_TYPE_ERROR = 1016000104
    INSTANCE_IS_EXIST = 1016000105
    DB_COMMIT_ERROR = 1016000106
    NOT_ALLOW_UPDATE_FIELD_IS_EXIST = 1016000107
    REQUIRED_FIELD_NOT_EXIST = 1016000108
    INSTANCE_IS_NOT_EXIST = 1016000109

    # 短信服务-验证码 101601
    SMS_REPEAT_SEND = 1016010101
    SMS_VERIFY_CODE_NOT_MATCH = 1016010102
    SMS_SEND_FAIL = 1016010103

    # 短信服务-通道商管理 101602

    # 短信服务-应用管理 101603
    SMS_APP_DEPENDENT_DELETE = 1016030010

    # 短信服务-应用模板管理 101604
    SMS_APP_TEMP_DEPENDENT_DELETE = 1016040010

    # 短信服务-业务模板管理 101605
    SMS_BUSSINESS_APP_TEMPLATE_IS_NOT_EXIST = 1016050101
    SMS_BUSSINESS_TEMPLATE_IS_EXIST = 1016050102

    # 短信服务-模板类型管理 101606

    # 短信服务-短信流水管理 101607

    # 短信服务-短信发送 101608
    SMS_SENDER_BUSS_TEMPLATE_NOT_EXIST = 1016080101
    SMS_SENDER_APP_TEMPLATE_NOT_EXIST = 1016080102
    SMS_SENDER_CONFIG_NOT_EXIST = 1016080103
    SMS_SENDER_FAILED = 1016080104

    # ip归属地服务 101609
    ERRPR_IP_NUMBER = 1016090101
    # 手机归属地服务 101610
    ERROR_PHONE_NUMBER = 1016100101

    msg = {
        SUCCESS: "成功",
        ERROR: "失败",
        PARAMS_ERROR: "参数错误",
        UNKNOW_ERROR: "未知错误",
        # CHAOS公共错误码
        VALIDATE_ERROR: "字段未通过验证",
        TYPE_CONVERT_ERROR: "目标类型不能转换",
        METHOD_NOT_ALLOW: "不支持该请求",
        FIELD_TYPE_ERROR: "字段类型错误",
        INSTANCE_IS_EXIST: "已存在该记录",
        DB_COMMIT_ERROR: "数据存储失败",
        NOT_ALLOW_UPDATE_FIELD_IS_EXIST: "存在不允许更新字段",
        REQUIRED_FIELD_NOT_EXIST: "缺少必要字段",
        INSTANCE_IS_NOT_EXIST: "不存在该记录",
        # 短信服务-验证码
        SMS_REPEAT_SEND: "重复发送",
        SMS_VERIFY_CODE_NOT_MATCH: "短信验证码不匹配",
        # 短信服务-应用模板管理
        SMS_APP_TEMP_DEPENDENT_DELETE: "有短信模板正在使用此应用模板，禁止删除！",
        # 短信服务-应用管理
        SMS_APP_DEPENDENT_DELETE: "有应用模板正在使用此应用，禁止删除！",
        # 短信服务-业务模板管理
        SMS_BUSSINESS_APP_TEMPLATE_IS_NOT_EXIST: "应用模板不存在",
        SMS_BUSSINESS_TEMPLATE_IS_EXIST: "业务模板已存在",
        # 短信服务-短信发送
        SMS_SENDER_BUSS_TEMPLATE_NOT_EXIST: "业务模板不存在",
        SMS_SENDER_APP_TEMPLATE_NOT_EXIST: "短信业务模版未配置通道模版",
        SMS_SENDER_CONFIG_NOT_EXIST: "未找到短信应用配置",
        SMS_SENDER_FAILED: "短信发送失败",
        # 手机号码归属地服务
        ERROR_PHONE_NUMBER: "手机号码错误",
        # ip归属地服务
        ERRPR_IP_NUMBER: "IP地址错误"
    }
