from pkg_resources import resource_filename
from pyramid.config import Configurator
from repoze.zodbconn.finder import PersistentApplicationFinder
from deform import Form
from fedexvoting.models import appmaker


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # add custom deform template search path
    deform_templates = resource_filename('deform', 'templates')
    fedexvoting_templates = resource_filename('fedexvoting', 'templates')
    search_path = (fedexvoting_templates, deform_templates)
    Form.set_zpt_renderer(search_path)
    zodb_uri = settings['zodb_uri']
    finder = PersistentApplicationFinder(zodb_uri, appmaker)
    def get_root(request):
        return finder(request.environ)
    # pyramid configuration
    config = Configurator(root_factory=get_root, settings=settings)
    # subscriber for base template setup
    config.add_subscriber(
        'fedexvoting.subscribers.add_base_template',
        'pyramid.events.BeforeRender')
    # add static views for this app and deform
    config.add_static_view('static', 'fedexvoting:static', cache_max_age=3600)
    config.add_static_view(
        'deform_static', 'deform:static', cache_max_age=3600)
    # find views
    config.scan('fedexvoting')
    return config.make_wsgi_app()