import json
import falcon
from sqlalchemy import desc, text
from sqlalchemy.exc import NoResultFound
from ..db.db_create import Album, Author, Song, session
from .func.todict import to_dict

s = session()

class SongsH:

    def on_get(self, req, resp):
       
        StrFilt = []
        if 'album' in req.params:
            StrFilt.append(Song.album_id == Album.id_album)
            StrFilt.append(Album.title.ilike(req.params['album'][-1] + '%'))
        if 'author' in req.params:
            if 'album' not in req.params:
                StrFilt.append(Song.album_id == Album.id_album)
            StrFilt.append(Album.author_id == Author.id_author)  
            StrFilt.append(Author.Name.ilike(req.params['author'][-1] + '%'))
        if 'tag' in req.params:
            StrFilt.append(Song.tag.ilike('%' + req.params['tag'][-1] + '%'))
        if 'song' in req.params:
            StrFilt.append(Song.title.ilike(req.params['song'][-1] + '%'))
        #DictAlbAuthor = {i.id_song: i.title for i in s.query(Song).filter(Song.album_id == Album.id_album).filter(Album.title.ilike(ValueTitle + '%'))}    Фильтрация по альбому
        #DictAlbAuthor = {i.id_song: i.title for i in s.query(Song).filter(Song.title.ilike(ValueTitle + '%'))}     Фильтрация по названию
        #DictAlbAuthor = {i.id_song: i.title for i in s.query(Song).filter(Song.album_id == Album.id_album).filter(Album.author_id == Author.id_author).filter(Author.Name.ilike(ValueTitle + '%'))}    Фильтрация по имени автора
        #DictAlbAuthor = {i.id_song: i.title for i in s.query(Song).filter(Song.tag.ilike('%' + ValueTitle + '%'))}     Фильтрация по тегу
        DictAlbAuthor = {i.id_song: i.title for i in s.query(Song).filter(*StrFilt)}
        SDictAlbAut = dict(sorted(DictAlbAuthor.items(), key=lambda x: x[0]))
        resp.text = json.dumps({'songs': SDictAlbAut})

    def on_post(self, req, resp):
        
        form = json.loads(req.stream.read()) #не по json подумать
        NameColumns = to_dict(Song)
        del NameColumns['id_song']
        if form.keys() == NameColumns.keys():
            s.add(Song(**form)) 
            s.commit()
            resp.status = falcon.HTTP_201
            resp.text = json.dumps({'id_song': s.query(Song.id_song).filter().order_by(desc(Song.id_song)).limit(1)[0][0]})#*
        else:
            raise falcon.HTTPBadRequest
        
class SongH:

    def on_get(self, req, resp, name): 
        if name.isdigit():
            try:
                alb = s.query(Song).get(name)
                resp.text = json.dumps(to_dict(alb)) 
            except AttributeError:
                raise falcon.HTTPNotFound
        else:
            raise falcon.HTTPNotFound('Please, enter your ID in numeric format')
        
    def on_post(self, req, resp, name): #теги
        if name.isdigit():
            form = json.loads(req.stream.read())
            if 'tag' in form:
                StrTags = form['tag'].strip()
                if ',' in form['tag']:
                    StrTags = StrTags.replace(',', ' ')
                if '.' in form['tag']:
                    StrTags = StrTags.replace('.', ' ')
                TagsList = StrTags.split()
                InfoSong = s.query(Song).get(name)
                if InfoSong.tag is not None:
                    TabTag = s.query(Song).get(name).tag
                    TabTagList = TabTag.split()
                    print(TabTag)
                    TabTagList.extend(TagsList)
                else:
                    TabTagList = TagsList
                InfoSong.tag = ' '.join(TabTagList)
                s.add(InfoSong)
                s.commit()  
                resp.status = falcon.HTTP_201
                resp.text = json.dumps({'title': 'Tags added successfully'})
            else:
                raise falcon.HTTPBadRequest
        else:
            raise falcon.HTTPNotFound("Please, enter song's ID in numeric format") 
         
    def on_patch(self, req, resp, name):
        if name.isdigit():
            try:
                form = json.loads(req.stream.read())
                alb = s.query(Song).get(name)
                AlbDict = to_dict(alb) 
                del AlbDict['id_song']
                if set(form.keys()).issubset(set(AlbDict.keys())):
                    if 'album_id' in list(form.keys()) and form['album_id'] not in [str(id_alb[0]) for id_alb in s.query(Album.id_album)]:
                        raise falcon.HTTPNotFound('Please, enter an existing author ID')
                    for key in form.keys():
                        setattr(alb, key, form[key])
                    s.add(alb)
                    s.commit()
                else:
                    raise falcon.HTTPBadRequest
                alb_1 = s.query(Song).get(name)
                resp.text = json.dumps(to_dict(alb_1))
            except AttributeError:
                raise falcon.HTTPNotFound
        else:
            raise falcon.HTTPNotFound('Please, enter album ID in numeric format') 
        
    def on_delete(self, req, resp, name):
        if name.isdigit():
            try:
                i = s.query(Song).filter(Song.id_song == name).one() #по айди
                s.delete(i)
                s.commit()
                resp.status = falcon.HTTP_204
            except NoResultFound:
                raise falcon.HTTPNotFound
        else:
            raise falcon.HTTPNotFound('Please, enter your ID in numeric format')