#убрать создание таблицы с данными из db при каждом запуске прил (ошибки при удалении альбома с айди, используемом в сонг, и новом запуске)
#обработать 500 ошибки (убрать/зашлушить 404 при отсутсвии элемента)
#добавить универсальности (album get, slbums post, album patch), привести запросы к одному виду (все по назв., все по айди, все по назв и по айди)???
import json
import falcon
from .db import *

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
        album_one = Album(title=form["title"], author_id=form["author_id"], genre=form["genre"], year=form["year"]) #имена
        s.add(album_one) 
        s.commit()
        resp.status = falcon.HTTP_201
        
class AlbumH:

    def on_get(self, req, resp, name):  
        l = list(s.query(Album.id_album, Album.title, Album.author_id, Album.genre, Album.year).filter(Album.title == name))  #?вывод всех (all), одинаковые альбомы - выводит 1-й в списке, подумать над другим выводом (по айди)
        #l = list(s.query(Album.id_album, Album.title, Album.author_id, Album.genre, Album.year).filter(Album.id_album == name)) #по айди, добавить независимоть от регистра, если вызов по назв.
        alb = {'id_album': l[0][0], #уменьшить, унив., одинаковые назв.
                'title': l[0][1],
                'author_id': l[0][2],
                'genre': l[0][3],
                'year': l[0][4]
                   }
        resp.text = json.dumps(alb) 
        resp.status = falcon.HTTP_200 
    
    def on_patch(self, req, resp, name): #500 при несуществ. автор_айди
        form = req.media
        id_1 = list(s.query(Album.id_album).filter(Album.title == name)) #одинаковые назв - редактирует первый
           # album_one = Album(title=form["title"], author_id=form["author_id"], genre=form["genre"], year=form["year"])
        i = s.query(Album).get(id_1[0][0]) # если альбома нет, выводится не та структура данных, которая ожидается (не забыть!!! 404)
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
        
    def on_delete(self, req, resp, name):#
        #i = s.query(Album).filter(Album.title == name).one() #если одинаковые назв. альбомов - 500
        i = s.query(Album).filter(Album.id_album == name).one() #по айди
        s.delete(i)
        s.commit()
        resp.status = falcon.HTTP_204
    

       # l = list(s.query(Album.id_album, Album.title, Album.author_id, Album.genre, Album.year).filter(Album.title == name)) #из on_get (сократить(get))
        #alb = {'id_album': l[0][0], #уменьшить, унив., одинаковые назв.
         #       'title': l[0][1],
         #       'author_id': l[0][2],
         #       'genre': l[0][3],
         #       'year': l[0][4]
          #         }
        #resp.text = json.dumps(alb)
        #resp.status = falcon.HTTP_200