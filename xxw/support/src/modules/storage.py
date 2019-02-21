"""
对象存储
商户 logo icon 上传下载、商户经理身份证正反面图片、头像数据等
"""

from qcloud_cos import CosConfig, CosS3Client
from flask import request, jsonify, Response, stream_with_context
from src import app

oss_url = "xxwfintech-1256721846.cos.ap-shanghai.myqcloud.com"
secret_id = "AKIDxoZAcs2rb9WhgVfez85OXUFrKbmn6QxL"
secret_key = "LWWLzRhBWfcNyNdhZGuU3Rgmuqa9Whjc"
region = "ap-shanghai"
bucket = "xxwfintech-1256721846"
token = ""
config = CosConfig(
    Secret_id=secret_id, Secret_key=secret_key, Region=region, Token=token
)
client = CosS3Client(config)


@app.route("/static/static/run_save_file", methods=["POST"])
def run_save_file():
    """存储文件"""
    file_name = request.form["name"]
    print(request.files["file"])
    if client.object_exists(bucket, file_name):
        return jsonify({"code": "-1", "msg": "文件已存在", "data": False})
    try:
        response = client.put_object(
            Bucket=bucket, Body=request.files["file"], Key=file_name
        )
    # print(response["Etag"])
    # if response["code"] == "NoSuchResource":
        # return jsonify({"code": "-1", "msg": "请上传文件", "data": False})
        return jsonify({"code": "0", "msg": "", "data": {"file_name": file_name}})
    except Exception as e:
        return jsonify({"code": "-1", "msg": "上传失败", "data": False})


@app.route("/static/static/view_file", methods=["POST"])
def view_file():
    """获取文件"""
    file_name = request.json["file_name"]
    if not client.object_exists(bucket, file_name):
        return jsonify({"code": "-1", "msg": "文件不存在", "data": False})
    response = client.get_object(Bucket=bucket, Key=file_name)
    return Response(stream_with_context(response["Body"].get_stream()))
