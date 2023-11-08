import json
import falcon
import jwt
from passlib.hash import sha256_crypt
from sqlalchemy.orm import sessionmaker
from .db.db_create import User, engine

engine.connect()
session = sessionmaker(bind=engine)
s = session()
cookie_o = {"name": "my_auth_token",
               "max_age": 36000,
               "path": "/res",
               "http_only": True}
secret = 'vqyvqfqekjn'
class LoginH:

    def on_post(self, req, resp):
        def add_new_jwtoken(resp, email):
            token = jwt.encode({'email': email #добавить что-то еще
                            },
                           secret,
                           algorithm='HS256')#алгоритм необязательно, если 256
            cookie_o["value"] = token #Значение токена
            resp.set_cookie(**cookie_o)
           
        form = json.loads(req.stream.read())
        try:
            email = form["email"]
            password = form["password"]
        except KeyError: 
            raise falcon.HTTPBadRequest

        ListLogin = [i[0] for i in s.query(User.login_1)] #два обращения к базе, попробовать сократить до одного
        if email in ListLogin and sha256_crypt.verify(password, s.query(User.password_1).filter(User.login_1 == email)[0][0]):
            add_new_jwtoken(resp, email)
        else:
            raise falcon.HTTPUnauthorized('Incorrect e-mail or password')

class AuthMiddleware:

    def process_resource(self, req, resp, resource, params):
        if isinstance(resource, LoginH):
            return

        token = req.cookies.get(cookie_o.get("name"))
        print(token)
        if token is None:
            raise falcon.HTTPUnauthorized('Auth token required')
        def valid(token):
            try:
                jwt.decode(token, secret, verify='True', algorithms=['HS256']) #option
                return True
            except:
                return False

        if not valid(token):
            raise falcon.HTTPUnauthorized('Auth token required')

auth_middleware = AuthMiddleware()
login = LoginH()

#s1 = sha256_crypt.hash("password")
#s2 = sha256_crypt.verify("password", s1)