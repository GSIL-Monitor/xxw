from src import api, app

from src.modules import (args_mgr, contract, mail_mgr, manager, manager_mgr, merchant_mgr,
                         risk_args, sms_mgr, task, credit_mgr, dashboard, dashboard_sale, dashboard_user,
                         credit_merchant, credit_conf, sx_mgr, regional_control, case_info, schedurun_mgr)
from src.modules.business_user import user, permission, public, merchant_business
from src.modules.monitor import config, monitor
# 执行脚本需要引用
from src.scripts.generate_init_data import generate_data

# 路由注册

# 任务处理
api.add_resource(task.AuditEvtAPI, "/api/v1/audit_task/tasks")
api.add_resource(task.AllotAuditEvtAPI, "/api/v1/audit_task/allot_task")
api.add_resource(task.AuditEvtAllotCntAPI, "/api/v1/audit_task/allot_cnt") 

# 参数配置
api.add_resource(args_mgr.CommonCodeAPI, "/api/v1/args_mgr/common_code")  # 通用参数字典
api.add_resource(args_mgr.IndustryPositionAPI, "/api/v1/args_mgr/industry_position")  # 行业职位
api.add_resource(args_mgr.IndustryCodeAPI, "/api/v1/args_mgr/industry_code")  # 行业代码

# b 端用户 ==================================================
api.add_resource(user.SignIn, "/api/v1/user/sign_in")
api.add_resource(user.Password, "/api/v1/user/password")
api.add_resource(user.SignOut, "/api/v1/user/sign_out")
api.add_resource(user.UserInfo, "/api/v1/user/info")
# 用户管理
api.add_resource(user.MerchantView, "/api/v1/user/merchant")
api.add_resource(user.UserManage, "/api/v1/user")
api.add_resource(user.ResetPassword, "/api/v1/user/password/reset")
api.add_resource(user.UserActivation, "/api/v1/user/activation")

# 获取商户名和系统名
api.add_resource(merchant_business.MerBizName, "/api/v1/merchant_business_name")
# 业务接入管理
api.add_resource(merchant_business.BusinessViewSet, "/api/v1/business")
api.add_resource(merchant_business.ActiveBusiness, "/api/v1/business/activation")
api.add_resource(merchant_business.BusinessAppid, "/api/v1/business/appid")
# 商户管理
api.add_resource(merchant_business.MerchantManage, "/api/v1/merchant")
api.add_resource(merchant_business.MerchantSystem, "/api/v1/merchant/system")

# 权限管理 - 授权user, 管理
api.add_resource(permission.AuthPermission, "/api/v1/permission/auth")
api.add_resource(permission.BusinessRole, "/api/v1/permission/auth/business_role")
# 权限管理 - 角色管理
api.add_resource(permission.RolePermission, "/api/v1/permission/role")
api.add_resource(permission.BusinessInterfaceMenu, "/api/v1/permission/role/business/interface_menu")
# 权限管理 - 接口管理
api.add_resource(permission.InterfacePermission, "/api/v1/permission/interface")
# 权限管理 - 菜单管理
api.add_resource(permission.MenuPermission, "/api/v1/permission/menu")

# 通过传递一个用户或商户列表，返回数据
api.add_resource(public.UsersDetail, "/api/v1/user/users_detail")
api.add_resource(public.MerchantsDetail, "/api/v1/merchant/merchants_detail")
# 验证 token 和验证接口权限
api.add_resource(public.VerifyToken, "/api/v1/verify/token"),
api.add_resource(public.VerifyInterface, "/api/v1/verify/interface")
# 公共接口 - 对内
api.add_resource(public.BusinessInquire, "/api/v1/public/business")
api.add_resource(public.UserMenu, "/api/v1/public/user_menu")
# 公共接口 - 对外
# 通过商户 code 获取产品
api.add_resource(public.MerchantProduction, "/api/v1/public/merchant_production")
# 产品相关
api.add_resource(public.Production, "/api/v1/production")
# 获取该业务系统下用户能访问的接口和菜单 - 对外
api.add_resource(public.BuzInterMe, "/api/v1/business/inter_menu")

# 商户管理=====================================================
# 商户信息相关
api.add_resource(merchant_mgr.MerchantInfo, "/api/v1/merchant/info")
# 商户产品相关
api.add_resource(merchant_mgr.MerchantProductionFlag, "/api/v1/merchant/production_flag")
# 商户业务系统信息
api.add_resource(merchant_mgr.MerchantBusines, "/api/v1/merchant/business")
# 商户产品信息
api.add_resource(merchant_mgr.MerchantProductionInfo, "/api/v1/merchant/production")

