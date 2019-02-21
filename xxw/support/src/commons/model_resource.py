from src.commons.logger import logger
from datetime import datetime

from flask import request
from mongoengine import NotUniqueError, ValidationError, DoesNotExist

from flask_restful import Resource, reqparse
from flask_sqlalchemy.model import DefaultMeta
from marshmallow_mongoengine import ModelSchema
import traceback
from src import db, ma, Msg
from src.commons.utils import validate_schema, Schema
from flask_restful import reqparse

filter_op_map = {
    ">": "__gt__",
    "<": "__lt__",
    ">=": "__ge__",
    "<=": "__le__",
    "!=": "__not__",
    "==": "__eq__",
    "contains": "contains",
    "in": "in_",
    "re":"op"     #正则 value为匹配的表达式
}

mongo_filter_op_map = {
    ">": "__gt",
    "<": "__lt",
    ">=": "__gte",
    "<=": "__lte",
    "!=": "__ne",
    "==": "",
    "contains": "contains",
}


def move_space(data: dict):
    if data:
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = str.strip(v)
        return data
    return {}


class BaseResource(Resource):
    validate_data = None
    validate_schemas = {}

    def dispatch_request(self, *args, **kwargs):
        req = None
        schema = None
        if request.method == "GET":
            schema = self.validate_schemas.get("get")
            req = request.args.to_dict()
        else:
            schema = self.validate_schemas.get(request.method.lower())
            req = request.json
        if isinstance(schema, Schema):
            data, errors = validate_schema(schema, move_space(req))
            if errors:
                logger.info(str(errors))
                return str(errors), 400           
            self.validate_data = data
        elif isinstance(schema, reqparse.RequestParser):
            parse_req = schema.parse_args()
            strict = self.validate_schemas.get("strict") or ""
            if strict:
                parse_req = schema.parse_args(strict=True)
            self.validate_data = {k: v for k, v in parse_req.items() if v}
        try:
            ret = super().dispatch_request(*args, **kwargs)
            return ret
        except NotUniqueError:
            logger.warn(traceback.format_exc())
            return Msg.DATA_EXIST, 400
        except ValidationError:
            logger.warn(traceback.format_exc())
            return Msg.PARAMS_ERROR, 400
        except DoesNotExist:
            logger.warn(traceback.format_exc())
            return Msg.NO_DATA, 400
        except AttributeError:
            logger.warn(traceback.format_exc())
            return Msg.PARAMS_ERROR, 400
        except Exception:
            logger.warn(traceback.format_exc())
            return Msg.UNKNOWN, 400


