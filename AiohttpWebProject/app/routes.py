from . import views

def routes(app):
    app.router.add_route('GET', '/city', views.getCity)
    app.router.add_route('POST', '/city', views.postCity)
    app.router.add_route('DELETE', '/city', views.delCity)
    app.router.add_route('GET', '/cities', views.getCities)
    #app.router.add_route('GET', '/nearestCities', views.nearestCities)