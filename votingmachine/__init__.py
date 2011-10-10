from pkg_resources import resource_filename
from pyramid.config import Configurator
from repoze.zodbconn.finder import PersistentApplicationFinder
from deform import Form
from votingmachine.models import appmaker


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # add custom deform template search path
    deform_templates = resource_filename('deform', 'templates')
    votingmachine_templates = resource_filename('votingmachine', 'templates')
    search_path = (votingmachine_templates, deform_templates)
    Form.set_zpt_renderer(search_path)
    zodb_uri = settings['zodb_uri']
    finder = PersistentApplicationFinder(zodb_uri, appmaker)
    def get_root(request):
        return finder(request.environ)
    # pyramid configuration
    config = Configurator(root_factory=get_root, settings=settings)
    # subscriber for base template setup
    config.add_subscriber(
        'votingmachine.subscribers.add_base_template',
        'pyramid.events.BeforeRender')
    # add static views for this app and deform
    config.add_static_view(
        'static', 'votingmachine:static', cache_max_age=3600)
    config.add_static_view(
        'deform_static', 'deform:static', cache_max_age=3600)
    # find views
    config.scan('votingmachine')
    return config.make_wsgi_app()
