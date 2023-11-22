import falcon
import json
from sqlalchemy.exc import NoResultFound


def to_dict(self):
    return {i.name: str(getattr(self, i.name, None)) for i in self.__table__.columns}


def valid_id_not_in_db(meth):
    def wrapper(self, req, resp, name):
        if name.isdigit() == False:
            raise falcon.HTTPNotFound("Please, enter resource's ID in numeric format")
        try:
            meth(self, req, resp, name)
        except (AttributeError, NoResultFound):
            raise falcon.HTTPNotFound

    return wrapper


def json_body(meth):
    def wrapper(self, req, resp):
        try:
            # if type(json.loads(req.stream.read())) == int:
            #   raise falcon.HTTPBadRequest("Not JSON")
            meth(self, req, resp)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            raise falcon.HTTPBadRequest("Not JSON")

    return wrapper


def json_body_and_name(meth):
    def wrapper(self, req, resp, name):
        try:
            meth(self, req, resp, name)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            raise falcon.HTTPBadRequest("Not JSON")

    return wrapper
