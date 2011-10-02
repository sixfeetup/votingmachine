from pyramid.config import Configurator
from pyramid_zodbconn import get_connection
from fedexvoting.models import appmaker

def root_factory(request):
    conn = get_connection(request)
    return appmaker(conn.root())

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=root_factory, settings=settings)
    config.add_subscriber(
        'fedexvoting.subscribers.add_base_template',
        'pyramid.events.BeforeRender')
    config.add_static_view('static', 'fedexvoting:static', cache_max_age=3600)
    config.add_static_view(
        'deform_static', 'deform:static', cache_max_age=3600)
    config.scan('fedexvoting')
    return config.make_wsgi_app()