# 商户经理=====================================================
# 管理操作
api.add_resource(manager_mgr.ManagerManage, "/api/v1/manager/manage")
api.add_resource(manager_mgr.ResetManagerPassword, "/api/v1/manager/manage/resetpassword")
# 登录/登出
api.add_resource(manager.ManagerSignIn, "/api/v1/manager/sign_in")
api.add_resource(manager.ManagerForgetPassword, "/api/v1/sign_in/forget_password")
# 商户经理信息相关
api.add_resource(manager.ManagerInfo, "/api/v1/manager/info")
api.add_resource(manager.ManagerModifyPassword, "/api/v1/manager/info/password")
api.add_resource(manager.FacesignInfo, "/api/v1/manager/info/facesign")
api.add_resource(manager.FacesignVerify, "/api/v1/manager/info/facesign_verify")
api.add_resource(manager.RushFacesign, "/api/v1/manager/info/rush_facesign")
# ===============================================================

# 合同管理
api.add_resource(contract.UserContractAPI, "/api/v1/contract/user_contract")
api.add_resource(contract.CFCASealCodeAPI, "/api/v1/cfca/seal_code")
api.add_resource(contract.ContractTemplateAPI, "/api/v1/cfca/contract_template")
api.add_resource(contract.ContractTypeAPI, "/api/v1/cfca/contract_type")
api.add_resource(contract.CFCATemplateAPI, "/api/v1/cfca/cfca_template")
api.add_resource(contract.ContractTextArgsAPI, "/api/v1/cfca/contract_text_args")
api.add_resource(contract.HtmlTemplateAPI, "/api/v1/cfca/html_template")
api.add_resource(contract.ContractConfigAPI, "/api/v1/cfca/contract_config")

# 邮件管理
api.add_resource(mail_mgr.MailTemplateAPI, "/mail_template")
api.add_resource(mail_mgr.MailLogAPI, "/mail_log")

# 短信管理
api.add_resource(sms_mgr.SmsLogAPI, "/sms_log")
api.add_resource(sms_mgr.SmsTemplateAPI, "/sms_template")
api.add_resource(sms_mgr.SmsTemplateTypeAPI, "/sms_template_types")
api.add_resource(sms_mgr.SmsTemplateSenderAPI, "/sms_template_sender")

# 风险管控
api.add_resource(risk_args.RiskArgsAPI, "/risk_args")
api.add_resource(regional_control.RegionalControlAPI, "/api/v1/risk/regional_control")


# 征信接口管理
api.add_resource(credit_mgr.CreditTypeApi, "/api/v1/config/merchant_credit")
# 征信日志查询
api.add_resource(credit_mgr.CreditLogApi, "/api/v1/logs/credit")
# 获取第三方征信源配置
api.add_resource(credit_conf.CreditConfigManageViews, "/api/v1/credit/conf")
# 获取租户征信配置
api.add_resource(credit_merchant.MerchantCredit, "/api/v1/merchant/credit")

# 可视化大盘
api.add_resource(dashboard.BasicInfo, "/api/v1/dashboard/basic_info")
api.add_resource(dashboard.EventCount, "/api/v1/dashboard/event_count")
api.add_resource(dashboard.RealTimeDetail, "/api/v1/dashboard/real_time_detail")
api.add_resource(dashboard.CompareChart, "/api/v1/dashboard/compare_chart")

# 销售情况统计
api.add_resource(dashboard_sale.ManagerSaleStatus, "/api/v1/manager/sale_status")
api.add_resource(dashboard_sale.ManagerSaleChart, "/api/v1/manager/sale_chart")

# 个人历史工单
api.add_resource(dashboard_user.UserHistoryWorkOrder, "/api/v1/user/history_work_order")
# 案件信息相关
api.add_resource(case_info.CaseListInfo, "/api/v1/case/list_info")   #列表
api.add_resource(case_info.CaseSingleInfo, "/api/v1/case/single_info")   #单条

# 配置监控修改=====================================
# support 项目配置
api.add_resource(config.Config, "/api/v1/config")
# 规则配置
api.add_resource(config.RuleConfig, "/api/v1/config/rule")
# 规则校验
api.add_resource(config.RuleVerify, "/api/v1/config/rule/verify")
# 配置更新历史
api.add_resource(config.ConfigHistory, "/api/v1/config/history")
# 配置回滚
api.add_resource(config.ConfigRollBack, "/api/v1/config/roll-back")
# 紧急同步
api.add_resource(config.SyncEmergency, "/api/v1/config/sync/emergency")
# 同步配置
api.add_resource(config.SyncConfig, "/api/v1/config/sync")
# 编辑请求
api.add_resource(config.EditRequest, "/api/v1/config/edit-request")
# 取消编辑锁定
api.add_resource(config.ReleaseEditLock, "/api/v1/config/edit-release")

# 注册服务监控
api.add_resource(monitor.ServerRegistration, "/api/v1/monitor/server-registration")

# ilog信息查询
api.add_resource(sx_mgr.CreditDetail, "/api/v1/credit/detail")

# 调度引擎运行事务管理
api.add_resource(schedurun_mgr.ScheduRunAPI, "/api/v1/schedurun")
api.add_resource(schedurun_mgr.ScheduBinRedoAPI, "/api/v1/schedubin_redo")

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port='8880')


