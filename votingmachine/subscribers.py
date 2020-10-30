from pyramid.renderers import get_renderer
from pyramid.security import authenticated_userid


def add_base_template(event):
    base = get_renderer('templates/base.pt').implementation()
    event.update({
        'base': base,
        'username': authenticated_userid(event['request'])})
