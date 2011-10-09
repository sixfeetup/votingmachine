from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.traversal import find_interface
import colander
from peppercorn import parse
from deform import ValidationFailure
from deform import Form
from deform import widget

from fedexvoting.models import ITeamFolder
from fedexvoting.models import IVotingBoothFolder

from fedexvoting.models import PollingPlace
from fedexvoting.models import VotingBoothFolder
from fedexvoting.models import VotingBooth
from fedexvoting.models import Team
from fedexvoting.models import TeamFolder

from fedexvoting.schema import VotingBoothSchema
from fedexvoting.schema import TeamSchema
from fedexvoting.schema import BallotSchema

CATEGORY_RANK = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
)


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


def _folder_contents(context, request, interface, sort='title',
                     max_items=None):
    folder = find_interface(context, interface)
    items = []
    keys = list(folder.keys())
    def sort_by(x, y):
        return cmp(getattr(folder[x], sort), getattr(folder[y], sort))
    keys.sort(sort_by)
    keys.reverse()
    if max_items is not None:
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


def _process_dates(values):
    date_fmt = u'%Y-%m-%d %H:%M:%S'
    start = datetime.strptime(values['start'], date_fmt)
    end = datetime.strptime(values['end'], date_fmt)
    return start, end


def _add_category_schema(context, request, schema):
    team_vote = schema['votes']['vote']
    if 'rankings' in team_vote:
        return
    categories = context.categories
    if not categories:
        return
    cat_vote_schema = colander.SchemaNode(colander.Mapping())
    for cat in categories:
        cat_name = cat['vote_category']
        cat_vote_schema.add(
            colander.SchemaNode(
                colander.Int(),
                name=cat_name,
                widget=widget.RadioChoiceWidget(values=CATEGORY_RANK),
                validator=colander.OneOf(dict(CATEGORY_RANK).keys()),
            )
        )
    team_vote.add(
        colander.SchemaNode(
            colander.Mapping(),
            cat_vote_schema,
            name='rankings'
        )
    )


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
        values = parse(request.params.items())
        start, end = _process_dates(values)
        voting_booth = VotingBooth(
            title=values['title'],
            start=start,
            end=end,
            categories=values['categories'],
            )
        voting_booth.__parent__ = context
        # maybe this should be done in the team add view?
        team_folder = TeamFolder()
        team_folder.__parent__ = voting_booth
        team_folder.__name__ = 'teams'
        voting_booth['teams'] = team_folder
        context.add_booth(voting_booth)
        return HTTPFound(location=request.resource_url(voting_booth))
    # set up default categories to use
    categories = [
        dict(vote_category='Completeness', weight='1.0'),
        dict(vote_category='Usefulness', weight='0.7'),
        dict(vote_category='Awesomeness', weight='0.5'),
    ]
    appstruct = dict(categories=categories)
    return {'form': form.render(appstruct), 'resource_tags': resource_tags}


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
        values = parse(request.params.items())
        start, end = _process_dates(values)
        context.title = values['title']
        context.start = start
        context.end = end
        context.categories = values['categories']
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


@view_config(name='vote', context=VotingBooth,
    renderer='fedexvoting:templates/vote.pt')
def vote_view(context, request):
    schema = BallotSchema()
    _add_category_schema(context, request, schema)
    form = Form(schema, buttons=('submit',))
    resource_tags = _form_resources(form)
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            form.validate(controls)
        except (ValidationFailure,), e:
            # Put the team names back in place
            cstruct = e.cstruct
            for vote in cstruct['votes']:
                team_id = vote['team_hidden']
                team_obj = context['teams'][team_id]
                team_title = team_obj.title
                team_title = team_obj.description
                vote['team_title'] = team_title
                vote['team_description'] = team_title
            return {'form': e.render(), 'resource_tags': resource_tags}
        results = parse(request.params.items())['votes']
        context.results.append(results)
        context._p_changed = True
        return HTTPFound(location=request.resource_url(context))
    # set up the list of teams
    teams = _folder_contents(
        context['teams'],
        request,
        ITeamFolder,
    )
    team_dicts = [
        dict(
            team_hidden=team['item'].__name__,
            team_title=team['item'].title,
            team_description=team['item'].description,
        )
        for team in teams
    ]
    appstruct = {'votes': team_dicts}
    return {'form': form.render(appstruct), 'resource_tags': resource_tags}


@view_config(name='results', context=VotingBooth,
    renderer='fedexvoting:templates/results.pt')
def results_view(context, request):
    """This is pretty ugly, needs a re-factoring
    """
    scores = {}
    # build up the list of weights
    weights = {}
    for category in context.categories:
        weights[category['vote_category']] = float(category['weight'])
    for vote in context.results:
        for team in vote:
            team_id = int(team['team_hidden'])
            team_obj = context['teams'][team_id]
            # WTF is up with the empty key for the rankings?
            vote_levels = team['rankings']['']
            for ranking in vote_levels:
                total = scores.setdefault(team_obj, 0)
                new_score = int(vote_levels[ranking]) * weights[ranking]
                scores[team_obj] = total + new_score
    return {'scores': sorted(scores.items(), cmp=lambda x, y: cmp(y[1], x[1]))}
