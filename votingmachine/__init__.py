from pkg_resources import resource_filename
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from repoze.zodbconn.finder import PersistentApplicationFinder
from deform import Form
from votingmachine.models import appmaker
from votingmachine.security import groupfinder


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

    authn_policy = AuthTktAuthenticationPolicy(
        secret='seekrit',
        callback=groupfinder,
    )
    authz_policy = ACLAuthorizationPolicy()
    # pyramid configuration
    config = Configurator(
        root_factory=get_root,
        settings=settings,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
    )
    config.load_zcml('configure.zcml')
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
