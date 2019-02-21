"""邮件管理"""
from flask import request


from src import db
from src.commons.model_resource import ModelSchemaResource
from src.commons.send_mail import send_mail
from src.models.mail import MailLog, MailTemplate
from src.models.user import TbMerchant


class MailTemplateAPI(ModelSchemaResource):
    model = MailTemplate
    filter_fields = [
        ["merchant", "==", "merchant", str],
        ["template_id", "==", "template_id", str],
        ["template_title", "contains", "template_title", str],
    ]


class MailLogAPI(ModelSchemaResource):
    model = MailLog
    allow_methods = ["get", "post"]
    filter_fields = [
        ["merchant", "==", "merchant", str],
        ["receiver", "==", "email", str],
        ["template_type", "==", "template_type", str],
        ["status", "==", "status", str],
        ["create_time", "<=", "create_time_end", int],
        ["create_time", ">=", "create_time_start", int],
    ]

    def post(self):
        """发送邮件"""
        mail_log, errors = self.detail_schema.load(request.json)
        if errors:
            return errors, 400
        receiver = mail_log.receiver
        template_title = mail_log.template_title
        content = mail_log.content
        sender = TbMerchant.query.get_or_404(int(mail_log.merchant))
        merchant_email = sender.email
        merchant_email_client = sender.email_client
        merchant_email_password = sender.email_password

        try:
            send_mail(merchant_email, receiver, template_title, content, merchant_email_client, merchant_email_password)
            mail_log.status = 1
        except:
            mail_log.status = 0
        db.session.add(mail_log)
        db.session.commit()
        return self.detail_schema.dump(mail_log).data
