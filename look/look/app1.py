import falcon
from .methods import AlbumsH, AlbumH

app = application = falcon.App()
    #Методы falcon.App.add_route()и falcon.asgi.App.add_route()используются для связи шаблона URI с ресурсом. Затем Falcon сопоставляет входящие запросы с ресурсами на основе этих шаблонов.
app.add_route('/albums', AlbumsH())
app.add_route('/albums/{name}', AlbumH())