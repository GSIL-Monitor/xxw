from flask_mail import Mail, Message

from src import app


def send_mail(sender, to, subject, template, mail_client, mail_password):
    """

    :param sender: 发送者邮箱
    :param to: 接收者邮箱
    :param subject: 邮件标题
    :param template: 邮件内容
    :param mail_client: 商户邮箱服务器
    :param mail_password: 商户邮箱授权码
    :return:
    """
    msg = Message(subject, sender=sender, recipients=[to])
    msg.body = template
    app.config["MAIL_SERVER"] = mail_client
    app.config["MAIL_USERNAME"] = sender
    app.config["MAIL_PASSWORD"] = mail_password
    mail = Mail(app)
    mail.send(msg)
