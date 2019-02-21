from werkzeug.security import check_password_hash, generate_password_hash

from src import db
from src.commons.date_utils import utc_timestamp

roles = db.Table(
    "tb_user_role",
    db.Column("role_id", db.Integer, db.ForeignKey("tb_role.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("tb_user.id"), primary_key=True),
)

interface = db.Table(
    "tb_role_interface",
    db.Column("interface_id", db.Integer, db.ForeignKey("tb_interface.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("tb_role.id"), primary_key=True),
)

menu = db.Table(
    "tb_role_menus",
    db.Column("menu_id", db.Integer, db.ForeignKey("tb_menu.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("tb_role.id"), primary_key=True),
)


class TbUser(db.Model):
    __tablename__ = "tb_user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), comment="用户名")
    phone = db.Column(db.String(11), unique=True, comment="手机号")
    sex = db.Column(db.String(7), default="unknown", comment="性别")
    password = db.Column(db.String(100), comment="密码")
    address = db.Column(db.String(264), comment="地址")
    avatar = db.Column(db.String(264), comment="头像")
    mail = db.Column(db.String(128), comment="邮箱")
    wechat = db.Column(db.String(128), comment="微信")
    qq = db.Column(db.String(20), comment="qq")
    is_admin = db.Column(db.Boolean, default=False, comment="是否是 superuser",)
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    update_time = db.Column(db.BigInteger, comment="更新时间")
    # 一个用户拥有多个角色
    roles = db.relationship(
        "TbRole",
        secondary=roles,
        lazy="subquery",
        backref=db.backref("users", lazy=True)
    )
    active = db.Column(db.Boolean, default=False, comment="是否激活")
    merchant_code = db.Column(db.Integer, db.ForeignKey("tb_merchant.code"))
    # merchant_code = db.Column(db.Integer)
    code = db.Column(db.String(32), comment="用户 code", unique=True)
    extra = db.Column(db.Text, comment="额外字段")
    # 外键
    business = db.relationship("TbBusiness", backref="creator", lazy=True, cascade="all, delete, delete-orphan")
    interface = db.relationship("TbInterface", backref="creator", lazy=True, cascade="all, delete, delete-orphan")
    menu = db.relationship("TbMenu", backref="creator", lazy=True, cascade="all, delete, delete-orphan")
    create_roles = db.relationship("TbRole", backref="creator", lazy=True, cascade="all, delete, delete-orphan")

    def get_name(self):
        return self.name

    def generate_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "用户 {}".format(self.name)


class TbMerchant(db.Model):
    """
    商户
    """

    __tablename__ = "tb_merchant"

    id = db.Column(db.Integer, primary_key=True, comment="自增 id", autoincrement=True)
    name = db.Column(db.String(128), comment="商户名")
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    is_active = db.Column(db.Boolean, default=True, comment="是否激活")
    logo = db.Column(db.String(264), comment="有颜色有文字图标")
    logo_no_word = db.Column(db.String(255), comment="有颜色无文字图标")
    icon = db.Column(db.String(264), comment="无颜色无文字透明图标")
    icon_no_word = db.Column(db.String(255), comment="无颜色无文字图标")
    url = db.Column(db.String(128), comment="域名")
    iba_loan_name = db.Column(db.String(128), comment="同业账户放款户名")
    iba_loan_no = db.Column(db.String(32), comment="同业账户放款账号")
    iba_collection_name = db.Column(db.String(128), comment="同业账户收款账户名")
    iba_collection_no = db.Column(db.String(32), comment="同业账户收款账号")
    iba_pre_deposit_name = db.Column(db.String(128), comment="同业账户预存款账户名")
    iba_pre_deposit_no = db.Column(db.String(128), comment="同业账户预存款账号")
    org_no = db.Column(db.String(32), comment="机构号")
    code = db.Column(db.String(32), unique=True, comment="商户号")
    xw_code = db.Column(db.String(32), comment="新网商户 id")
    area_code = db.Column(db.String(16), comment="地址编码")
    area_name = db.Column(db.String(32), comment="地址")
    email = db.Column(db.String(128), comment="邮件")
    email_client = db.Column(db.String(128), comment="邮箱客户端")
    email_password = db.Column(db.String(128), comment="邮箱密码")
    sys_url = db.Column(db.String(256), comment="系统子域名")
    push_flag = db.Column(db.Boolean, default=False, comment="推送标志, 0 未推送， 1 已推送")
    extra = db.Column(db.Text, comment="额外字段")
    # # 外键
    roles = db.relationship("TbRole", backref="merchant", lazy=True, cascade="all, delete, delete-orphan")
    users = db.relationship("TbUser", backref="merchant", lazy=True, cascade="all, delete, delete-orphan")
    production = db.relationship("TbProduction", backref="merchant", lazy=True, cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "商户 {}".format(self.name)


class TbMerchantFile(db.Model):
    """商户文件"""
    __tablename__ = "tb_merchant_file"

    id = db.Column(db.Integer, primary_key=True, comment="自增 id", autoincrement=True)
    merchant_code = db.Column(db.String(32), db.ForeignKey("tb_merchant.code"))
    # merchant_code = db.Column(db.String(32))
    cover = db.Column(db.String(64), comment="封面")
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    extra = db.Column(db.Text, comment="额外字段")


class TbProduction(db.Model):
    """
    商户产品表
    """

    __tablename__ = "tb_production"

    id = db.Column(db.Integer, primary_key=True, comment="自增 id", autoincrement=True)
    merchant_code = db.Column(db.String(32), db.ForeignKey("tb_merchant.code"))
    name = db.Column(db.String(64), comment="产品名称")
    code = db.Column(db.String(32), unique=True, comment="产品号")
    status = db.Column(db.Boolean, default=True, comment="产品是否启用")
    logo = db.Column(db.String(264), comment="标志")
    icon = db.Column(db.String(264), comment="透明图标")
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    sms_appkey = db.Column(db.String(128), comment="短信发送 appkey")
    sms_appid = db.Column(db.String(128), comment="短信发送 appid")
    sms_sign = db.Column(db.String(128), comment="短信发送签名")
    face_flag = db.Column(db.Boolean, default=False, comment="面签标志")
    e_sign = db.Column(db.Boolean, default=False, comment="手写签名标志")
    amount_limit = db.Column(db.Integer, default=0, comment="面签额度")
    loan_min_amt = db.Column(db.Integer, default=0, comment="单笔提现最小值")
    loan_max_amt = db.Column(db.Integer, default=40000, comment="单笔提现最大值")
    extra = db.Column(db.Text, comment="额外字段")


class TbMerchantPublic(db.Model):
    """
    商户公众号表
    """

    __tablename__ = "tb_merchant_public"
    id = db.Column(db.Integer, primary_key=True, comment="自增 id", autoincrement=True)
    name = db.Column(db.String(128), comment="公众号名")
    appid = db.Column(db.String(32), comment="公众号 appid")
    status = db.Column(db.Boolean, default=True, comment="公众号开关")
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    update_time = db.Column(db.BigInteger, comment="创建时间")
    creator_code = db.Column(db.String(32), comment="创建者 code")
    merchant_code = db.Column(db.String(32), comment="商户 code")
    production_code = db.Column(db.String(32), comment="产品 code")
    extra = db.Column(db.Text, comment="额外字段")


class TbMerchantBusiness(db.Model):
    """
    """

    __tablename__ = "tb_merchant_business"
    id = db.Column(db.Integer, primary_key=True, comment="自增主键", autoincrement=True)
    merchant_code = db.Column(db.String(32))
    business_code = db.Column(db.String(32))
    merchant_name = db.Column(db.String(128))
    business_name = db.Column(db.String(128))
    logo = db.Column(db.String(256), default="", comment="业务 logo")
    icon = db.Column(db.String(256), default="", comment="业务 icon")
    alias = db.Column(db.String(64), default="", comment="业务别名")
    domain = db.Column(db.String(256), default="", comment="域名")
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")


class TbBusiness(db.Model):
    """
    业务系统
    """

    __tablename__ = "tb_business"

    id = db.Column(db.Integer, primary_key=True, comment="自增 id", autoincrement=True)
    name = db.Column(db.String(64), comment="业务名")
    appid = db.Column(db.String(64), comment="业务 appid")
    status = db.Column(db.Boolean, default=False, comment="业务状态")
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    creator_code = db.Column(db.String(32), db.ForeignKey("tb_user.code"))
    code = db.Column(db.String(32), comment="业务号", unique=True)

    # 外键
    interface = db.relationship("TbInterface", backref="business", lazy=True, cascade="all, delete, delete-orphan")
    menu = db.relationship("TbMenu", backref="business", lazy=True, cascade="all, delete, delete-orphan")
    roles = db.relationship("TbRole", backref="business", lazy=True, cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "业务系统 {}".format(self.name)


class TbInterface(db.Model):
    """
    接口
    """

    __tablename__ = "tb_interface"

    id = db.Column(db.Integer,
                   primary_key=True,
                   comment="自增 id", autoincrement=True)
    name = db.Column(db.String(64), comment="接口名")
    path = db.Column(db.String(128), comment="接口路径")
    business_code = db.Column(db.String(32), db.ForeignKey("tb_business.code"))
    method = db.Column(db.String(16), comment="调用方法")
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    creator_code = db.Column(db.String(32), db.ForeignKey("tb_user.code"))
    code = db.Column(db.String(32), comment="接口号", unique=True)
    visible = db.Column(db.Boolean, default=True, comment="是否可见")

    def __repr__(self):
        return "接口 {}".format(self.name)


class TbMenu(db.Model):
    """
    菜单
    """

    __tablename__ = "tb_menu"

    id = db.Column(db.Integer,
                   primary_key=True,
                   comment="自增 id", autoincrement=True)
    name = db.Column(db.String(64), comment="菜单名")
    path = db.Column(db.String(128), comment="菜单路径")
    business_code = db.Column(db.String(32), db.ForeignKey("tb_business.code"))
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    creator_code = db.Column(db.String(32), db.ForeignKey("tb_user.code"))
    code = db.Column(db.String(32), comment="菜单号", unique=True)
    visible = db.Column(db.Boolean, default=True, comment="是否可见")

    def __repr__(self):
        return "菜单 {}".format(self.name)


class TbRole(db.Model):
    """
    角色表
    """

    __tablename__ = "tb_role"

    id = db.Column(db.Integer, primary_key=True, comment="自增 id", autoincrement=True)
    name = db.Column(db.String(64), comment="角色名")
    interface = db.relationship(
        "TbInterface",
        secondary=interface,
        lazy="subquery",
        backref=db.backref("roles", lazy=True)
    )
    menu = db.relationship(
        "TbMenu",
        secondary=menu,
        lazy="subquery",
        backref=db.backref("roles", lazy=True))
    create_time = db.Column(db.BigInteger, default=utc_timestamp, comment="创建时间")
    creator_code = db.Column(db.String(32), db.ForeignKey("tb_user.code"))
    business_code = db.Column(db.String(32), db.ForeignKey("tb_business.code"))
    code = db.Column(db.String(32), comment="角色号", unique=True)
    merchant_code = db.Column(db.String(32), db.ForeignKey("tb_merchant.code"))

    def __repr__(self):
        return "角色表 {}".format(self.name)


class TbOperation(db.Model):
    """
    用户操作记录
    """

    __tablename__ = "tb_operation"

    id = db.Column(db.Integer,
                   primary_key=True,
                   comment="自增 id", autoincrement=True)
    operator_code = db.Column(db.String(32))
    content = db.Column(db.Text, comment="操作记录")
    operate_time = db.Column(db.BigInteger, default=utc_timestamp, comment="操作时间")
    # USER, INTERFACE, MENU, MERCHANT, ROLE, BUSINESS, USER_MANAGE
    category = db.Column(db.String(32), comment="操作种类， 用户、商户、接口")
    # DELETE, ADD, EDIT
    type = db.Column(db.String(32), comment="操作类型, 增删改")
    code = db.Column(db.String(32), comment="操作号", unique=True)

    def __repr__(self):
        return "用户操作 {}".format(self.content)


class TbMerchantCredit(db.Model):
    """
    商户接口信息表
    """
    __tablename__ = "tb_merchant_credit"

    interface = db.Column(db.String(20), nullable=False, comment="接口编码", primary_key=True)
    merchant_code = db.Column(db.String(32), nullable=False, comment="租户编号", primary_key=True)
    production_code = db.Column(db.String(32), nullable=False, comment="产品编号", primary_key=True)
    status = db.Column(db.BigInteger, default=1, nullable=False, comment="是否可用")
    interface_status = db.Column(db.Integer, default=1, nullable=False, comment="interface是否可用")
    update_time = db.Column(db.BigInteger, nullable=False, comment="更新时间")
    is_delete = db.Column(db.Integer, default=0, comment="删除状态")

    def to_json(self):
        return {
            "interface": self.interface or "",
            "merchant_code": self.merchant_code or "",
            "production_code": self.production_code or "",
            "status": 1 if self.status else 0,
            "interface_status": 1 if self.interface_status else 0,
            "update_time": self.update_time or '',
        }

    def __init__(self, **kwargs):
        self.merchant_code = kwargs.get("merchant_code", "")
        self.production_code = kwargs.get("production_code", "")
        self.interface = kwargs.get("interface", "")
        self.status = kwargs.get("status", "")
        self.interface_status = kwargs.get("interface_status", "")
        self.update_time = utc_timestamp()
