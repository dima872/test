import json
import falcon
from sqlalchemy import desc
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from ..db.db_create import Album, Author, session
from .func.todict import to_dict

s = session()

class AlbumsH:

    def on_get(self, req, resp):
        
        if req.params == {} or list(req.params.keys())[0].lower() != 'author':
            ListAlbAuthor = [title[0] for title in s.query(Album.title)]
        else:
            ValueTitle = list(req.params.values())[0]
            if type(ValueTitle) is list:
                ValueTitle = ValueTitle[-1]
            ListAlbAuthor = [title[0] for title in s.query(Album.title).filter(Album.author_id == Author.id_author).filter(Author.name.ilike(ValueTitle + '%'))]
        resp.text = json.dumps({'albums': ListAlbAuthor})

    def on_post(self, req, resp):
        
        form = json.loads(req.stream.read()) #не по json подумать
        NameColumns = to_dict(Album)
        del NameColumns['id_album']
        if form.keys() == NameColumns.keys():
            s.add(Album(**form)) 
            s.commit()
            resp.status = falcon.HTTP_201
            resp.text = json.dumps({'id_album': s.query(Album.id_album).filter().order_by(desc(Album.id_album)).limit(1)[0][0]})#*
        else:
            raise falcon.HTTPBadRequest
        
class AlbumH:

    def on_get(self, req, resp, name): 
        if name.isdigit():
            try:
                alb = s.query(Album).get(name)
                resp.text = json.dumps(to_dict(alb)) 
            except AttributeError:
                raise falcon.HTTPNotFound
        else:
            raise falcon.HTTPNotFound('Please, enter your ID in numeric format')
        
    def on_patch(self, req, resp, name):
        if name.isdigit():
            try:
                form = json.loads(req.stream.read())
                alb = s.query(Album).get(name)
                AlbDict = to_dict(alb) 
                del AlbDict['id_album']
                if form.keys() == AlbDict.keys():
                    for key in form.keys():
                        setattr(alb, key, form[key])
                    s.add(alb)
                    s.commit()
                else:
                    raise falcon.HTTPBadRequest
                alb_1 = s.query(Album).get(name)
                resp.text = json.dumps(to_dict(alb_1))
            except AttributeError:
                raise falcon.HTTPNotFound
        else:
            raise falcon.HTTPNotFound('Please, enter your ID in numeric format') 
        
    def on_delete(self, req, resp, name):
        if name.isdigit():
            try:
                i = s.query(Album).filter(Album.id_album == name).one() #по айди
                s.delete(i)
                s.commit()
                resp.status = falcon.HTTP_204
            except NoResultFound:
                raise falcon.HTTPNotFound
        else:
            raise falcon.HTTPNotFound('Please, enter your ID in numeric format')
