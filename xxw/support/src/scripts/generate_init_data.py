"""
生成初始化数据
"""

from src import app, db
from src.models.user import TbBusiness, TbInterface, TbMenu, TbUser

interface = [
    {"name": "权限管理-授权管理-列表", "path": "/permission/auth", "method": "GET", "visible": True},
    {"name": "权限管理-授权管理-授权", "path": "/permission/auth", "method": "PUT", "visible": True},
    {"name": "权限管理-授权管理-系统角色列表", "path": "/permission/auth/business_role", "method": "GET", "visible": True},
    {"name": "权限管理-角色管理-列表", "path": "/permission/role", "method": "GET", "visible": True},
    {"name": "权限管理-角色管理-编辑", "path": "/permission/role", "method": "PUT", "visible": True},
    {"name": "权限管理-角色管理-添加", "path": "/permission/role", "method": "POST", "visible": True},
    {"name": "权限管理-角色管理-删除", "path": "/permission/role", "method": "DELETE", "visible": True},
    {
        "name": "权限管理-角色管理-菜单接口列表",
        "path": "/permission/role/business/interface_menu",
        "method": "GET",
        "visible": True,
    },
    {"name": "权限管理-接口管理-列表", "path": "/permission/interface", "method": "GET", "visible": False},
    {"name": "权限管理-接口管理-编辑", "path": "/permission/interface", "method": "PUT", "visible": False},
    {"name": "权限管理-接口管理-删除", "path": "/permission/interface", "method": "DELETE", "visible": False},
    {"name": "权限管理-接口管理-添加", "path": "/permission/interface", "method": "POST", "visible": False},
    {"name": "权限管理-菜单管理-列表", "path": "/permission/menu", "method": "GET", "visible": False},
    {"name": "权限管理-菜单管理-添加", "path": "/permission/menu", "method": "POST", "visible": False},
    {"name": "权限管理-菜单管理-编辑", "path": "/permission/menu", "method": "PUT", "visible": False},
    {"name": "权限管理-菜单管理-删除", "path": "/permission/menu", "method": "DELETE", "visible": False},
    {"name": "系统接入管理-列表", "path": "/business", "method": "GET", "visible": False},
    {"name": "系统接入管理-编辑", "path": "/business", "method": "PUT", "visible": False},
    {"name": "系统接入管理-添加", "path": "/business", "method": "POST", "visible": False},
    {"name": "系统接入管理-激活状态", "path": "/business/activation", "method": "PUT", "visible": False},
    {"name": "商户管理-列表", "path": "/merchant", "method": "GET", "visible": False},
    {"name": "商户管理-添加", "path": "/merchant", "method": "POST", "visible": False},
    {"name": "商户管理-编辑", "path": "/merchant", "method": "PUT", "visible": False},
    {"name": "商户管理-分配系统", "path": "/merchant/system", "method": "PUT", "visible": False},
    {"name": "用户管理-列表", "path": "/user", "method": "GET", "visible": True},
    {"name": "用户管理-添加", "path": "/user", "method": "POST", "visible": True},
    {"name": "用户管理-编辑", "path": "/user", "method": "PUT", "visible": True},
    {"name": "用户管理-激活状态", "path": "/user/activation", "method": "PUT", "visible": True},
    {"name": "用户管理-商户列表", "path": "/user/merchant", "method": "GET", "visible": False},
    {"name": "用户管理-重置密码", "path": "/user/password/reset", "method": "PUT", "visible": True},
    {"name": "已激活系统列表", "path": "/public/business", "method": "GET", "visible": True},
    {"name": "动态菜单列表", "path": "/public/user_menu", "method": "GET", "visible": True},
]

