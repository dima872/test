import json
import falcon
from sqlalchemy import desc
from db.db_create import Album, Author, Song, session
import mimetypes
from .func.functions1 import to_dict, valid_id_not_in_db, json_body, json_body_and_name

s = session()


class SongsH:
    def __init__(self, handl):
        self.handl = handl

    def on_get(self, req, resp):
        list_songs = self.handl.songs_get(req.params)
        resp.text = json.dumps({"songs": list_songs})

    @json_body
    def on_post(self, req, resp):
        self.handl.songs_post(req.stream)
        resp.status = falcon.HTTP_201
        resp.text = json.dumps(
            {
                "id_song": s.query(Song.id_song)
                .filter()
                .order_by(desc(Song.id_song))
                .limit(1)[0][0]
            }
        )


class SongH:
    def __init__(self, handl):
        self.handl = handl

    @valid_id_not_in_db
    def on_get(self, req, resp, name):
        one_song = self.handl.get_song(name)
        resp.text = json.dumps(one_song)

    @valid_id_not_in_db
    @json_body_and_name
    def on_post(self, req, resp, name):  # теги
        self.handl.post_song(req.stream, name)
        resp.status = falcon.HTTP_201
        resp.text = json.dumps({"title": "Tags added successfully"})

    @valid_id_not_in_db
    @json_body_and_name
    def on_patch(self, req, resp, name):
        song_get = self.handl.patch_song(req.stream, name)
        resp.text = json.dumps(song_get)

    @valid_id_not_in_db
    @json_body_and_name
    def on_delete(self, req, resp, name):
        self.handl.del_song(name)
        resp.status = falcon.HTTP_204


class LoadGet:
    def __init__(self, handl):
        self.handl = handl

    def valid_content_type(req, resp, resource, params):
        if "multipart/form-data" not in req.content_type:
            raise falcon.HTTPBadRequest("Use 'multipart/form-data' content")

    @valid_id_not_in_db
    def on_get(self, req, resp, name):
        # decplaysong = base64.b64decode(playsong)
        playsong = s.query(Song).get(name).file
        resp.content_type = "audio/mpeg"
        resp.data = playsong
        resp.status = falcon.HTTP_200  # 206

    @valid_id_not_in_db
    @json_body_and_name
    @falcon.before(valid_content_type)
    def on_put(self, req, resp, name):  # подумать на типом метода (put/patch)
        self.handl.put_load_song(name, req.get_media())
        resp.status = falcon.HTTP_201


class HandlerSongs:
    def songs_get(self, params):
        song_list = self.songs_get_filter(params)
        dictsong = {i.id_song: i.title for i in s.query(Song).filter(*song_list)}
        sdictsong = dict(sorted(dictsong.items(), key=lambda x: x[0]))
        return sdictsong

    def songs_get_filter(self, params):
        strfilt = []
        if "album" in params:
            strfilt.append(Song.album_id == Album.id_album)
            lalbum = params["album"]
            if type(lalbum) != list:
                lalbum = lalbum.split()
            for alb in lalbum:
                strfilt.append(Album.title.ilike(alb.rstrip() + "%"))

        if "author" in params:
            if "album" not in params:
                strfilt.append(Song.album_id == Album.id_album)
            strfilt.append(Album.author_id == Author.id_author)
            lauthor = params["author"]
            if type(lauthor) != list:
                lauthor = lauthor.split()
            for aut in lauthor:
                strfilt.append(Author.Name.ilike(aut.rstrip() + "%"))

        if "tag" in params:
            ltag = params["tag"]
            if type(ltag) != list:
                ltag = ltag.split()
            for t in ltag:
                strfilt.append(Song.tag.ilike("%" + t.rstrip() + "%"))

        if "song" in params:
            lsong = params["song"]
            if type(lsong) != list:
                lsong = lsong.split()
            for sg in lsong:
                strfilt.append(Song.title.ilike(sg.rstrip() + "%"))
        return strfilt

    def songs_post(self, body_j):
        form = json.loads(body_j.read())
        form_valid = self.post_form(form)
        s.add(Song(**form_valid))
        s.commit()

    def post_form(self, form):
        namecolumns = to_dict(Song)
        del namecolumns["id_song"]
        del namecolumns["file"]
        if type(form) == dict and form.keys() == namecolumns.keys():
            self.existing_album(form)
            return form
        else:
            raise falcon.HTTPBadRequest

    def get_song(self, name):
        songquery = s.query(Song).get(name)
        dictsq = to_dict(songquery)
        if songquery.file is not None:
            dictsq["file"] = "Available"
            return dictsq
        dictsq["file"] = "Not available"
        return dictsq

    def post_song(self, body_j, name):
        form = json.loads(body_j.read())
        if type(form) == dict:
            tagslist = self.valid_tags(form)
            tags = self.add_tags(tagslist, name)
            s.add(tags)
            s.commit()
        else:
            raise falcon.HTTPBadRequest

    def valid_tags(self, form):
        if "tag" in form:
            StrTags = form["tag"].strip()
            if "," in form["tag"]:
                StrTags = StrTags.replace(",", " ")
            if "." in form["tag"]:
                StrTags = StrTags.replace(".", " ")
            return StrTags.split()
        else:
            raise falcon.HTTPBadRequest

    def add_tags(self, tagslist, name):
        infosong = s.query(Song).get(name)
        if infosong.tag is not None:
            tabtag = infosong.tag
            tabtaglist = tabtag.split()
            tabtaglist.extend(tagslist)
        else:
            tabtaglist = tagslist
        tabtaglist = list(set(tabtaglist))
        print(tabtaglist)
        infosong.tag = " ".join(tabtaglist)
        return infosong

    def patch_song(self, body_j, name):
        form = json.loads(body_j.read())
        get_query_song = s.query(Song).get(name)
        modified_res = self.modif_song(get_query_song, form)
        s.add(modified_res)
        s.commit()
        sg1 = self.get_song(name)
        return sg1

    def modif_song(self, sg, form):
        sgdict = to_dict(sg)
        del sgdict["id_song"]
        del sgdict["file"]
        if type(form) == dict and set(form.keys()).issubset(set(sgdict.keys())):
            self.existing_album(form)
            for key in form.keys():
                setattr(sg, key, form[key])
            return sg
        else:
            raise falcon.HTTPBadRequest

    def existing_album(self, form):
        if "album_id" in list(form) and form["album_id"] not in [
            str(id_alb[0]) for id_alb in s.query(Album.id_album)
        ]:
            raise falcon.HTTPNotFound("Please, enter an existing author ID")

    def del_song(self, name):
        i = s.query(Song).filter(Song.id_song == name).one()  # по айди
        s.delete(i)
        s.commit()

    def put_load_song(self, name, get_media):
        load_sound = self.put_load_song_valid(name, get_media)
        s.add(load_sound)
        s.commit()

    def put_load_song_valid(self, name, get_media):
        for i in get_media:
            content_of_file = i.stream.read()
            name_of_file = i.filename
        if mimetypes.guess_type(name_of_file)[0] != "audio/mpeg":
            raise falcon.HTTPBadRequest("You can only use .mp3 format")
        audiofile = s.query(Song).get(name)
        audiofile.file = content_of_file
        return audiofile
