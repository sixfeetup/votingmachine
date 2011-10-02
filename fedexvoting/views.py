from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.traversal import find_interface
from deform import ValidationFailure
from deform import Form
from fedexvoting.models import PollingPlace
from fedexvoting.models import IVotingBoothFolder
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


def _get_booths(context, request, max_items=10):
    booth_folder = find_interface(context, IVotingBoothFolder)
    booths = []
    keys = list(booth_folder.keys())
    def byint(a, b):
        try:
            return cmp(int(a), int(b))
        except TypeError:
            return cmp(a, b)
    keys.sort(byint)
    keys.reverse()
    keys = keys[:max_items]
    for name in keys:
        entry = booth_folder[name]
        booth_url = request.resource_url(entry)
        new = dict(
            name=name,
            title=entry.title,
            start=entry.start,
            end=entry.end,
            url=booth_url,
        )
        booths.append(new)
    return booths


@view_config(context=PollingPlace,
    renderer='fedexvoting:templates/polling_place.pt')
def polling_view(context, request):
    current_votes = _get_booths(context['votes'], request, 1)
    if current_votes:
        current_vote = current_votes[0]
    else:
        current_vote = None
    return {'current_vote': current_vote}


@view_config(context=VotingBoothFolder,
    renderer='fedexvoting:templates/voting_booth_folder.pt')
def voting_booth_folder(context, request):
    booths = _get_booths(context, request)
    return {'booths': booths}


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
        params = request.params
        vote_categories = params.getall(u'vote_category')
        weights = params.getall(u'weight')
        categories = dict(zip(vote_categories, weights))
        voting_booth = VotingBooth(
            title=params['title'],
            start=params['start'],
            end=params['end'],
            categories=categories,
            )
        voting_booth.__parent__ = context
        context.add_booth(voting_booth)
        return HTTPFound(location=request.resource_url(voting_booth))
    return {'form': form.render(), 'resource_tags': resource_tags}
