import falcon
from .resources.albums import AlbumsH, AlbumH
from .resources.authors import AuthorsH, AuthorH
#from .resources.songs import SongsH, SongH
from .jwtoken import auth_middleware, login
app = application = falcon.App(middleware=[auth_middleware])
    #Методы falcon.App.add_route()и falcon.asgi.App.add_route()используются для связи шаблона URI с ресурсом. Затем Falcon сопоставляет входящие запросы с ресурсами на основе этих шаблонов.
app.add_route('/res/albums', AlbumsH())
app.add_route('/res/albums/{name}', AlbumH())
app.add_route('/res/authors', AuthorsH())
app.add_route('/res/authors/{name}', AuthorH())
#app.add_route('/res/songs', SongsH())
#app.add_route('/res/songs/{name}', SongH())
app.add_route('/login', login)
#falcon.strip_url_path_trailing_slash = True