menu = [
    {"name": "仪表盘", "path": "/", "visible": True},
    {"name": "权限管理-授权管理", "path": "/permission/auth", "visible": True},
    {"name": "权限管理-角色管理", "path": "/permission/role", "visible": True},
    {"name": "权限管理-接口管理", "path": "/permission/api", "visible": False},
    {"name": "权限管理-菜单管理", "path": "/permission/menu", "visible": False},
    {"name": "系统接入管理", "path": "/system", "visible": False},
    {"name": "商户管理", "path": "/merchant", "visible": False},
    {"name": "用户管理", "path": "/user", "visible": True},
]

fraud_api = [
  {
    "name": "数据大屏-设置-列表",
    "path": "/bank/list",
    "method": "GET",
    "visible": True
  },
  {
    "name": "数据大屏-设置-保存",
    "path": "/bank",
    "method": "POST",
    "visible": True
  },
  {
    "name": "数据大屏-设置-删除",
    "path": "/bank",
    "method": "DELETE",
    "visible": True
  },
  {
    "name": "数据大屏-设置-上传logo",
    "path": "/bank/icon/upload",
    "method": "POST",
    "visible": True
  },
  {
    "name": "控制中心-事件大盘-周期事件对比数据",
    "path": "/dashboard/compare/cycle",
    "method": "GET",
    "visible": True
  },
  {
    "name": "控制中心-事件大盘-事件地图数据",
    "path": "/dashboard/map",
    "method": "GET",
    "visible": True
  },
  {
    "name": "控制中心-事件大盘-大盘趋势数据",
    "path": "/dashboard/trend",
    "method": "GET",
    "visible": True
  },
  {
    "name": "控制中心-事件大盘-命中规则排行数据",
    "path": "/dashboard/ranking",
    "method": "GET",
    "visible": True
  },
  {
    "name": "控制中心-事件历史-查询",
    "path": "/event/query",
    "method": "GET",
    "visible": True
  },
  {
    "name": "控制中心-规则事件列表-查询",
    "path": "/event/hitrule",
    "method": "GET",
    "visible": True
  },
  {
    "name": "策略中心-特征集管理-添加",
    "path": "/strategy/feature",
    "method": "POST",
    "visible": True
  },
  {
    "name": "策略中心-特征集管理-更新",
    "path": "/strategy/feature",
    "method": "PUT",
    "visible": True
  },
  {
    "name": "策略中心-特征集管理-查询",
    "path": "/strategy/feature",
    "method": "GET",
    "visible": True
  },
  {
    "name": "策略中心-特征集管理-删除",
    "path": "/strategy/feature",
    "method": "DELETE",
    "visible": True
  },
  {
    "name": "策略中心-区域管控-添加",
    "path": "/strategy/area",
    "method": "POST",
    "visible": True
  },
  {
    "name": "策略中心-区域管控-查询",
    "path": "/strategy/area",
    "method": "GET",
    "visible": True
  },
  {
    "name": "策略中心-区域管控-更新",
    "path": "/strategy/area",
    "method": "PUT",
    "visible": True
  },
  {
    "name": "策略中心-区域管控-删除",
    "path": "/strategy/area",
    "method": "DELETE",
    "visible": True
  }
]

fraud_menu = [
  {
    "name": "数据大屏-展示",
    "path": "/screen",
    "visible": True
  },
  {
    "name": "数据大屏-设置",
    "path": "/screen/config",
    "visible": True
  },
  {
    "name": "控制中心-事件大盘",
    "path": "/setting/dashboard",
    "visible": True
  },
  {
    "name": "控制中心-事件历史",
    "path": "/setting/records",
    "visible": True
  },
  {
    "name": "控制中心-规则事件列表",
    "path": "/setting/hit",
    "visible": True
  },
  {
    "name": "策略中心-特征集管理",
    "path": "/strategy/feature",
    "visible": True
  },
  {
    "name": "策略中心-区域管控",
    "path": "/strategy/region",
    "visible": True
  }
]

