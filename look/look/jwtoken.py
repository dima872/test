import json
import falcon
import jwt
from passlib.hash import sha256_crypt
from db.db_create import User, session
from resources.func.functions1 import json_body

s = session()
cookie_o = {"name": "auth_token", "max_age": 3600, "path": "/res", "http_only": True}
secret = "vqyvqfqekjns"


class LoginH:
    @json_body
    def on_post(self, req, resp):
        cookie = self.add_new_jwtoken(req.stream)
        resp.set_cookie(**cookie)

    def add_new_jwtoken(self, body_j):
        email = self.valid_email_password(body_j)
        token = jwt.encode(
            {"email": email}, secret, algorithm="HS256"  # добавить что-то еще
        )  # алгоритм необязательно, если 256
        cookie_o["value"] = token  # Значение токена
        return cookie_o

    def valid_email_password(self, body_j):
        list_login = [
            i[0] for i in s.query(User.login_1)
        ]  # два обращения к базе, попробовать сократить до одного
        email, passw = self.get_email_password(body_j)
        if email in list_login and sha256_crypt.verify(
            passw, s.query(User.password_1).filter(User.login_1 == email)[0][0]
        ):
            return email
        else:
            raise falcon.HTTPUnauthorized("Incorrect e-mail or password")

    def get_email_password(self, body_j):
        form = json.loads(body_j.read())
        try:
            email = form["email"]
            password = form["password"]
            return email, password
        except (KeyError, TypeError):
            raise falcon.HTTPBadRequest("The required field is missing")


class AuthMiddleware:
    def process_resource(self, req, resp, resource, params):
        if isinstance(resource, LoginH):
            return
        token = self.get_token(req)
        if not self.valid_token(token):
            raise falcon.HTTPUnauthorized("Incorrect token, auth token required")

    def get_token(self, req):
        token_1 = req.cookies.get(cookie_o.get("name"))
        print(token_1)
        if token_1 is None:
            raise falcon.HTTPUnauthorized("Auth token required")
        return token_1

    def valid_token(self, token):
        try:
            jwt.decode(token, secret, verify="True", algorithms=["HS256"])  # option
            return True
        except:
            return False


# s1 = sha256_crypt.hash("password")
# s2 = sha256_crypt.verify("password", s1)
