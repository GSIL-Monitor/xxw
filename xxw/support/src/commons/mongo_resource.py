import traceback
from datetime import datetime

from flask import request
from mongoengine import NotUniqueError, ValidationError, DoesNotExist

from flask_restful import Resource
from src import Msg
from src.commons.logger import logger
from src.commons.utils import validate_schema, Schema

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
        try:
            ret = super().dispatch_request(*args, **kwargs)
            return ret
        except NotUniqueError:
            logger.warn(traceback.format_exc())
            return Msg.DATA_EXIST, 400
        except ValidationError as e:
            logger.warn(traceback.format_exc())
            return str(e), 400
        except DoesNotExist:
            logger.warn(traceback.format_exc())
            return Msg.NO_DATA, 400
        except AttributeError as e:
            logger.warn(traceback.format_exc())
            return str(e), 400
        except Exception as e:
            logger.warn(traceback.format_exc())
            return str(e), 400


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

    def get_queryset(self):
        filter_conditions = {}
        for filter_field in self.filter_fields:
            column, op, field, convert_fn = filter_field
            value = request.args.get(field)
            if value:
                try:
                    value = convert_fn(value)
                    if convert_fn.__name__ == 'bool':
                        if value == "true":
                            value = True
                        else:
                            value = False
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
        queryset = self.model.objects.only(*self.list_fields).filter(**filter_conditions)
        return queryset

    def dispatch_request(self, *args, **kwargs):
        if request.method.lower() not in self.allow_methods:
            return Msg.REQUEST_ERROR, 405
        return super().dispatch_request(*args, **kwargs)

    def get(self):
        if request.args.get("id"):
            instance = (
                self.model.objects
                    .only(*self.detail_fields)
                    .filter(id=request.args.get("id"))
                    .first()
            )
            return instance.to_dict()
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
        queryset = self.get_queryset()
        if self.allow_query_all and page_size == -1:
            page_size = queryset.count()
        pagination = queryset.paginate(page=page, per_page=page_size)
        return {
            "total": pagination.total,
            "pages": pagination.pages,
            "page": pagination.page,
            "page_size": pagination.per_page,
            "results": [obj.to_dict() for obj in pagination.items],
        }

    def post(self):
        instance = self.model(**request.json)
        try:
            instance.save()
        except Exception as e:
            logger.info(str(e))
            return str(e), 400
        return instance.to_dict()

    def put(self):
        _id = request.json.pop("id")
        instance = self.model.objects().filter(id=_id).first()
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

        instance.update_time = datetime.utcnow()
        instance.update(**request.json)
        instance.save()
        return instance.to_dict()

    def delete(self):
        instance = self.model.objects().filter(id=request.json.get("id")).first()
        if not instance:
            return Msg.NO_DATA, 400
        instance.delete()