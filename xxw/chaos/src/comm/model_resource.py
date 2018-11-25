from datetime import datetime

from flask import request
from flask_restful import Resource, reqparse

from src import db, ma
from src.config.msgconfig import Msg

from .logger import logger
from .utils import Schema, validate_schema

filter_op_map = {
    ">": "__gt__",
    "<": "__lt__",
    ">=": "__ge__",
    "<=": "__le__",
    "!=": "__not__",
    "==": "__eq__",
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
    allow_methods = ["get", "post", "put", "delete"]

    def dispatch_request(self, *args, **kwargs):
        if request.method.lower() not in self.allow_methods:
            return Msg.METHOD_NOT_ALLOW, 405
        req = None
        schema = None
        if request.method == "GET":
            schema = self.validate_schemas.get("get")
            req = request.args.to_dict()
        else:
            schema = self.validate_schemas.get(request.method.lower())
            req = request.json
        req = move_space(req)
        if isinstance(schema, Schema):
            data, errors = validate_schema(schema, req)
            if errors:
                logger.info(str(errors))
                return Msg.VALIDATE_ERROR
            self.validate_data = data
        elif isinstance(schema, reqparse.RequestParser):
            parse_req = schema.parse_args()
            strict = self.validate_schemas.get("strict") or ""
            if strict:
                parse_req = schema.parse_args(strict=True)
            self.validate_data = {k: v for k, v in parse_req.items() if v}

        if not self.validate_data:
            self.validate_data = req
        return super().dispatch_request(*args, **kwargs)

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass


class SQLModelResource(BaseResource):
    pk_name = "id"
    model = None
    args_schema = None
    list_schema = None
    detail_schema = None
    exclude = []
    list_fields = []
    update_exclude_fields = []
    update_include_fields = []
    filter_fields = []
    allow_query_all = False
    max_page_size = 100
    default_page_size = 10
    has_is_delete = False
    business_unique_fields = []

    def custom_serializable(self, data):
        return self.list_schema.dump(data).data

    def get_queryset(self, args):
        filter_conditions = []
        for filter_field in self.filter_fields:
            column, op, field, convert_fn = filter_field
            value = args.get(field)
            if value:
                try:
                    value = convert_fn(value)
                except:
                    logger.info(
                        "Cannot convert field {} into {}".format(
                            field, convert_fn.__name__
                        )
                    )
                    return Msg.TYPE_CONVERT_ERROR
                column = getattr(self.model, column)
                operator = filter_op_map[op]
                filter_conditions.append(getattr(column, operator)(value))

        queryset = self.model.query.filter(*filter_conditions)
        if self.has_is_delete:
            queryset = queryset.filter_by(is_delete=False)
        return queryset

    def get(self):
        try:
            page = self.validate_data.get("page")
            if page:
                page = int(page)
            else:
                page = 1
        except:
            logger.info("page should be int")
            return Msg.FIELD_TYPE_ERROR
        try:
            page_size = self.validate_data.get("page_size")
            if page_size:
                page_size = int(page_size)
            else:
                page_size = self.default_page_size
            if page_size > self.max_page_size:
                page_size = self.max_page_size
        except:
            logger.info("page_size should be int")
            return Msg.FIELD_TYPE_ERROR

        queryset = self.get_queryset(self.validate_data)

        if self.allow_query_all and page_size == -1:
            page_size = queryset.count()

        pagination = queryset.paginate(page=page, per_page=page_size)
        results = self.custom_serializable(pagination.items)
        if self.list_fields:
            results = [
                {k: v for k, v in data.items() if k in self.list_fields}
                for data in results
            ]

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
                filter_conditions.append(
                    getattr(column, "__eq__")(self.validate_data.get(field))
                )
            instance = basequery.filter(*filter_conditions).first()
            if instance:
                logger.info("instance is exist")
                return Msg.INSTANCE_IS_EXIST

        instance, errors = self.detail_schema.load(self.validate_data)
        if errors:
            logger.info(errors)
            return Msg.FIELD_TYPE_ERROR
        try:
            db.session.add(instance)
            db.session.commit()
        except Exception as e:
            logger.info(str(e))
            return Msg.DB_COMMIT_ERROR
        return self.detail_schema.dump(instance).data

    def put(self):
        instance = self.model.query.get(self.validate_data.get(self.pk_name))
        if not instance:
            return Msg.INSTANCE_IS_NOT_EXIST
        instance, errors = self.detail_schema.load(self.validate_data, partial=True)
        exclude_fields = set(self.validate_data.keys()) & set(
            self.update_exclude_fields
        )
        include_fields = set(self.validate_data.keys()) - set(
            self.update_include_fields
        )
        if self.update_include_fields and include_fields:
            logger.info("Not allowed to update " + str(include_fields))
            return Msg.NOT_ALLOW_UPDATE_FIELD_IS_EXIST
        if exclude_fields:
            logger.info("Not allowed to update " + str(exclude_fields))
            return Msg.NOT_ALLOW_UPDATE_FIELD_IS_EXIST
        if errors:
            logger.info(errors)
            return Msg.FIELD_TYPE_ERROR
        if hasattr(instance, "update_time"):
            instance.update_time = int(datetime.utcnow().timestamp())
        db.session.commit()
        return self.detail_schema.dump(instance).data

    def delete(self):
        pk = self.validate_data.get(self.pk_name)
        if not pk:
            logger.info("Please pass in the <{}>".format(self.pk_name))
            return Msg.REQUIRED_FIELD_NOT_EXIST
        instance = self.model.query.get(pk)
        if not instance:
            return Msg.INSTANCE_IS_NOT_EXIST
        if self.has_is_delete:
            instance.is_delete = True
        else:
            db.session.delete(instance)
        db.session.commit()


class SQLModelSchemaResource(SQLModelResource):
    def dispatch_request(self, *args, **kwargs):
        meta = type("Meta", (object,), dict(model=self.model))
        schema = type("Schema", (ma.ModelSchema,), dict(Meta=meta))
        self.list_schema = schema(many=True, exclude=self.exclude)
        self.detail_schema = schema(exclude=self.exclude)
        return super().dispatch_request(*args, **kwargs)