class MongoModelResource(BaseResource):
    model = None
    args_schema = None
    list_schema = None
    detail_schema = None
    allow_methods = ["get", "post", "put", "delete"]
    update_exclude_fields = []
    update_include_fields = []
    list_fields = []
    detail_fields = []
    filter_fields = []
    max_page_size = 100
    default_page_size = 10
    allow_query_all = False

    def get_queryset(self, args):
        filter_conditions = {}
        for filter_field in self.filter_fields:
            column, op, field, convert_fn = filter_field
            value = args.get(field)
            if value:
                try:
                    value = convert_fn(value)
                except:
                    return (
                        "Cannot convert field {} into {}".format(
                            field, convert_fn.__name__
                        ),
                        400,
                    )
                operator = mongo_filter_op_map[op]
                filter_conditions[
                    "{column}{operator}".format(column=column, operator=operator)
                ] = value
        return self.model.objects().only(*self.list_fields).filter(**filter_conditions)

    def dispatch_request(self, *args, **kwargs):
        if request.method.lower() not in self.allow_methods:
            return Msg.REQUEST_ERROR, 405
        return super().dispatch_request(*args, **kwargs)

    def get(self):
        if request.args.get("id"):
            instance = (
                self.model.objects()
                .only(*self.detail_fields)
                .filter(id=request.args.get("id"))
                .first()
            )
            return self.detail_schema.dump(instance).data
        try:
            page = request.args.get("page")
            if page:
                page = int(page)
            else:
                page = 1
        except Exception:
            return "page should be int", 400
        try:
            page_size = request.args.get("page_size")
            if page_size:
                page_size = int(page_size)
            else:
                page_size = self.default_page_size
            if page_size > self.max_page_size:
                page_size = self.default_page_size
        except Exception:
            return "page_size should be int", 400
        queryset = self.get_queryset(move_space(request.args.to_dict()))
        if not queryset:
            return {
                "total": 0,
                "pages": 0,
                "page": 0,
                "page_size": 0,
                "results": []
            }
        if self.allow_query_all and page_size == -1:
            page_size = queryset.count()
        pagination = queryset.paginate(page=page, per_page=page_size)
        return {
            "total": pagination.total,
            "pages": pagination.pages,
            "page": pagination.page,
            "page_size": pagination.per_page,
            "results": self.list_schema.dump(pagination.items).data,
        }

    def post(self):
        instance, errors = self.detail_schema.load(request.json)
        if errors:
            logger.info(str(errors))
            return str(errors), 400
        instance.save()
        return self.detail_schema.dump(instance).data

    def put(self):
        _id = request.json.pop("id")
        instance = self.model.objects(id=_id).filter(id=_id).first()
        if not instance:
            return Msg.NO_DATA, 400
        exclude_fields = set(request.json.keys()) & set(self.update_exclude_fields)
        include_fields = set(request.json.keys()) - set(self.update_include_fields)
        if self.update_include_fields and include_fields:
            logger.info("Not Allowed To Update " + str(include_fields))
            return "Not allowed to update " + str(include_fields), 400
        if exclude_fields:
            logger.info("Not Allowed To Update " + str(exclude_fields))
            return "Not allowed to update " + str(exclude_fields), 400
        instance, errors = self.detail_schema.update(instance, request.json)
        if errors:
            logger.info(str(errors))
            return str(errors), 400
        if getattr(instance, "update_time", None):
            instance.update_time = int(datetime.utcnow().timestamp())
        instance.save()
        return self.detail_schema.dump(instance).data

    def delete(self):
        instance = self.model.objects().filter(id=request.json.get("id")).first()
        if not instance:
            return Msg.NO_DATA, 400
        instance.delete()
        return {}


class MongoModelSchemaResource(MongoModelResource):
    def dispatch_request(self, *args, **kwargs):
        meta = type("Meta", (object,), dict(model=self.model))
        schema = type("Schema", (ModelSchema,), dict(Meta=meta))
        self.list_schema = schema(many=True)
        self.detail_schema = schema()
        ret = super().dispatch_request(*args, **kwargs)
        return ret


