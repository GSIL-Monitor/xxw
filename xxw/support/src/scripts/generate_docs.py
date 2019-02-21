import json
from pprint import pprint

import markdown2
from mongoengine import Document

from src import api, app
from src.commons.model_resource import ModelSchemaResourceMeta

from src import api, app
from src.commons.model_resource import ModelSchemaResourceMeta

method_map = {"get": "获取", "post": "创建", "put": "更新", "delete": "删除"}


def _generate_docs():
    docstring = []
    model_type=""
    for resource, router, _ in api.resources:
        if getattr(resource, "model", None):
            if issubclass(resource.model, Document):
                model_type="mongo"
            else:
                model_type = "sql"
            for method in resource.allow_methods:
                docstring.append('\n')
                if model_type == "sql":
                    docstring.append('### '+ method_map[method] + (resource.model.__doc__ or resource.model.__table__.name.upper()))
                elif model_type == "mongo":
                    docstring.append(
                        '### ' + method_map[method] + (resource.model.__doc__ or resource.model._meta['collection']))
                docstring.append(method.upper() +' '+ router[0]+'\n')
                if method == "get":
                    docstring.append("查询参数\n")
                    docstring.append("page : 默认为1 \n")
                    docstring.append("page_size : 默认为10，-1表示提取全部数据 \n")
                    docstring.append("\n".join([i[2] + "\n" for i in resource.filter_fields]))
                    docstring.append("\n返回")
                    docstring.append("\n```json")
                    docstring.append(
                        json.dumps(
                            {
                                "code": 0,
                                "msg": "success",
                                "data": {"count": 16, "pages": 1, "page": 1, "page_size": 20, "results": []},
                            },
                            indent=4,
                        )
                    )
                    docstring.append("```")
                else:
                    docstring.append("返回")
                    docstring.append("```json")
                    docstring.append(json.dumps({"code": 0, "msg": "success", "data": {}}, indent=4))
                    docstring.append("```")
            docstring.append('\n')
            docstring.append('|字段|类型|说明|')
            docstring.append('|---|---|---|')
            if model_type == "sql":
                for column in resource.model.__table__.columns:
                    docstring.append("|%s|%s|%s|"
                        % (column.name, str(column.type), str(column.comment) if column.comment else column.name.upper()))
            elif model_type == "mongo":
                for field,field_type in resource.model._fields.items():
                    verbose_name=field.upper()
                    if hasattr(field_type,'verbose_name'):
                        verbose_name = field_type.verbose_name
                    docstring.append("|%s|%s|%s|"
                        % (field, str(field_type.__class__.__name__)[:-5],verbose_name))
        else:
            docstring.append(
                '### ' + (resource.__doc__ or resource.__name__))
            for method in resource.methods:
                desc = str(getattr(resource, method.lower()).__doc__ or '')
                docstring.append(desc)
                docstring.append(method.upper() + ' ' + router[0] + '\n')
    text = '\n'.join(docstring)
    html = markdown2.markdown(text, extras=["tables","fenced-code-blocks", "toc", "code-friendly"])
    return html


@app.cli.command()
def generate_docs():
    _generate_docs()
