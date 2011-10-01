from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from deform import ValidationFailure
from deform import Form
from fedexvoting.models import PollingPlace
from fedexvoting.models import VotingBoothFolder
from fedexvoting.models import VotingBooth
from fedexvoting.schema import VotingBoothSchema


def _form_resources(form):
    resources = form.get_widget_resources()
    js_resources = resources['js']
    css_resources = resources['css']
    js_links = ['/deform_static/%s' % r for r in js_resources]
    css_links = ['/deform_static/%s' % r for r in css_resources]
    js_tags = [
        '<script type="text/javascript" src="%s"></script>' % link
        for link in js_links]
    css_tags = [
        '<link rel="stylesheet" media="screen" type="text/css" href="%s"/>' % link
        for link in css_links]
    return css_tags + js_tags


@view_config(context=PollingPlace,
    renderer='fedexvoting:templates/polling_place.pt')
def polling_view(request):
    return {}


@view_config(context=VotingBoothFolder,
    renderer='fedexvoting:templates/voting_booth_folder.pt')
def voting_booth_folder(request):
    return {}


@view_config(context=VotingBooth,
    renderer='fedexvoting:templates/voting_booth.pt')
def voting_booth_view(request):
    return {}


@view_config(name='add', context=VotingBoothFolder,
    renderer='fedexvoting:templates/voting_booth_edit.pt')
def add_voting_booth(context, request):
    schema = VotingBoothSchema()
    form = Form(schema, buttons=('submit',))
    resource_tags = _form_resources(form)
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            form.validate(controls)
        except (ValidationFailure,), e:
            return {'form': e.render(), 'resource_tags': resource_tags}
        voting_booth = VotingBooth(
            title=request.POST['title'],
            start=request.POST['start'],
            end=request.POST['end'],
            )
        voting_booth.__parent__ = context
        context.add_booth(voting_booth)
        return HTTPFound(location=request.resource_url(voting_booth))
    return {'form': form.render(), 'resource_tags': resource_tags}
