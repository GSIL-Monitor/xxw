客户经理相关接口
-说明s
    A-管理类
    B-登录类
    C-信息类


A-管理类-
-请求token说明
    由B端用户登录成功时生成，管理类请求都在 url 带上 token，字段为： jwt
    -例如：
    https://127.0.0.1:5000/user/id?jwt=xxx.xxx

1）管理-分配客户经理
-url
    /api/v1/manager/manage

-method
    POST

-请求参数(application/json)
    {
        "phone":"1388888888"
    }

-返回参数
    {
        "code":"10000"
        "message":"成功"
        "data":{}
    }
===============================

2)管理-获取客户经理信息
-url
    /api/v1/manager/manage

-method
    GET

-请求参数(application/json)
    无

-返回参数
    {
        "code":"10000"
        "message":"成功"
        "data":{
            "result":[
                {
                "id":"1",
                "name":"张三",
                "phone":"1388888888",
                "sex":"male",
                "address":"成都新希望",
                "code":"j5k4g2lp2dl2m2112",
                "create_time":"2018..",
                "update_time":"2018..",
                "creator":"张三爸爸",
                "status":"0",
                "id_code":"532626199803030933",
                "id_img":"src/media/img",
                "head_img":"src/media/img",
                },
                {
                "id":"2",
                "name":"张四",
                "phone":"1388888882",
                "sex":"male",
                "address":"成都新希望",
                "code":"j5k4g2lp2dl2m2112",
                "create_time":"2018..",
                "update_time":"2018..",
                "creator":"张三爸爸",
                "status":"0",
                "id_code":"532626199803030233",
                "id_img":"src/media/img",
                "head_img":"src/media/img",
                },
                {....},
                {....},
                ......
            ]
        }
    }
===============================

3）管理-编辑客户经理信息
-url
    /api/v1/manager/manage

-method
    PUT

-请求参数(application/json)
    {
        "manager_code"="j12h534ndfiwp45jd", #必传-定位编辑端对象
        "name"="张三",                       #根据编辑需求选传
        "sex"="male",                       #目前提供左侧参数
        "address"="凛兰之巅"
        "id_img"="src/media/img",
        "head_img"="src/media/img",
    }

-返回参数
    {
        "code":"10000"
        "message":"成功"
        "data":{}
    }
===============================

4）管理-重置密码
-url
    /api/v1/manager/manage/resetpassword

-method
    PUT

-请求参数(application/json)
    {
        "manager_code"="j12h534ndfiwp45jd", #必传-定位重置密码对象        
    }

-返回参数
    {
        "code":"10000"
        "message":"成功"
        "data":{}
    }
===============================
===============================

B-登录类-
1）登录-客户经理登录
-说明
    -当我们只有一个小程序的时候，用户这个时候只有open_id,
    -当多个小程序的时候，用户有唯一的union_id和多个open_id
    -kind（登录方式）有三种
        1）手机+密码
        2）union_id+open_id+登录密码
        3）手机号+短信验证码
    -方式 2）说明
    -我这边会把 union_id + open_id 两个联合id会组成一个叫combine_id 形成唯一键并映射手机号
    -若combine_id无手机号映射，则返回登录失败，需进行手机绑定

-url
    /api/v1/manager/sign_in

-method
    POST

-请求参数(application/json)
    {
        "phone":"18206708942",  # kind为1,3时必传，
        "union_id": "1111",     # kind为2时必传，
        "open_id":"2222",       # kind为2时必传，
        "pwd":"123456",         # kind为3时不传，
        "kind":"1",             # 1-手机+密码 2-union_id+open_id+登录密码 3-手机号+短信验证码
    }

-返回参数
    {
        "code":"10000"
        "message":"成功"
        "data":{
            'token':'cd69661deb914212ab9e43672c21685',
            'name': 'A'
        }
    }
===============================

2）登录-忘记密码
-说明
    调用发送验证码以后传 验证码和电话号码进行验证
-url
    /api/v1/manager/manage/sign_in/forgetpassword

-method
    PUT

-请求参数(application/json)
    {
        "phone":"13888888888",
        "verify_code":"74757"      
    }

-返回参数
    {
        "code":"10000"
        "message":"成功"
        "data":{}
    }
===============================
===============================

C-客户经理信息类-
-请求token说明
    由客户经理登录成功时生成，信息类请求都在 url 带上 token，字段为： jwt
    -例如：
    https://127.0.0.1:5000/user/id?jwt=xxx.xxx

1）信息-获取获取当前客户经理信息

-url
    /api/v1/manager/manage/info

-method
    GET

-请求参数(application/json)
    无

-返回参数
    {
        "code":"10000"
        "message":"成功"
        "data":{}
    }
===============================

2）信息-修改当前客户经理信息

-url
    /api/v1/manager/manage/info

-method
    PUT

-请求参数(application/json)
    {
        "address":"琳兰之巅",       #暂定可修改项为左侧
        "id_img":"src/media/img"，
        "head_img":"src/media/img"      
    }

-返回参数
    {
        "code":"10000"
        "message":"成功"
        "data":{}
    }
===============================

3）信息-获取获取当前客户经理的签约信息

-url
    /api/v1/manager/manage/info/contract

-method
    GET

-请求参数(application/json)
    无

-返回参数
    {
        "code":"10000"
        "message":"成功"
        "data":{}
    }
===============================

4）信息-获取获取当前客户经理的总体成

-url
    /api/v1/manager/manage/info/contract/commission

-method
    GET

-请求参数(application/json)
    无

-返回参数
    {
        "code":"10000"
        "message":"成功"
        "data":{}
    }
===============================