operation_api = [{
    "path": "/sms/history",
    "name": "短信管理-短信历史-列表",
    "method": "GET"
  },
  {
    "path": "/sms/types",
    "name": "短信管理-短信类型",
    "method": "GET"
  },
  {
    "path": "/sms/send",
    "name": "短信管理-短信发送",
    "method": "POST"
  },
  {
    "path": "/sms/send",
    "name": "短信管理-短信发送-模板下载",
    "method": "GET"
  },
  {
    "path": "/sms/template",
    "name": "短信管理-短信模板-列表",
    "method": "GET"
  },
  {
    "path": "/sms/templates",
    "name": "短信管理-根据租户查询所有模板",
    "method": "GET"
  },
  {
    "path": "/sms/template",
    "name": "短信管理-短信模板-删除",
    "method": "DELETE"
  },
  {
    "path": "/sms/template",
    "name": "短信管理-短信模板-更新",
    "method": "PUT"
  },
  {
    "path": "/sms/template",
    "name": "短信管理-短信模板-新增",
    "method": "POST"
  },
  {
    "path": "/audit/applycase",
    "name": "业务处理-申请案件-列表",
    "method": "GET"
  },
  {
    "path": "/audit/applycase/detail",
    "name": "业务处理-申请案件-详情",
    "method": "GET"
  },
  {
    "path": "/audit/credit",
    "name": "业务处理-授信审批-列表",
    "method": "GET"
  },
  {
    "path": "/audit/credit/detail",
    "name": "业务处理-授信审批-详情",
    "method": "GET"
  },
  {
    "path": "/audit/credit/pass",
    "name": "业务处理-授信审批-通过",
    "method": "POST"
  },
  {
    "path": "/audit/credit/refuse",
    "name": "业务处理-授信审批-驳回",
    "method": "POST"
  },
  {
    "path": "/audit/facesign",
    "name": "业务处理-面签审批-列表",
    "method": "GET"
  },
  {
    "path": "/audit/facesign/detail",
    "name": "业务处理-面签审批-详情",
    "method": "GET"
  },
  {
    "path": "/audit/facesign/refuse",
    "name": "业务处理-面签审批-驳回",
    "method": "POST"
  },
  {
    "path": "/audit/facesign/pass",
    "name": "业务处理-面签审批-通过",
    "method": "POST"
  },
  {
    "path": "/audit/fscase",
    "name": "业务处理-面签案件-列表",
    "method": "GET"
  },
  {
    "path": "/audit/fscase/detail",
    "name": "业务处理-面签案件-详情",
    "method": "GET"
  },
  {
    "path": "/account/manage",
    "name": "客户经理管理-用户管理-列表",
    "method": "GET"
  },
  {
    "path": "/account/manage",
    "name": "客户经理管理-用户管理-新增",
    "method": "POST"
  },
  {
    "path": "/account/manage",
    "name": "客户经理管理-用户管理-更新",
    "method": "PUT"
  },
  {
    "path": "/account/manage",
    "name": "客户经理管理-用户管理-删除",
    "method": "DELETE"
  },
  {
    "path": "/account/manage/qr",
    "name": "客户经理管理-用户管理-二维码",
    "method": "GET"
  },
  {
    "path": "/account/sales",
    "name": "客户经理管理-销售管理-列表",
    "method": "GET"
  },
  {
    "path": "/account/sales/chart",
    "name": "客户经理管理-销售管理-图标",
    "method": "GET"
  },
  {
    "path": "/account/sales/dowload",
    "name": "客户经理管理-销售管理-导出",
    "method": "GET"
  },
  {
    "path": "/parameter/refusecode",
    "name": "参数管理-拒绝代码-列表",
    "method": "GET"
  },
  {
    "path": "/parameter/refusecode",
    "name": "参数管理-拒绝代码-新增",
    "method": "POST"
  },
  {
    "path": "/parameter/refusecode",
    "name": "参数管理-拒绝代码-更新",
    "method": "PUT"
  },
  {
    "path": "/parameter/refusecode",
    "name": "参数管理-拒绝代码-删除",
    "method": "DELETE"
  },
  {
    "path": "/parameter/refusecodes",
    "name": "参数管理-拒绝代码-所有列表",
    "method": "GET"
  },
  {
    "path": "/parameter/occupation",
    "name": "参数管理-行业代码-列表",
    "method": "GET"
  },
  {
    "path": "/parameter/occupation",
    "name": "参数管理-行业代码-新增",
    "method": "POST"
  },
  {
    "path": "/parameter/occupation",
    "name": "参数管理-行业代码-更新",
    "method": "PUT"
  },
  {
    "path": "/parameter/occupation",
    "name": "参数管理-行业代码-删除",
    "method": "DELETE"
  },
  {
    "path": "/parameter/occupation/industry",
    "name": "参数管理-行业代码-获取行业",
    "method": "GET"
  },
  {
    "path": "/common/city",
    "name": "公共接口-城市列表",
    "method": "GET"
  },
  {
    "path": "/common/upload",
    "name": "公共接口-文件上传",
    "method": "POST"
  },
  {
    "path": "/common/tenant",
    "name": "公共接口-商户",
    "method": "GET"
  },
  {
    "path": "/common/tenant",
    "name": "公共接口-商户",
    "method": "GET"
  }
]