class SQLModelResource(BaseResource):
    model = None                  
    args_schema = None
    allow_methods = ["get", "post", "put", "delete"]
    list_schema = None            #生成modelschema-many
    detail_schema = None          #生成modelschema 
    exclude = []                  #生成modelschema时除去的属性/字段 GET，PUT，POST都不会影响到该字段   
    filter_fields = []            #GET方法可筛选的过滤条件   
    list_fields = []              #GET方法时要展示的字段
    allow_query_all = False       #GET方法允许查询所有/ 即page_size 为-1时查询全部
    max_page_size = 100           #GET方法分页时最大单页显示数 超过100设定值为100
    default_page_size = 10        #GET方法分页时默认的单页显示数   
    update_exclude_fields = []    #PUT方法不可以修改的字段
    update_include_fields = []    #PUT方法可以进行修改的字段
    put_select = ["id","id"]      #PUT方法定位到instans的条件 默认id   
    has_is_delete = False         
    business_unique_fields = []

    def get_queryset(self, args):
        filter_conditions = []
        for filter_field in self.filter_fields:
            column, op, field, convert_fn = filter_field
            value = args.get(field)
            if value:
                try:
                    value = convert_fn(value)
                except:
                    return (
                        "Cannot convert field {} into {}".format(
                            field, convert_fn.__name__
                        ),
                        400,
                    )
                column = getattr(self.model, column)
                operator = filter_op_map[op]
                if operator == "op":
                    filter_conditions.append(getattr(column, operator)("regexp")(r""+value))
                else:    
                    filter_conditions.append(getattr(column, operator)(value))
        return self.model.query.filter(*filter_conditions)

    def dispatch_request(self, *args, **kwargs):

        if request.method.lower() not in self.allow_methods:
            return Msg.REQUEST_ERROR, 405
        return super().dispatch_request(*args, **kwargs)

    def get(self):
        try:
            page = request.args.get("page")
            if page:
                page = int(page)
            else:
                page = 1
        except:
            return "page should be int", 400
        try:
            page_size = request.args.get("page_size")
            if page_size:
                page_size = int(page_size)
            else:
                page_size = self.default_page_size
            if page_size > self.max_page_size:
                page_size = self.max_page_size
        except:
            return "page_size should be int", 400

        queryset = self.get_queryset(move_space(request.args.to_dict()))

        if self.has_is_delete:
            queryset = queryset.filter_by(is_delete=False)

        if self.allow_query_all and page_size == -1:
            page_size = queryset.count()

        pagination = queryset.paginate(page=page, per_page=page_size)
        results = self.list_schema.dump(pagination.items).data
        if self.list_fields:
            results = [{k: v for k, v in data.items() if k in self.list_fields} for data in results]

        return {
            "total": pagination.total,
            "pages": pagination.pages,
            "page": pagination.page,
            "page_size": pagination.per_page,
            "results": results,
        }

    def post(self):
        filter_conditions = []
        if self.business_unique_fields:
            basequery = self.model.query
            if self.has_is_delete:
                basequery = basequery.filter_by(is_delete=False)
            for field in self.business_unique_fields:
                column = getattr(self.model, field)
                filter_conditions.append(getattr(column, '__eq__')(request.json.get(field)))
            instance = basequery.filter(*filter_conditions).first()
            if instance:
                logger.info("template is exist")
                return "template is exist", 400

        instance, errors = self.detail_schema.load(request.json)
        if errors:
            logger.info(errors)
            return errors, 400
        try:
            db.session.add(instance)
            db.session.commit()
        except Exception as e:
            logger.info(str(e))
            return str(e), 400
        return self.detail_schema.dump(instance).data

    def put(self):
        #instance = self.model.query.get_or_404(request.json.get("id"))
        #if self.put_select:
        instance = self.model.query.filter(
            getattr(self.model, self.put_select[0]) == request.json.get(self.put_select[1])).first() 
        if not instance :
            return "Not find any date", 400
        instance, errors = self.detail_schema.load(request.json, instance=instance, partial=True)
        exclude_fields = set(request.json.keys()) & set(self.update_exclude_fields)
        include_fields = set(request.json.keys()) - set(self.update_include_fields)
        if self.update_include_fields and include_fields:
            logger.info("Not allowed to update " + str(include_fields))
            return "Not allowed to update " + str(include_fields), 400
        if exclude_fields:
            logger.info("Not allowed to update " + str(exclude_fields))
            return "Not allowed to update " + str(exclude_fields), 400
        if errors:
            logger.info(errors)
            return errors, 400
        if hasattr(instance, "update_time"):
            instance.update_time = int(datetime.utcnow().timestamp())
        db.session.commit()
        return self.detail_schema.dump(instance).data

    def delete(self):
        instance = self.model.query.get_or_404(request.json.get("id"))
        if self.has_is_delete:
            instance.is_delete = True
        else:
            db.session.delete(instance)
        db.session.commit()
        return "success!"


