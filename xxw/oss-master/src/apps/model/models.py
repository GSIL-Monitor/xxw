from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password


# Create your models here.


class MyUserManager(BaseUserManager):
    def create_user(self, username, email, mobile, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email or not username:
            raise ValueError('Users must have an email address and username')

        user = self.model(
            email=self.normalize_email(email),
            mobile=mobile,
            username=username
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, mobile, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            username=username,
            mobile=mobile
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class Merchant(models.Model):
    """
    商户
    """
    # 商户名
    name = models.CharField(max_length=100)
    # 创建时间
    create_time = models.DateTimeField(default=now)
    active = models.BooleanField(default=True)
    # 标志
    logo = models.CharField(max_length=256)
    # 域名
    url = models.CharField(max_length=128)
    # 同业账户放款户名
    iba_loan_name = models.CharField(max_length=128)
    # 同业账户放款账号
    iba_loan_no = models.CharField(max_length=32)
    # 同业账户收款账户名
    iba_collection_name = models.CharField(max_length=128)
    # 同业账户收款账号
    iba_collection_no = models.CharField(max_length=32)
    # 同业账户预存款账户名
    iba_pre_deposit_name = models.CharField(max_length=128)
    # 同业账户预存款账号
    iba_pre_deposit_no = models.CharField(max_length=128)
    # 机构号
    org_no = models.CharField(max_length=32)
    # 产品名称
    production = models.CharField(max_length=64)
    code = models.CharField(max_length=32)
    area_code = models.CharField(max_length=16)

    def __repr__(self):
        return "商户 {}".format(self.name)

    def __str__(self):
        return "商户 {}".format(self.name)


class Interface(models.Model):
    """
    接口
    """
    # 接口名
    name = models.CharField(max_length=50)
    # 接口路径
    path = models.CharField(max_length=100, null=True)
    # 外键
    business = models.ForeignKey("Business", on_delete=models.CASCADE, related_name="interface")
    # 创建时间
    method = models.CharField(max_length=10)
    create_time = models.DateTimeField(default=now)
    creator = models.ForeignKey("User", on_delete=models.CASCADE)
    code = models.CharField(max_length=32)
    visible = models.BooleanField(default=1)

    def __repr__(self):
        return "接口 {}".format(self.name)

    def __str__(self):
        return "接口 {}".format(self.name)


class Menu(models.Model):
    """
    菜单
    """
    # 菜单名
    name = models.CharField(max_length=50)
    # 菜单路径
    path = models.CharField(max_length=100, null=True)
    # 外键
    business = models.ForeignKey("Business", on_delete=models.CASCADE, related_name="menu")
    # 创建时间
    create_time = models.DateTimeField(default=now)
    creator = models.ForeignKey("User", on_delete=models.CASCADE)
    code = models.CharField(max_length=32)
    visible = models.BooleanField(default=1)

    def __repr__(self):
        return "菜单 {}".format(self.name)

    def __str__(self):
        return "菜单 {}".format(self.name)


class Role(models.Model):
    """
    角色表
    """
    # 角色名
    name = models.CharField(max_length=50)
    # 包含的接口
    interface = models.ManyToManyField("Interface")
    # 包含的菜单
    menu = models.ManyToManyField("Menu")
    # 创建时间
    create_time = models.DateTimeField(default=now)
    creator = models.ForeignKey("User", on_delete=models.CASCADE)
    merchant = models.ForeignKey("Merchant", on_delete=models.CASCADE, blank=True, null=True)
    business = models.ForeignKey("Business", on_delete=models.CASCADE, related_name="roles")
    code = models.CharField(max_length=32)

    def __repr__(self):
        return "角色表 {}".format(self.name)

    def __str__(self):
        return "角色表 {}".format(self.name)


class Business(models.Model):
    """
    业务系统
    """
    # 业务系统名
    name = models.CharField(max_length=50)
    # 生成的 appid
    appid = models.CharField(max_length=50, null=True)
    # 状态，是否启用
    status = models.BooleanField(default=False)
    # 创建时间
    create_time = models.DateTimeField(default=now)
    merchant = models.ManyToManyField("Merchant", related_name="business")
    creator = models.ForeignKey("User", on_delete=models.CASCADE)
    code = models.CharField(max_length=32)

    def __repr__(self):
        return "业务系统 {}".format(self.name)

    def __str__(self):
        return "业务系统 {}".format(self.name)


class User(AbstractBaseUser):
    name = models.CharField(max_length=100, null=True)
    mobile = models.CharField(max_length=11, unique=True)
    sex = models.CharField(max_length=7, null=True)
    password = models.CharField(max_length=100)
    address = models.CharField(max_length=200, null=True)
    avatar = models.CharField(max_length=200, null=True)
    mail = models.EmailField(null=True)
    wechat = models.CharField(max_length=100, null=True)
    qq = models.CharField(max_length=20, null=True)
    # 是否是 superuser
    is_admin = models.BooleanField(default=False)
    create_time = models.DateTimeField(default=now, null=True, blank=True)
    update_time = models.DateTimeField(null=True, blank=True)
    # 一个用户拥有多个角色
    roles = models.ManyToManyField(Role)
    active = models.BooleanField(default=False)    
    merchant = models.ForeignKey("Merchant", on_delete=models.CASCADE, null=True, blank=True)
    code = models.CharField(max_length=32)
 
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['mail', 'mobile']

    def get_name(self):
        return self.name

    def generate_password(self, password):
        self.password = make_password(password)

    def verify_password(self, password):
        return check_password(password, self.password)
    
    def __repr__(self):
        return "用户 {}".format(self.name)

    def __str__(self):
        return "name={}, mobile={}".format(self.name, self.mobile)


class Operation(models.Model):
    """
    用户操作记录
    """
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    operation = models.CharField(max_length=250)
    operate_time = models.DateTimeField(default=now)
    code = models.CharField(max_length=32)

    def __repr__(self):
        return "用户操作 {}".format(self.operation)
    
    def __str__(self):
        return "用户操作 {}".format(self.operation)


class Domain(models.Model):
    """
    domain 表
    """
    domain = models.CharField(max_length=128)
    merchant = models.ForeignKey("Merchant", on_delete=models.CASCADE, related_name="domains")
    business = models.ForeignKey("Business", on_delete=models.CASCADE, related_name="domains")
    create_time = models.DateTimeField(default=now)
    creator = models.ForeignKey("User", on_delete=models.CASCADE)
    code = models.CharField(max_length=32)

    def __repr__(self):
        return "域名 {}".format(self.domain)

    def __str__(self):
        return "域名 {}".format(self.domain)


class Manager(models.Model):
    """
    商户经理
    """
    # 用户与多个小程序绑定时才产生/唯一
    union_id = models.CharField(max_length=100, unique=True ,null=True)
    # 用户与每个小程序绑定以后产生/绑定几个产生几个
    open_id = models.CharField(max_length=100, unique=True ,null=True)
    # 经理名
    name = models.CharField(max_length=50, null=True)
    # 所属商户号 
    merchant_code = models.CharField(max_length=100, null=True)
    #　手机号
    phone = models.CharField(max_length=11, unique=True, null=True)
    #　性别
    sex = models.CharField(max_length=7, null=True)
    # 地址
    address = models.CharField(max_length=200, null=True)
    # 创建时间
    create_time = models.DateTimeField(default=now, null=True)
    # 更新时间
    update_time = models.DateTimeField(null=True, auto_now = True )
    # 创建者
    creator = models.ForeignKey("User", on_delete=models.CASCADE)
    # 状态
    status = models.BooleanField(default=False)
    #密码
    password = models.CharField(max_length=100)
    #身份证号
    id_code = models.CharField(max_length=100, null=True)
    #身份证照片 
    id_img = models.CharField(max_length=100, null=True)
    #大头照
    head_img = models.CharField(max_length=100, null=True)
    #工作gps经度
    work_longitude = models.CharField(max_length=100, null=True)
    #工作gps纬度
    work_latiude = models.CharField(max_length=100, null=True)
    #错误密码输出次数
    pwd_err_count = models.IntegerField(default="0", null=True)
    #因密码错误冻结时间
    pwd_frozen_time = models.DateTimeField(max_length=100, null=True)
    #二维码
    qrcode = models.BinaryField(null=True)
    code = models.CharField(max_length=32, null=True)
    
    def generate_password(self, password):
        self.password = make_password(password)   

    def verify_password(self, password):
        return check_password(password, self.password)         

    def __repr__(self):
        return "商户经理 {}".format(self.name)

    def __str__(self):
        return "商户经理 {}".format(self.name)

class Contract(models.Model):
    """
    签约表
    """
    
    # 签约表单号
    singn_code = models.CharField(max_length=100, unique=True, null=True)
    # 商户经理id
    manager = models.ForeignKey("Manager", on_delete=models.CASCADE)
    #签约用户id(customer) 暂且关联USER
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    #创建时间
    create_time = models.DateTimeField(default=now, null=True)
    #此单提成  
    commission = models.IntegerField(default="0", null=True)
    #签约经度 
    singn_longityde = models.CharField(max_length=100, null=True)
    #签约纬度
    singn_latitude = models.CharField(max_length=100, null=True)
    #经理和用户合照
    img = models.CharField(max_length=100, null=True)
    #是否有效      
    status = models.BooleanField(default=False)
    code = models.CharField(max_length=32, null=True)
    def __repr__(self):
        return "签约表 {}".format(self.singn_code)
    def __str__(self):
        return "签约表 {}".format(self.singn_code)

class ChannelPhone(models.Model): 
    """
    渠道手机映射表
    """
    # 联合id　
    combine_id = models.CharField(max_length=100, null=True)
    # 用户与多个小程序绑定时才产生/唯一
    union_id = models.CharField(max_length=100, unique=True ,null=True)
    # 用户与每个小程序绑定以后产生/绑定几个产生几个
    open_id = models.CharField(max_length=100, unique=True ,null=True)
    create_time = models.DateTimeField(default=now, null=True)
    phone = models.CharField(max_length=11, null=True)




