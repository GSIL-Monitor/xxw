"""业务处理(审核)"""

from schema import Schema, Optional, And

from src.commons.model_resource import ModelSchemaResource, BaseResource
from src.models.task import Evt
from src.commons.logger import logger


class AuditEvtAPI(ModelSchemaResource):
    """审核事件"""

    model = Evt
    allow_methods = ["get", "put"]
    filter_fields = [
        ["id", "==", "id", str],
        ["serial_no", "==", "serial_no", str],
        ["merchant_code", "==", "merchant_code", str],
        ["production_code", "==", "production_code", str],
        ["uin", "==", "uin", int],
        ["status", "==", "status", int],
        ["time", ">=", "start_time", int],
        ["time", "<=", "end_time", int],
        ["operator_id", "==", "operator_id", str],
        ["operator", "==", "operator", str],
        ["evt_type", "==", "evt_type", str],
        ["username", "==", "username", str],
        ["phone", "==", "phone", str],
        ["id_card", "==", "id_card", str],
    ]
    list_fields = [
        "serial_no",
        "merchant_code",
        "production_code",
        "evt_type",
        "status",
        "time",
        "uin",
        "username",
        "phone",
        "id_card",
        "update_time",
        "audit_extend_fileds",
        "manager_code",
    ]
    update_include_fields = [
        "status",
        "operator_id",
        "operator",
        "audite_desc",
        "audit_extend_fileds",
    ]
    validate_schemas = {
        "put": Schema(
            {"id": str,
             Optional("audit_extend_fileds"): object,
             "operator_id": str,
             "operator": str,
             Optional("audite_desc"): str,
             "status": And(int, lambda x: x in [0, 1, 2, 3, 4])}
        )
    }


class AllotAuditEvtAPI(BaseResource):
    validate_schemas = {
        "post": Schema(
            {"evt_type": str,
             "operator_id": str,
             "operator": str,
             "count": And(int, lambda x: x >= 0)}
        )}

    def post(self):
        """
        分配审核任务
        """
        evt_type = self.validate_data.get("evt_type")
        operator = self.validate_data.get("operator")
        operator_id = self.validate_data.get("operator_id")
        count = self.validate_data.get("count")
        queryset = Evt.objects(operator_id=None, evt_type=evt_type)
        res_list = queryset.order_by("time")[:count]
        for evt in res_list:
            evt.operator = operator
            evt.operator_id = operator_id
            evt.save()
            logger.info("已分配审核任务 evt_id:%s , rxt(serial_no):%s , 审核类型:%s , 审核人:%s , 审核人id: %s " %
                        (evt.id, evt.serial_no, evt.evt_type, evt.operator, evt.operator_id))
        logger.info("分配成功数量：%s" % len(res_list))
        return {"cnt": len(res_list)}


class AuditEvtAllotCntAPI(BaseResource):
    validate_schemas = {
        "get": Schema({Optional("evt_type"): str})
    }

    def get(self):
        """
        获取任务分配待审核数量，未分配数量, 已分配数量
        """
        evt_type = self.validate_data.get("evt_type")
        queryset = Evt.objects(evt_type=evt_type)
        un_allot_cnt = queryset(operator_id=None).count()
        writing_audit_cnt = queryset(status__in=[0, 4]).count()
        total_count = queryset.count()
        allot_cnt = total_count - un_allot_cnt
        logger.info("获取%s任务分配数量 待审核数量:%s , 未分配数量:%s, 已分配数量:%s" %
                    (evt_type, writing_audit_cnt, un_allot_cnt, allot_cnt))
        return {"un_allot_cnt": un_allot_cnt, "allot_cnt": allot_cnt, "writing_audit_cnt": writing_audit_cnt}
