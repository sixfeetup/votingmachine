from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.traversal import find_interface
from deform import ValidationFailure
from deform import Form

from fedexvoting.models import ITeamFolder
from fedexvoting.models import IVotingBoothFolder

from fedexvoting.models import PollingPlace
from fedexvoting.models import VotingBoothFolder
from fedexvoting.models import VotingBooth
from fedexvoting.models import Team
from fedexvoting.models import TeamFolder

from fedexvoting.schema import VotingBoothSchema
from fedexvoting.schema import TeamSchema


def _form_resources(form):
    resources = form.get_widget_resources()
    js_resources = resources['js']
    css_resources = resources['css']
    js_links = ['/deform_static/%s' % r for r in js_resources]
    css_links = ['/deform_static/%s' % r for r in css_resources]
    jtag = '<script type="text/javascript" src="%s"></script>'
    ltag = '<link rel="stylesheet" media="screen" type="text/css" href="%s"/>'
    js_tags = [jtag % link for link in js_links]
    css_tags = [ltag % link for link in css_links]
    return css_tags + js_tags


def _folder_contents(context, request, interface, sort='title', max_items=10):
    folder = find_interface(context, interface)
    items = []
    keys = list(folder.keys())
    def sort_by(x, y):
        return cmp(getattr(folder[x], sort), getattr(folder[y], sort))
    keys.sort(sort_by)
    keys.reverse()
    keys = keys[:max_items]
    for name in keys:
        item = folder[name]
        item_url = request.resource_url(item)
        new = dict(
            name=name,
            item=item,
            url=item_url,
        )
        items.append(new)
    return items


@view_config(context=PollingPlace,
    renderer='fedexvoting:templates/polling_place.pt')
def polling_view(context, request):
    current_votes = _folder_contents(
        context['votes'],
        request,
        IVotingBoothFolder,
        sort='start',
        max_items=1,
    )
    if current_votes:
        current_vote = current_votes[0]
    else:
        current_vote = None
    return {'current_vote': current_vote}


@view_config(context=VotingBoothFolder,
    renderer='fedexvoting:templates/voting_booth_folder.pt')
def voting_booth_folder(context, request):
    booths = _folder_contents(
        context,
        request,
        IVotingBoothFolder,
        sort='start',
    )
    return {'booths': booths}


@view_config(context=VotingBooth,
    renderer='fedexvoting:templates/voting_booth.pt')
def voting_booth_view(context, request):
    teams = _folder_contents(
        context['teams'],
        request,
        ITeamFolder,
    )
    return {'teams': teams}


def _process_categories(params):
    vote_categories = params.getall(u'vote_category')
    weights = params.getall(u'weight')
    # create a list of dicts which is what deform will expect
    categories = [
        dict(vote_category=i[0], weight=i[1])
        for i in zip(vote_categories, weights)]
    return categories


def _process_dates(params):
    date_fmt = u'%Y-%m-%d %H:%M:%S'
    start = datetime.strptime(params['start'], date_fmt)
    end = datetime.strptime(params['end'], date_fmt)
    return start, end


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
        categories = _process_categories(params)
        start, end = _process_dates(params)
        voting_booth = VotingBooth(
            title=params['title'],
            start=start,
            end=end,
            categories=categories,
            )
        voting_booth.__parent__ = context
        # maybe this should be done in the team add view?
        team_folder = TeamFolder()
        team_folder.__parent__ = voting_booth
        team_folder.__name__ = 'teams'
        voting_booth['teams'] = team_folder
        context.add_booth(voting_booth)
        return HTTPFound(location=request.resource_url(voting_booth))
    return {'form': form.render(), 'resource_tags': resource_tags}


@view_config(name='edit', context=VotingBooth,
    renderer='fedexvoting:templates/voting_booth_edit.pt')
def edit_voting_booth(context, request):
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
        categories = _process_categories(params)
        start, end = _process_dates(params)
        context.title = params['title']
        context.start = start
        context.end = end
        context.categories = categories
        return HTTPFound(location=request.resource_url(context))
    appstruct = dict(
        title=context.title,
        start=context.start,
        end=context.end,
        categories=context.categories,
    )
    return {'form': form.render(appstruct), 'resource_tags': resource_tags}


@view_config(context=TeamFolder)
def teams_view(context, request):
    return HTTPFound(location=request.resource_url(context.__parent__))


@view_config(context=Team)
def team_view(context, request):
    return HTTPFound(location=request.resource_url(context.__parent__))


@view_config(name='add', context=TeamFolder,
    renderer='fedexvoting:templates/team_edit.pt')
def add_team(context, request):
    schema = TeamSchema()
    form = Form(schema, buttons=('submit',))
    resource_tags = _form_resources(form)
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            form.validate(controls)
        except (ValidationFailure,), e:
            return {'form': e.render(), 'resource_tags': resource_tags}
        params = request.params
        team = Team(
            title=params['title'],
            description=params['description'],
            )
        team.__parent__ = context
        context.add_team(team)
        return HTTPFound(location=request.resource_url(context.__parent__))
    return {'form': form.render(), 'resource_tags': resource_tags}


@view_config(name='edit', context=Team,
    renderer='fedexvoting:templates/team_edit.pt')
def edit_team(context, request):
    schema = TeamSchema()
    form = Form(schema, buttons=('submit',))
    resource_tags = _form_resources(form)
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            form.validate(controls)
        except (ValidationFailure,), e:
            return {'form': e.render(), 'resource_tags': resource_tags}
        params = request.params
        context.title = params['title']
        context.description = params['description']
        # TODO: use find by interface here
        voting_booth = context.__parent__.__parent__
        return HTTPFound(location=request.resource_url(voting_booth))
    return {'form': form.render(), 'resource_tags': resource_tags}
