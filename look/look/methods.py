#обработать 500 ошибки (убрать/зашлушить 404 при отсутсвии элемента)
#добавить универсальности (album get, slbums post, album patch), привести запросы к одному виду (все по назв., все по айди, все по назв и по айди)???
import json
import falcon
from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from .db_create import Base, Album, Author, Song
engine = create_engine("postgresql+psycopg2://dima:8726621331@localhost/dima", echo=True)
engine.connect()
#echo включает ведение лога

session = sessionmaker(bind=engine)
s = session()
def to_dict(self):
    return {c.name: str(getattr(self, c.name, None)) for c in self.__table__.columns}
Base.to_dict = to_dict

class AlbumsH:

    def on_get(self, req, resp):

        l = []
        if 'author' in req.params: #сократить
             for title in s.query(Album.title).filter(Album.author_id == Author.id_author).filter(Author.name == req.params['author']): #req.params['author']):
                 l.append(title[0])
        else:
            if len(req.params) == 0:
                for title in s.query(Album.title):
                    l.append(title[0]) 
        alb = {'albums': l}
        resp.text = json.dumps(alb)
        resp.status = falcon.HTTP_200 #Этот блок кода

    def on_post(self, req, resp):
        form = req.media
        try: #подумать над автоматическим выводом ошибок средствами фреймворка
            album_one = Album(title=form["title"], author_id=form["author_id"], genre=form["genre"], year=form["year"]) #имена
            s.add(album_one) 
            s.commit()
            resp.status = falcon.HTTP_201
        except KeyError:
            resp.text = json.dumps({'title': '400 Bad Request'})
            resp.status = falcon.HTTP_400
        
class AlbumH:

    def on_get(self, req, resp, name): 
        try:
            alb = s.query(Album).get(name)
            resp.text = json.dumps(to_dict(alb)) 
            resp.status = falcon.HTTP_200 
        except AttributeError:
            resp.text = json.dumps({'title': '404 Not Found'})
            resp.status = falcon.HTTP_404
    
    def on_patch(self, req, resp, name): #500 при несуществ. автор_айди
        form = req.media
       # id_1 = list(s.query(Album.id_album).filter(Album.title == name)) #одинаковые назв - редактирует первый
           # album_one = Album(title=form["title"], author_id=form["author_id"], genre=form["genre"], year=form["year"])
        try:
            i = s.query(Album).get(name) # если альбома нет, выводится не та структура данных, которая ожидается (не забыть!!! 404)
            #for key, value in form.items():
            if 'title' in form:   #унив под все случаи
                i.title = form['title']
            if 'author_id' in form:
                i.author_id = form['author_id']
            if 'year' in form:
                i.year = form['year']
            if 'genre' in form:
                i.genre = form['genre']
            s.add(i)
            s.commit()

            l = list(s.query(Album.id_album, Album.title, Album.author_id, Album.genre, Album.year).filter(Album.title == form['title'])) 
            alb = {'id_album': l[0][0], #уменьшить, унив., одинаковые назв., изменить тут и в гет
                'title': l[0][1],
                'author_id': l[0][2],
                'genre': l[0][3],
                'year': l[0][4]
                   }
            resp.text = json.dumps(alb) 
            resp.status = falcon.HTTP_200 
        except:
            resp.text = json.dumps({'title': '400 Bad Request'})
            resp.status = falcon.HTTP_400 
        
    def on_delete(self, req, resp, name):#
        #i = s.query(Album).filter(Album.title == name).one() #если одинаковые назв. альбомов - 500
        try:
            i = s.query(Album).filter(Album.id_album == name).one() #по айди
            s.delete(i)
            s.commit()
            resp.status = falcon.HTTP_204
        except NoResultFound:
            resp.text = json.dumps({'title': '404 Not Found'})
            resp.status = falcon.HTTP_404

       # l = list(s.query(Album.id_album, Album.title, Album.author_id, Album.genre, Album.year).filter(Album.title == name)) #из on_get (сократить(get))
        #alb = {'id_album': l[0][0], #уменьшить, унив., одинаковые назв.
         #       'title': l[0][1],
         #       'author_id': l[0][2],
         #       'genre': l[0][3],
         #       'year': l[0][4]
          #         }
        #resp.text = json.dumps(alb)
        #resp.status = falcon.HTTP_200
#def to_dict(self):
   # return {c.name: getattr(self, c.name, None)
  #          for c in self.__table__.columns}
#Base.to_dict = to_dict
#i1 = (s.query(Album).get(12))
#print (to_dict(i1))