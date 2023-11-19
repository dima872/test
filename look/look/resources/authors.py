import json
import falcon
from sqlalchemy import desc
from ..db.db_create import Author, Album, session
from .func.functions1 import to_dict, valid_id_not_in_db, json_body, json_body_and_name

s = session()


class AuthorsH:
    def __init__(self, handl):
        self.handl = handl

    def on_get(self, req, resp):
        list_aut = self.handl.autors_get(req.params)
        resp.text = json.dumps({"authors": list_aut})

    @json_body
    def on_post(self, req, resp):
        self.handl.autors_post(req.stream)
        resp.status = falcon.HTTP_201
        resp.text = json.dumps(
            {
                "id_author": s.query(Author.id_author)
                .filter()
                .order_by(desc(Author.id_author))
                .limit(1)[0][0]
            }
        )


class AuthorH:
    def __init__(self, handl):
        self.handl = handl

    @valid_id_not_in_db
    def on_get(self, req, resp, name):
        aut = s.query(Author).get(name)
        resp.text = json.dumps(to_dict(aut))

    @valid_id_not_in_db
    @json_body_and_name
    def on_patch(self, req, resp, name):
        self.handl.autor_patch(req.stream, name)
        alb_1 = s.query(Album).get(name)
        resp.text = json.dumps(to_dict(alb_1))

    @valid_id_not_in_db
    @json_body_and_name
    def on_delete(self, req, resp, name):
        self.handl.autor_del(name)
        resp.status = falcon.HTTP_204


class HandlerAuthors:
    def autors_get(self, params):
        strfilt = self.autors_get_filter(params)
        dictalbaut = {i.id_author: i.Name for i in s.query(Author).filter(*strfilt)}
        sdictalbaut = dict(sorted(dictalbaut.items(), key=lambda x: x[0]))
        return sdictalbaut

    def autors_get_filter(self, params):
        strfilt = []
        if "author" in params:
            lauthor = params["author"]
            if type(lauthor) != list:
                lauthor = lauthor.split()
            for aut in lauthor:
                strfilt.append(Author.Name.ilike(aut.rstrip() + "%"))
        return strfilt

    def autors_post(self, body_j):
        form = json.loads(body_j.read())
        form_valid = self.post_form(form)
        s.add(Author(**form_valid))
        s.commit()
        return

    def post_form(self, form):
        namecolumns = to_dict(Author)
        del namecolumns["id_author"]
        if form.keys() == namecolumns.keys():
            return form
        else:
            raise falcon.HTTPBadRequest

    def autor_patch(self, body_j, name):
        form = json.loads(body_j.read())
        form_valid = self.patch_form(form, name)
        s.add(form_valid)
        s.commit()
        return

    def patch_form(self, form, name):
        aut = s.query(Author).get(name)
        autdict = to_dict(aut)
        del autdict["id_author"]
        if set(form.keys()).issubset(set(autdict.keys())):
            for key in form:
                setattr(aut, key, form[key])
            return aut
        else:
            raise falcon.HTTPBadRequest

    def autor_del(self, name):
        i = s.query(Author).filter(Author.id_author == name).one()  # по айди
        s.delete(i)
        s.commit()
        return
