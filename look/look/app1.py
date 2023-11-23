import falcon
from resources.albums import AlbumsH, AlbumH, HandlerAlbums
from resources.authors import AuthorsH, AuthorH, HandlerAuthors
from resources.songs import SongsH, SongH, LoadGet, HandlerSongs
from jwtoken import AuthMiddleware, LoginH

# falcon.strip_url_path_trailing_slash = True
app = application = falcon.App(middleware=[AuthMiddleware()])
# Метод falcon.App.add_route() используtтся для связи шаблона URI с ресурсом. Затем Falcon сопоставляет входящие запросы с ресурсами на основе этих шаблонов.
handleralb = HandlerAlbums()
handleraut = HandlerAuthors()
handlersgs = HandlerSongs()


app.add_route("/res/albums", AlbumsH(handleralb))
app.add_route("/res/albums/{name}", AlbumH(handleralb))
app.add_route("/res/authors", AuthorsH(handleraut))
app.add_route("/res/authors/{name}", AuthorH(handleraut))
app.add_route("/res/songs", SongsH(handlersgs))
app.add_route("/res/songs/{name}", SongH(handlersgs))
app.add_route("/login", LoginH())
app.add_route("/res/songs/{name}/load", LoadGet(handlersgs))
