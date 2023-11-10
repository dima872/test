import json
import falcon
from sqlalchemy import desc
from sqlalchemy.exc import NoResultFound
from ..db.db_create import Album, Author, session
from .func.todict import to_dict

s = session()

class AlbumsH:

    def on_get(self, req, resp):
        
        if req.params == {} or list(req.params.keys())[0].lower() != 'author':
            
            DictAlbAuthor = {i.id_album: i.title for i in s.query(Album)}
        else:
            ValueTitle = list(req.params.values())[0]
            if type(ValueTitle) is list:
                ValueTitle = ValueTitle[-1]
            DictAlbAuthor = {i.id_album: i.title for i in s.query(Album).filter(Album.author_id == Author.id_author).filter(Author.Name.ilike(ValueTitle + '%'))}
        SDictAlbAut = dict(sorted(DictAlbAuthor.items(), key=lambda x: x[0]))
        resp.text = json.dumps({'albums': SDictAlbAut})
        
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
            raise falcon.HTTPNotFound("Please, enter album's ID in numeric format")
        
    def on_patch(self, req, resp, name):
        if name.isdigit():
            try:
                form = json.loads(req.stream.read())
                alb = s.query(Album).get(name)
                AlbDict = to_dict(alb) 
                del AlbDict['id_album']
                if set(form.keys()).issubset(set(AlbDict.keys())):
                    print(form)
                    if 'author_id' in list(form.keys()) and form['author_id'] not in [str(id_aut[0]) for id_aut in s.query(Author.id_author)]:
                        raise falcon.HTTPNotFound("Please, enter an existing author's ID")
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
            raise falcon.HTTPNotFound("Please, enter album's ID in numeric format") 
        
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
            raise falcon.HTTPNotFound("Please, enter album's ID in numeric format")
