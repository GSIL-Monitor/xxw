from src.apps.common.func import make_response
from src.apps.model.models import User, Role, Interface, Menu, Business
from src.constant import Msg


def role_insert(role, interface, menu):
    try:
        for i in interface:
            inter = Interface.objects.get(code=i)
            role.interface.add(inter)
        for i in menu:
            me = Menu.objects.get(code=i)
            role.menu.add(me)
        role.save()
        return make_response()
    except Interface.DoesNotExist:
        return make_response(code=Msg.INTERFACE_NOT_EXIST, status=400)
    except Menu.DoesNotExist:
        return make_response(code=Msg.MENU_NOT_EXIST, status=400)


def query_dict(id, name, path) -> dict:
    
    res = {}
    if id:
        res.update({"business__code": id})
    if name:
        res.update({"name__contains": name})
    if path:
        res.update({"path__contains": path})
    return res
