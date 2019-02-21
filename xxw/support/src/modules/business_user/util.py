from src.models.user import TbInterface, TbMenu, TbBusiness
from src import db, app
from src.commons.constant import Msg


def role_insert(role, interface, menu):
    for i in interface:
        inter = TbInterface.query.filter_by(code=i).first()
        if not inter:
            return Msg.INTERFACE_NOT_EXIST
        role.interface.append(inter)
    for i in menu:
        me = TbMenu.query.filter_by(code=i).first()
        if not me:
            return Msg.MENU_NOT_EXIST
        role.menu.append(me)
    return {}


def query_result(model, id, name, path, page, count):
    condition = [model.name.contains("%{}%".format(name if name else "")),
                 model.path.contains("%{}%".format(path if path else ""))]
    if id:
        condition.append(model.business.has(code=id))
    return model.query.filter(*condition).order_by(model.id.desc()).paginate(page=page, per_page=count)


def batch_delete(model_instance):
    """
    批量删除
    """
    if model_instance:
        for i in model_instance:
            db.session.delete(i)
        return True
    else:
        return False


def get_business_code():
    """通过用户中心 appid 获取用户中心业务系统的 business_code"""

    return TbBusiness.query.filter_by(appid=app.config["USER_CENTER"]).first().code
