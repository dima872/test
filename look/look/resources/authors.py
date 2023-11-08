import json
import falcon
from sqlalchemy import desc
from sqlalchemy.exc import NoResultFound
from ..db.db_create import Author, session
from .func.todict import to_dict

s = session()

class AuthorsH:

    def on_get(self, req, resp):
       
        if req.params == {} or list(req.params.keys())[0].lower() != 'author':
            ListAuthor = [AuthorName[0] for AuthorName in s.query(Author.Name)]
        else:
            ValueName= list(req.params.values())[0]
            if type(ValueName) is list:
                ValueName = ValueName[-1]
            ListAuthor = [AuthorName[0] for AuthorName in s.query(Author.Name).filter(Author.Name.ilike(ValueName + '%'))]
        resp.text = json.dumps({'authors': ListAuthor})

    def on_post(self, req, resp):
       
        form = json.loads(req.stream.read()) #не по json подумать
        NameColumns = to_dict(Author)
        del NameColumns['id_author']
        if form.keys() == NameColumns.keys():
            s.add(Author(**form)) 
            s.commit()
            resp.status = falcon.HTTP_201
            resp.text = json.dumps({'id_author': s.query(Author.id_author).filter().order_by(desc(Author.id_author)).limit(1)[0][0]})#*
        else:
            raise falcon.HTTPBadRequest
        
class AuthorH:

    def on_get(self, req, resp, name): 
       
        if name.isdigit():
            try:
                alb = s.query(Author).get(name)
                resp.text = json.dumps(to_dict(alb)) 
            except AttributeError:
                raise falcon.HTTPNotFound
        else:
            raise falcon.HTTPNotFound('Please, enter your ID in numeric format')
    
    def on_patch(self, req, resp, name):
        if name.isdigit():
            try:
                form = json.loads(req.stream.read())
                aut = s.query(Author).get(name)
                AutDict = to_dict(aut) 
                del AutDict['id_author']
                if set(form.keys()).issubset(set(AutDict.keys())):
                    for key in form.keys():
                        setattr(aut, key, form[key])
                    s.add(aut)
                    s.commit()
                else:
                    raise falcon.HTTPBadRequest
                aut_1 = s.query(Author).get(name)
                resp.text = json.dumps(to_dict(aut_1))
            except AttributeError:
                raise falcon.HTTPNotFound
        else:
            raise falcon.HTTPNotFound('Please, enter your ID in numeric format')
        
    def on_delete(self, req, resp, name):
        if name.isdigit():
            try:
                i = s.query(Author).filter(Author.id_author == name).one() #по айди
                s.delete(i)
                s.commit()
                resp.status = falcon.HTTP_204
            except NoResultFound:
                raise falcon.HTTPNotFound
        else:
            raise falcon.HTTPNotFound('Please, enter your ID in numeric format')