operation_menu = [{
    "path": "/sms/history",
    "name": "短信管理-短信历史"
  },
  {
    "path": "/sms/template",
    "name": "短信管理-短信模板"
  },
  {
    "path": "/sms/send",
    "name": "短信管理-发送短信"
  },
  {
    "path": "/audit/credit",
    "name": "业务处理-授信审批"
  },
  {
    "path": "/audit/applycase",
    "name": "业务处理-申请案件"
  },
  {
    "path": "/audit/fscase",
    "name": "业务处理-面签案件"
  },
  {
    "path": "/audit/facesign",
    "name": "业务处理-面签审批"
  },
  {
    "path": "/account/manage",
    "name": "客户经理管理-用户管理"
  },
  {
    "path": "/account/sales",
    "name": "客户经理管理-销售情况"
  },
  {
    "path": "/parameter",
    "name": "参数管理"
  }
]


@app.cli.command()
def generate_data():
    # 生成 superuser
    print("生成超级用户中......")
    user = TbUser(name="超级用户", phone="13308086321", is_admin=True, active=True)
    user.generate_password("123456")
    db.session.add(user)
    db.session.commit()
    user.code = str(1000000000 + user.id)
    print("成功超级用户成功，密码：{}, 请务必记住！".format("123456"))
    print("生成系统中......")
    print("生成用户中心中......")
    biz = TbBusiness(
        # 业务系统名
        name="用户中心",
        # 生成的 appid
        appid="26855f6e949911e89ed30a580a000421",
        # 状态，是否启用
        status=True,
        creator_code=user.code,
    )
    print("生成反欺诈系统中......")
    fraud_biz = TbBusiness(
        # 业务系统名
        name="反欺诈系统",
        # 生成的 appid
        appid="606fd0e40320418d83d1dd5c2e800767",
        # 状态，是否启用
        status=True,
        creator_code=user.code,
    )
    print("生成运营平台中......")
    operation = TbBusiness(
        # 业务系统名
        name="运营平台",
        # 生成的 appid
        appid="d19e03be22eb41dcac16dbf752ea8d7c",
        # 状态，是否启用
        status=True,
        creator_code=user.code,
    )
    print("生成信贷核心中......")
    credit = TbBusiness(
        # 业务系统名
        name="信贷核心",
        # 生成的 appid
        appid="1b46f632d4ed479da978c0cf15107c66",
        # 状态，是否启用
        status=True,
        creator_code=user.code,
    )
    print("生成风险驾驶舱中......")
    risk = TbBusiness(
        # 业务系统名
        name="风险驾驶舱",
        # 生成的 appid
        appid="13f01893d2114a81b4666deda3195b57",
        # 状态，是否启用
        status=True,
        creator_code=user.code,
    )
    print("生成金科大后台中......")
    backend = TbBusiness(
        # 业务系统名
        name="金科大后台",
        # 生成的 appid
        appid="d3fd3a372e2a4f75a05dda69fea5a1d6",
        # 状态，是否启用
        status=True,
        creator_code=user.code,
    )
    user.business.append(biz)
    user.business.append(fraud_biz)
    user.business.append(operation)
    user.business.append(risk)
    user.business.append(credit)
    user.business.append(backend)
    db.session.add(biz)
    db.session.add(fraud_biz)
    db.session.add(operation)
    db.session.add(risk)
    db.session.add(credit)
    db.session.add(backend)
    db.session.commit()
    biz.code = str(1200000000 + biz.id)
    fraud_biz.code = str(1200000000 + fraud_biz.id)
    operation.code = str(1200000000 + operation.id)
    risk.code = str(1200000000 + risk.id)
    credit.code = str(1200000000 + credit.id)
    backend.code = str(1200000000 + backend.id)
    db.session.commit()
    print("用户中心生成成功!")
    print("反欺诈系统生成成功!")
    print("运营中心生成成功!")
    print("风险驾驶舱生成成功!")
    print("金科大后台生成成功!")
    print("信贷核心生成成功!")
    print("用户系统 appid 为 {}".format("26855f6e949911e89ed30a580a000421"))
    print("反欺诈系统 appid 为 {}".format("606fd0e40320418d83d1dd5c2e800767"))
    print("运营中心 appid 为 {}".format("d19e03be22eb41dcac16dbf752ea8d7c"))
    print("风险驾驶舱 appid 为 {}".format("13f01893d2114a81b4666deda3195b57"))
    print("金科大后台 appid 为 {}".format("d3fd3a372e2a4f75a05dda69fea5a1d6"))
    print("信贷核心 appid 为 {}".format("1b46f632d4ed479da978c0cf15107c66"))
    print("生成用户中心菜单中......")
    for i in menu:
        m = TbMenu(
            name=i["name"], 
            path=i["path"], 
            creator_code=user.code, 
            business_code=biz.code, 
            visible=i["visible"])
        biz.menu.append(m)
        user.menu.append(m)
        db.session.add(m)
        db.session.commit()
        m.code = str(1500000000 + m.id)
        db.session.commit()
    print("生成用户中心菜单成功!")
    print("生成系统接口中......")
    for i in interface:
        inter = TbInterface(
            name=i["name"],
            path=i["path"],
            method=i["method"],
            business_code=biz.code,
            creator_code=user.code,
            visible=i["visible"]
        )
        biz.interface.append(inter)
        user.interface.append(inter)
        db.session.add(inter)
        db.session.commit()
        inter.code = str(1400000000 + inter.id)
        db.session.commit()
    print("生成用户中心接口成功！")

    print("生成反欺诈菜单中......")
    for i in fraud_menu:
        m = TbMenu(
            name=i["name"], 
            path=i["path"], 
            creator_code=user.code, 
            business_code=fraud_biz.code, 
            visible=i["visible"])
        fraud_biz.menu.append(m)
        user.menu.append(m)
        db.session.add(m)
        db.session.commit()
        m.code = str(1500000000 + m.id)
        db.session.commit()
    print("生成反欺诈菜单成功!")
    print("生成反欺诈接口中......")
    for i in fraud_api:
        inter = TbInterface(
            name=i["name"],
            path=i["path"],
            method=i["method"],
            business_code=fraud_biz.code,
            creator_code=user.code, 
            visible=i["visible"]
        )
        fraud_biz.interface.append(inter)
        user.interface.append(inter)
        db.session.add(inter)
        db.session.commit()
        inter.code = str(1400000000 + inter.id)
        db.session.commit()
    print("生成反欺诈接口成功！")
