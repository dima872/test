import json
import falcon
from sqlalchemy import desc
from ..db.db_create import Album, Author, session
from .func.functions1 import to_dict, valid_id_not_in_db, json_body, json_body_and_name

s = session()


class AlbumsH:
    def __init__(self, handl):
        self.handl = handl

    def on_get(self, req, resp):
        list_alb = self.handl.albums_get(req.params)
        resp.text = json.dumps({"albums": list_alb})

    @json_body
    def on_post(self, req, resp):
        self.handl.albums_post(req.stream)
        resp.status = falcon.HTTP_201
        resp.text = json.dumps(
            {
                "id_album": s.query(Album.id_album)
                .filter()
                .order_by(desc(Album.id_album))
                .limit(1)[0][0]
            }
        )


class AlbumH:
    def __init__(self, handl):
        self.handl = handl

    @valid_id_not_in_db
    def on_get(self, req, resp, name):
        alb = s.query(Album).get(name)
        resp.text = json.dumps(to_dict(alb))

    @valid_id_not_in_db
    @json_body_and_name
    def on_patch(self, req, resp, name):
        self.handl.album_patch(req.stream, name)
        alb_1 = s.query(Album).get(name)
        resp.text = json.dumps(to_dict(alb_1))

    @valid_id_not_in_db
    @json_body_and_name
    def on_delete(self, req, resp, name):
        self.handl.album_del(name)
        resp.status = falcon.HTTP_204


class HandlerAlbums:
    def albums_get(self, params):
        #  if 'albums' in self.__module__:
        #     flagcollect = 'alb'
        # else:
        #     flagcollect = 'aut'
        strfilt = self.alb_aut_get_filter(params)
        dictalbaut = {i.id_album: i.title for i in s.query(Album).filter(*strfilt)}
        sdictalbaut = dict(sorted(dictalbaut.items(), key=lambda x: x[0]))
        return sdictalbaut

    def albums_get_filter(self, params):
        strfilt = []
        if "author" in params:
            lauthor = params["author"]
            strfilt.append(Album.id_album == Author.id_author)
            if type(lauthor) != list:
                lauthor = lauthor.split()
            for aut in lauthor:
                strfilt.append(Author.Name.ilike(aut.rstrip() + "%"))
        return strfilt

    def albums_post(self, body_j):
        form = json.loads(body_j.read())
        form_valid = self.post_form(form)
        s.add(Album(**form_valid))
        s.commit()
        return

    def post_form(self, form):
        namecolumns = to_dict(Album)
        del namecolumns["id_album"]
        if form.keys() == namecolumns.keys():
            return form
        else:
            raise falcon.HTTPBadRequest

    def album_patch(self, body_j, name):
        form = json.loads(body_j.read())
        form_valid = self.patch_form(form, name)
        s.add(form_valid)
        s.commit()
        return

    def patch_form(self, form, name):
        alb = s.query(Album).get(name)
        albdict = to_dict(alb)
        del albdict["id_album"]
        if set(form.keys()).issubset(set(albdict.keys())):
            if "author_id" in list(form) and form["author_id"] not in [
                str(id_aut[0]) for id_aut in s.query(Author.id_author)
            ]:
                raise falcon.HTTPNotFound("Please, enter an existing author's ID")
            for key in form:
                setattr(alb, key, form[key])
            return alb
        else:
            raise falcon.HTTPBadRequest

    def album_del(self, name):
        i = s.query(Album).filter(Album.id_album == name).one()  # по айди
        s.delete(i)
        s.commit()
        return
