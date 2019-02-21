common_code_post = {
    "type": "reject_code",
    "code": "4001",
    "name": "error_data",
    "desc": "error_data",
    "operator_id": "xxz",
    "operator": "xxz"
}
common_code_put = {"operator_id": "xxxxx", "code": "500", "name": "timeout",
                   "desc": "timeout", "type": "unknown_error"}
common_code_get = {
    "type": "reject_code",
    "code": "400",
    "name": "error_data",
    "desc": "error_data",
    "operator_id": "xxz",
    "operator": "xxz"
}

industry_position_post = {
    "industry_code": "Z09",
    "industry_name": "教育机构",
    "position_code": "0001",
    "position_name": "t班主任",
    "rank": "2",
    "operator": "xxz",
    "operator_id": "xxz",
}
industry_position_put = {"industry_name": "政府机构", "position_name": "主任",
                         "rank": "1", "operator_id": "xxxxz", "operator": "xxz"}
industry_position_get = {"industry_code": "Z09", "position_code": "0001"}

auto_trans_conf_post = {"rules": ["1", "2", "3"], "error_codes": ["1", "2"],
                        "count": 1, "operator_id": "xxz", "operator": "xxz"}
auto_trans_conf_put = {"rules": ["5", "2", "3"], "error_codes": ["9", "2"],
                       "count": 2, "operator_id": "xxxxx", "operator": "xxz"}
risk_args_post = {
    "merchant_code": "123",
    "production_code": "123",
    "rule_desc": "234234",
    "status": True,
    "rule_conf": {
        "age_range": [24, 37],
        "degrees": [
            "postgraduate",
            "undergraduate"
        ],
        "selected_industries_and_professions": [
            {
                "industry_code": "S",
                "industry_name": "水、电、煤、气、烟草、石化行业",
                "professions": [
                    {
                        "position_code": "901",
                        "position_name": "企业法人；公司高级管理人员"
                    }
                ]
            },
            {
                "industry_code": "Z",
                "industry_name": "政府机关/社会团体/事业单位/非盈利性机构",
                "professions": [
                    {
                        "position_code": "901",
                        "position_name": "副厅；厅局级以上"
                    }
                ]
            }
        ]
    },
    "rule_name": "测试",
    "lend_range": [15, 42]
}

risk_args_put = {

    "rule_desc": "2334",
    "status": True,
    "rule_conf": {
        "age_range": [23, 37],
        "degrees": [
            "postgraduate",
            "undergraduate"
        ],
        "selected_industries_and_professions": [
            {
                "industry_code": "S",
                "industry_name": "水、电、煤、气、烟草、石化行业",
                "professions": [
                    {
                        "position_code": "901",
                        "position_name": "企业法人；公司高级管理人员"
                    }
                ]
            },
            {
                "industry_code": "Z",
                "industry_name": "政府机关/社会团体/事业单位/非盈利性机构",
                "professions": [
                    {
                        "position_code": "901",
                        "position_name": "副厅；厅局级以上"
                    }
                ]
            }
        ]
    },
    "rule_name": "测试修改",
    "lend_range": [16, 42]
}

risk_args_get = {"merchant_code": "123",
                 "production_code": "123",
                 "rule_name": "测试"}

sms_template_post = {"template": " 您的验证码为：{1}，{2}分钟内有效，请继续完成操作。任何人索取验证码均为诈骗，切勿泄露！同时切勿通过中介申请，谨防诈骗！",
                     "production_code": "qyd",
                     "is_valid": False,
                     "price": "13.00",
                     "merchant_code": "00000005",
                     "template_title": "用户注册",
                     "template_type_code": 1,
                     "template_content_code": "999999",
                     "production_name": "aa"}

sms_template_put = {"is_valid": True,
                    "price": "14.00",
                    "template_title": "用户登陆",
                    "template_type_code": 2,
                    }

sms_template_get = {"merchant_code": "00000005",
                    "production_code": "qyd",
                    "production_name": "aa",
                    "template_content_code": "999999",
                    "template_title": "用户注册"
                    }

sms_template_type_post = {"template_type": "用户注册",
                          "code": "8"
}

sms_template_type_put = {"template_type": "用户登录"}

sms_template_type_get = {"code": "8"}
