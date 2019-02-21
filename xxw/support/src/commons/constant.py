class Msg:

    SUCCESS = 0
    MOBILE_NOT_REGISTER = 10001
    PARAMS_ERROR = 10002
    TOKEN_EXPIRATION = 10003
    INVALID_TOKEN = 10004
    OLD_PASSWORD_ERROR = 10005
    PASSWORD_ERROR = 10006
    PHONE_USED = 10007
    UPLOAD_IMG_FAILED = 10008
    ASSIGN_FAILED = 10009
    ADD_ROLE_FAILED = 10010
    ASSIGN_APPID_FIRST = 10014
    DATA_EXIST = 10011
    UNKNOWN = 10012
    REQUEST_ERROR = 10013
    USER_OFFLINE = 10015
    MOBILE_NOT_REGISTER_OR_PASSWORD_ERROR = 10016
    UPDATE_CONFIG_FAILED = 10017
    SYNC_FAILED = 10018
    WRONG_VERSION = 10019
    RELEASE_LOCK_FAILED = 10020
    UPDATE_PRODUCTION_FAILED = 10021
    NO_DATA = 20000
    USER_FORBIDDEN = 20001
    PERMISSION_DENIED = 30000
    ACCOUNT_FREEZING = 30001
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
    COMBINE_ID_NOT_EXISTS = 40021
    COMBINE_ID_NOT_BINGDING = 40022
    PRODUCTION_NOT_EXIST = 40023
    WORKING_ADDRESS_NOT_EXISTS = 40024
    MERCHANT_BUSINESS_NOT_EXIST = 40025
    NO_CONFIG = 40026
    APPID_ALREADY_EXIST = 50000
    MERCHANT_NAME_ALREADY_EXIST = 50001
    BUSINESS_NAME_ALREADY_EXIST = 50002
    ROLE_NAME_ALREADY_EXIST = 50003
    MERCHANT_BUSINESS_ALREADY_EXIST = 50004
    DOMAIN_ALREADY_EXIST = 50005
    LOAN_NO_ALREADY_EXIST = 50006
    COLLECTION_NO_ALREADY_EXIST = 50007
    PRE_DEPOSIT_NO_ALREADY_EXIST = 50008
    DOMAIN_DUNPLICATE = 50009
    EDIT_LOCKED = 50010
    OFFICIAL_ACCOUNT_ALREADY_EXIST = 50011
    
    # 商户经理错误码 (suport服务)1014+(商户经理类型)20+(错误码)0000
    MANAGER_MERCHANT_NOT_EXIST = 1014200001  # ^00 为管理类错误
    MANAGER_NOT_EXISTS = 101420002
    MANAGER_IDCARD_EXIST = 1014200003
    MANAGER_PHONE_EXIST = 1014200004
    MANAGER_PHONE_NOT_EXIST = 1014200101  # ^01 为登录类错误
    MANAGER_BINDING_ERROR = 1014200102
    MANAGER_WECHET_NOT_BINDING = 1014200103
    MANAGER_VERIFY_CODE_ERROR = 1014200104
    MANAGER_PASSWORD_ERROR = 1014200105
    MANAGER_PASSWORD_ERROR_FROZEN = 1014200106
    MANAGER_PASSWORD_DIFFERENT = 1014200201  # ^02以上为操作类错误
    MANAGER_OLD_PASSWORD_ERROR = 1014200202
    MANAGER_FACESIGN_NOT_EXIST = 1014200301

    msg = {
        SUCCESS: "成功",
        MOBILE_NOT_REGISTER: "手机号未注册",
        MOBILE_NOT_REGISTER_OR_PASSWORD_ERROR: "手机号未注册或密码错误",
        PARAMS_ERROR: "参数错误",
        TOKEN_EXPIRATION: "token 过期",
        INVALID_TOKEN: "token 错误",
        USER_NOT_EXISTS: "用户不存在",
        OLD_PASSWORD_ERROR: "旧密码错误",
        PASSWORD_ERROR: "密码错误",
        PHONE_USED: "手机号已注册",
        ASSIGN_FAILED: "分配失败",
        ADD_ROLE_FAILED: "添加角色失败",
        ASSIGN_APPID_FIRST: "请先为系统分配 APPID",
        DATA_EXIST: "数据已存在",
        UNKNOWN: "未知错误",
        REQUEST_ERROR: "当前请求不被允许",
        UPDATE_CONFIG_FAILED: "更新配置失败",
        SYNC_FAILED: "同步失败",
        WRONG_VERSION: "同步失败，该配置不是最新配置，请拉取最新配置进行修改",
        RELEASE_LOCK_FAILED: "当前用户无法释放编辑锁定",
        UPDATE_PRODUCTION_FAILED: "产品更新失败",
        NO_DATA: "无数据",
        USER_FORBIDDEN: "用户被拒绝",
        PERMISSION_DENIED: "用户无权限",
        ACCOUNT_FREEZING: "帐号被冻结",
        BUSINESS_NOT_EXIST: "该业务系统不存在",
        INTERFACE_NOT_EXIST: "该接口不存在",
        MENU_NOT_EXIST: "该菜单不存在",
        ROLE_NOT_EXIST: "该角色不存在",
        MERCHANT_NOT_EXIST: "该商户不存在",
        USER_NOT_ACTIVE: "用户未激活",
        USER_IS_BANED: "用户已被禁用，请联系管理员",
        COMBINE_ID_NOT_EXISTS: "小程序联合id不存在",
        COMBINE_ID_NOT_BINGDING: "号码未绑定",
        WORKING_ADDRESS_NOT_EXISTS: "工作地址不存在",
        MERCHANT_BUSINESS_NOT_EXIST: "商户该业务系统不存在",
        NO_CONFIG: "未找到配置，同步失败！",
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
        USER_OFFLINE: "用户在其他地方登录，请重新登录",
        DOMAIN_DUNPLICATE: "域名重复，请检测输入值",
        EDIT_LOCKED: "编辑已经锁定，请联系正在编辑的用户",
        OFFICIAL_ACCOUNT_ALREADY_EXIST: "公众号已存在",
        #商户经理错误
        MANAGER_MERCHANT_NOT_EXIST: "商户不存在",
        MANAGER_NOT_EXISTS: "该客户经理不存在",
        MANAGER_PHONE_EXIST: "手机号码已存在",
        MANAGER_IDCARD_EXIST: "身份证号已存在",
        MANAGER_PHONE_NOT_EXIST: "无法找到手机号码",
        MANAGER_BINDING_ERROR: "手机和openid绑定关系错误",
        MANAGER_WECHET_NOT_BINDING: "该微信未绑定任何手机",
        MANAGER_VERIFY_CODE_ERROR: "验证码错误",
        MANAGER_PASSWORD_ERROR : "登录密码错误",
        MANAGER_PASSWORD_ERROR_FROZEN : "因多次密码错误，已冻结",
        MANAGER_PASSWORD_DIFFERENT: "两次输入密码不同",
        MANAGER_OLD_PASSWORD_ERROR: "旧密码错误",
        MANAGER_FACESIGN_NOT_EXIST: "无该预约面签单/或已被抢",


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


class ConfigNameMap:
    """
    项目配置名
    """
    SUPPORT = "SUPPORT"
    OS_CENTER = "OS_CENTER"
    CREDIT = "CREDIT"
    ANTIFRAUD = "ANTIFRAUD"
    SHEDULE = "SHEDULE"
    CREDIT_DPC = "CREDIT_DPC"
    AUDIT_TASK = "AUDIT_TASK"
    AUDIT_TASK_REDO = "AUDIT_TASK_REDO"
    CHAOS = "CHAOS"

    name = {
        0: SUPPORT,
        1: OS_CENTER,
        2: CREDIT,
        3: ANTIFRAUD,
        4: SHEDULE,
        5: CREDIT_DPC,
        6: AUDIT_TASK,
        7: AUDIT_TASK_REDO,
        8: CHAOS
    }

    menu_path = {
        SUPPORT: "/center/basic",
        OS_CENTER: "/center/user",
        CREDIT: "/center/credit",
        ANTIFRAUD: "/center/antifraud",
        CREDIT_DPC: "/center/dpc",
        AUDIT_TASK: "/center/audit_task",
        AUDIT_TASK_REDO: "/center/audit_task_redo",
        CHAOS: "/center/chaos"
    }

    zk_path = {
            CREDIT: "/entry/config/service/credit",
            CREDIT_DPC: "/entry/config/service/dpc_server",
            OS_CENTER: "/entry/config/service/os_center",
            ANTIFRAUD: "/entry/config/service/antifraud",
            SHEDULE: "/entry/config/service/shedule",
            AUDIT_TASK: "/entry/config/service/audit_task",
            AUDIT_TASK_REDO: "/entry/config/service/audit_task_redo",
            CHAOS: "/entry/config/service/chaos"
        }