class SQLModelSchemaResource(SQLModelResource):
    def dispatch_request(self, *args, **kwargs):
        meta = type("Meta", (object,), dict(model=self.model))
        schema = type("Schema", (ma.ModelSchema,), dict(Meta=meta))
        self.list_schema = schema(many=True, exclude=self.exclude)
        self.detail_schema = schema(exclude=self.exclude)
        return super().dispatch_request(*args, **kwargs)


class ModelResourceMeta(type):
    """ModelResourceMeta"""

    def __new__(cls, name, bases, attrs):
        model = attrs.get("model")
        if model is None:
            return super().__new__(cls, name, bases, attrs)
        if isinstance(model, DefaultMeta):
            return type(name, (SQLModelResource,), attrs)
        else:
            return type(name, (MongoModelResource,), attrs)


class ModelSchemaResourceMeta(type):
    """ModelSchemaResourceMeta"""

    def __new__(cls, name, bases, attrs):
        model = attrs.get("model")
        if model is None:
            return super().__new__(cls, name, bases, attrs)
        if isinstance(model, DefaultMeta):
            return type(name, (SQLModelSchemaResource,), attrs)
        else:
            return type(name, (MongoModelSchemaResource,), attrs)


class ModelSchemaResource(metaclass=ModelSchemaResourceMeta):
    """ModelSchemaResource"""


class ModelResource(metaclass=ModelResourceMeta):
    """ModelResource"""


def get_data(instance, model, exclude=[], only=None, pure=False):
    """
    参数说明
    1）instance: 查询的结果集
    2）model: 序列化对应的ModelSchema
    3）exclude: ModelSchema的排除字段
    4）only: ModelSchema仅有字段设置
    5）pure: (纯净) 为ture时  会直接返回dump以后的schema数据 
                   为false时 返回分页数据
    """
    meta = type("Meta", (object,), dict(model=model))
    schema = type("Schema", (ma.ModelSchema,), dict(Meta=meta))
    list_schema = schema(many=True, exclude=exclude, only=only)
    detail_schema = schema(exclude=exclude, only=only)
    if pure == True:
        data2 = list_schema.dump(instance).data
        return data2
    if not hasattr(instance, "__iter__"):
        data = detail_schema.dump(instance).data
        return {"results": data}
    page = int(request.args.get("page") or 1)
    page_size = int(request.args.get("page_size") or 10)
    if page_size == -1:
        page_size = instance.count()
    pagination = instance.paginate(page=page, per_page=page_size)
    data = list_schema.dump(pagination.items).data
    return {
        "total": pagination.total,
        "pages": pagination.pages,
        "page": pagination.page,
        "page_size": pagination.per_page,
        "results": data,
    }


def post_data(json, model, exclude=[], only=None):
    """
    参数说明：
    1）json: 需要序列化的数据
    2）model: 序列化对应的ModelSchema
    3）exclude: ModelSchema的排除字段
    4）only: ModelSchema仅有字段设置
    """
    meta = type("Meta", (object,), dict(model=model))
    schema = type("Schema", (ma.ModelSchema,), dict(Meta=meta))
    list_schema = schema(many=True, exclude=exclude, only=only)
    detail_schema = schema(exclude=exclude, only=only)
    instance, errors = detail_schema.load(json)
    db.session.add(instance)
    db.session.commit()
    return instance


def put_data(instance, json, model, exclude=[], only=None):
    """
    参数说明：
    1）instance: 查询的结果集
    2）json: 需要序列化的数据
    3）model: 序列化对应的ModelSchema
    4）exclude: ModelSchema的排除字段
    5）only: ModelSchema仅有字段设置
    """
    meta = type("Meta", (object,), dict(model=model))
    schema = type("Schema", (ma.ModelSchema,), dict(Meta=meta))
    detail_schema = schema(exclude=exclude, only=only)
    instance, errors = detail_schema.load(json, instance=instance ,partial=True)
    if getattr(instance, "update_time", None):
        instance.update_time = int(datetime.utcnow().timestamp())
    db.session.commit()
    return instance
