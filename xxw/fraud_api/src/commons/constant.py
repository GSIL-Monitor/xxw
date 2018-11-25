class Msg:

    SUCCESS = 0
    MOBILE_NOT_REGISTER = 10001
    PARAMS_ERROR = 10002
    TOKEN_EXPIRATION = 10003
    INVALID_TOKEN = 10004
    OLD_PASSWORD_ERROR = 10005
    PASSWORD_ERROR = 10006
    MOBILE_USED = 10007
    UPLOAD_IMG_FAILED = 10008
    ASSIGN_FAILED = 10009
    ADD_ROLE_FAILED = 10010
    ASSIGN_APPID_FIRST = 10014
    DATA_EXIST = 10011
    UNKNOWN = 10012
    REQUEST_ERROR = 10013
    USER_OFFLINE = 10015
    NO_DATA = 20000
    USER_FORBIDDEN = 20001
    PERMISSION_DENIED = 30000
    ACCOUNT_FREEZING = 30001
    MANAGER_FROZEN = 30002
    USER_NOT_EXISTS = 40001
    BUSINESS_NOT_EXIST = 40002
    INTERFACE_NOT_EXIST = 40003
    MENU_NOT_EXIST = 40004
    ROLE_NOT_EXIST = 40005
    MERCHANT_NOT_EXIST = 40006
    APPID_NOT_EXIST = 40007
    DOMAIN_NOT_EXIST = 40008
    USER_NOT_ACTIVE = 40009
    USER_IS_BANED = 40010
    PRODUCTION_NOT_EXIST = 40011
    MANAGER_NOT_EXISTS = 40020
    COMBINE_ID_NOT_EXISTS = 40021
    COMBINE_ID_NOT_BINGDING = 40022
    PRODUCTION_NOT_EXIST = 40023
    WORKING_ADDRESS_NOT_EXISTS = 40024
    APPID_ALREADY_EXIST = 50000
    MERCHANT_NAME_ALREADY_EXIST = 50001
    BUSINESS_NAME_ALREADY_EXIST = 50002
    ROLE_NAME_ALREADY_EXIST = 50003
    MERCHANT_BUSINESS_ALREADY_EXIST = 50004
    DOMAIN_ALREADY_EXIST = 50005
    LOAN_NO_ALREADY_EXIST = 50006
    COLLECTION_NO_ALREADY_EXIST = 50007
    PRE_DEPOSIT_NO_ALREADY_EXIST = 50008

    msg = {
        SUCCESS: "成功",
        MOBILE_NOT_REGISTER: "手机号未注册",
        PARAMS_ERROR: "参数错误",
        TOKEN_EXPIRATION: "token 过期",
        INVALID_TOKEN: "token 错误",
        USER_NOT_EXISTS: "用户不存在",
        OLD_PASSWORD_ERROR: "旧密码错误",
        PASSWORD_ERROR: "密码错误",
        MOBILE_USED: "手机号已注册",
        ASSIGN_FAILED: "分配失败",
        ADD_ROLE_FAILED: "添加角色失败",
        ASSIGN_APPID_FIRST: "请先为系统分配 APPID",
        DATA_EXIST: "数据已存在",
        UNKNOWN: "未知错误",
        REQUEST_ERROR: "当前请求不被允许",
        NO_DATA: "无数据",
        USER_FORBIDDEN: "用户被拒绝",
        PERMISSION_DENIED: "用户无权限",
        ACCOUNT_FREEZING: "帐号被冻结",
        MANAGER_FROZEN: "商户经理被冻结",
        BUSINESS_NOT_EXIST: "该业务系统不存在",
        INTERFACE_NOT_EXIST: "该接口不存在",
        MENU_NOT_EXIST: "该菜单不存在",
        ROLE_NOT_EXIST: "该角色不存在",
        MERCHANT_NOT_EXIST: "该商户不存在",
        USER_NOT_ACTIVE: "用户未激活",
        USER_IS_BANED: "用户已被禁用，请联系管理员",
        MANAGER_NOT_EXISTS: "该客户经理不存在",
        COMBINE_ID_NOT_EXISTS: "小程序联合id不存在",
        COMBINE_ID_NOT_BINGDING: "号码未绑定",
        WORKING_ADDRESS_NOT_EXISTS: "工作地址不存在",
        APPID_ALREADY_EXIST: "该业务系统 appid 已存在",
        APPID_NOT_EXIST: "无此 appid 对应的业务系统",
        MERCHANT_NAME_ALREADY_EXIST: "商户名已存在",
        BUSINESS_NAME_ALREADY_EXIST: "业务系统名已存在",
        ROLE_NAME_ALREADY_EXIST: "角色名已存在",
        MERCHANT_BUSINESS_ALREADY_EXIST: "该商户此业务已存在",
        DOMAIN_NOT_EXIST: "该域名不存在",
        DOMAIN_ALREADY_EXIST: "该域名已存在",
        UPLOAD_IMG_FAILED: "图片上传失败",
        LOAN_NO_ALREADY_EXIST: "同业账户放款账号已存在",
        COLLECTION_NO_ALREADY_EXIST: "同业账户收款账号已存在",
        PRE_DEPOSIT_NO_ALREADY_EXIST: "同业账户预存款账号已存在",
        PRODUCTION_NOT_EXIST: "此商户下无产品",
        USER_OFFLINE: "用户在其他地方登录，请重新登录"
    }


class WordToInt:
    cons = {
        "a": "1",
        "b": "2",
        "c": "3",
        "d": "4",
        "e": "5",
        "f": "6",
        "g": "7",
        "h": "8",
        "i": "9",
        "j": "1",
        "k": "2",
        "l": "3",
        "m": "4",
        "n": "5",
        "o": "6",
        "p": "7",
        "q": "8",
        "r": "9",
        "s": "1",
        "t": "2",
        "u": "3",
        "v": "4",
        "w": "5",
        "x": "6",
        "y": "7",
        "z": "8",
    }
