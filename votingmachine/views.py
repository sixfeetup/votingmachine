from datetime import datetime
from types import StringTypes
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.security import remember
from pyramid.security import forget
from pyramid.view import view_config
from pyramid.traversal import find_interface
import colander
from peppercorn import parse
from deform import ValidationFailure
from deform import Form
from deform import widget
from repoze.who.plugins.zodb.users import get_sha_password

from votingmachine.models import ITeamFolder
from votingmachine.models import IVotingBoothFolder

from votingmachine.models import PollingPlace
from votingmachine.models import VotingBoothFolder
from votingmachine.models import VotingBooth
from votingmachine.models import Team
from votingmachine.models import TeamFolder
from votingmachine.models import Profile

from votingmachine.schema import VotingBoothSchema
from votingmachine.schema import TeamSchema
from votingmachine.schema import BallotSchema
from votingmachine.schema import ProfileAddSchema


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
    return (css_tags, js_tags)


def _folder_contents(context, request, interface, sort='title',
                     sort_order='ascending', max_items=None):
    folder = find_interface(context, interface)
    items = []
    keys = list(folder.keys())

    def sort_by(x, y):
        attr1 = getattr(folder[x], sort)
        attr2 = getattr(folder[y], sort)
        if isinstance(attr1, StringTypes) and isinstance(attr2, StringTypes):
            attr1 = attr1.lower()
            attr2 = attr2.lower()
        return cmp(attr1, attr2)

    keys.sort(sort_by)
    if sort_order == 'descending':
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


def _team_vocab(context, request, select=False):
    root = request.root
    # TODO: use a catalog and index these?
    profiles = root['profiles']
    profile_values = list(profiles.values())
    profile_values.sort(key=lambda x: x.last_name)
    vocab = []
    names = set()
    for profile in profile_values:
        fullname = "%s %s" % (profile.first_name, profile.last_name)
        if fullname in names:
            names.add(fullname)
            fullname = '%s (%s)' % (fullname, profile.username)
        else:
            names.add(fullname)
        vocab.append((profile.username, fullname))
    if select:
        vocab.insert(0, ('', 'Select a value'))
    return vocab


@view_config(
    context=PollingPlace, name='login',
    renderer='templates/login.pt', permission='view')
@view_config(
    context='pyramid.httpexceptions.HTTPForbidden',
    renderer='templates/login.pt')
def login(request):
    logged_in = authenticated_userid(request)
    login_url = request.resource_url(request.context, 'login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/'  # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        user_folder = request.context['users']
        user = user_folder.get(login)
        if user is not None and user['password'] == get_sha_password(password):
            headers = remember(request, login)
            return HTTPFound(location=came_from, headers=headers)
        message = (
            'The username or password that you entered was not correct, try '
            'again'
        )

    return dict(
        message=message,
        url=request.application_url + '/login',
        came_from=came_from,
        login=login,
        password=password,
        logged_in=logged_in,
    )


@view_config(context=PollingPlace, name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(
        location=request.resource_url(request.context),
        headers=headers,
    )


@view_config(context=PollingPlace,
    renderer='votingmachine:templates/polling_place.pt', permission='view')
def polling_view(context, request):
    logged_in = authenticated_userid(request)
    current_votes = _folder_contents(
        context['votes'],
        request,
        IVotingBoothFolder,
        sort='start',
        sort_order='descending',
        max_items=1,
    )
    if current_votes:
        current_vote = current_votes[0]
    else:
        current_vote = None
    return {
        'current_vote': current_vote,
        'logged_in': logged_in,
    }


@view_config(context=VotingBoothFolder,
    renderer='votingmachine:templates/voting_booth_folder.pt',
    permission='view')
def voting_booth_folder(context, request):
    logged_in = authenticated_userid(request)
    booths = _folder_contents(
        context,
        request,
        IVotingBoothFolder,
        sort='start',
        sort_order='descending',
    )
    return {
        'booths': booths,
        'logged_in': logged_in,
    }


@view_config(context=VotingBooth,
    renderer='votingmachine:templates/voting_booth.pt', permission='view')
def voting_booth_view(context, request):
    logged_in = authenticated_userid(request)
    teams = _folder_contents(
        context['teams'],
        request,
        ITeamFolder,
    )
    return {
        'teams': teams,
        'logged_in': logged_in,
    }


@view_config(name='add', context=VotingBoothFolder,
    renderer='votingmachine:templates/voting_booth_edit.pt', permission='edit')
def add_voting_booth(context, request):
    logged_in = authenticated_userid(request)
    schema = VotingBoothSchema()
    form = Form(schema, buttons=('submit',))
    css_resources, js_resources = _form_resources(form)
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            form.validate(controls)
        except (ValidationFailure,), e:
            return {
                'form': e.render(),
                'css_resources': css_resources,
                'js_resources': js_resources,
            }
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
    return {
        'form': form.render(appstruct),
        'css_resources': css_resources,
        'js_resources': js_resources,
        'logged_in': logged_in,
    }


@view_config(name='edit', context=VotingBooth,
    renderer='votingmachine:templates/voting_booth_edit.pt', permission='edit')
def edit_voting_booth(context, request):
    logged_in = authenticated_userid(request)
    schema = VotingBoothSchema()
    form = Form(schema, buttons=('submit',))
    css_resources, js_resources = _form_resources(form)
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            form.validate(controls)
        except (ValidationFailure,), e:
            return {
                'form': e.render(),
                'css_resources': css_resources,
                'js_resources': js_resources,
                'logged_in': logged_in,
            }
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
    return {
        'form': form.render(appstruct),
        'css_resources': css_resources,
        'js_resources': js_resources,
        'logged_in': logged_in,
    }


@view_config(context=TeamFolder)
def teams_view(context, request):
    return HTTPFound(location=request.resource_url(context.__parent__))


@view_config(context=Team)
def team_view(context, request):
    return HTTPFound(location=request.resource_url(context.__parent__))


@view_config(name='add', context=TeamFolder,
             renderer='votingmachine:templates/team_edit.pt',
             permission='add:team')
def add_team(context, request):
    logged_in = authenticated_userid(request)
    schema = TeamSchema()
    # XXX: this could end badly...
    schema.children[2].widget.values = _team_vocab(context, request)
    schema.children[3].widget.values = _team_vocab(context, request, True)
    form = Form(schema, buttons=('submit',))
    css_resources, js_resources = _form_resources(form)
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            form.validate(controls)
        except (ValidationFailure,), e:
            return {
                'form': e.render(),
                'css_resources': css_resources,
                'js_resources': js_resources,
                'logged_in': logged_in,
            }
        params = parse(controls)
        team = Team(
            title=params['title'],
            description=params['description'],
            members=params['members'],
            leader=params['leader'],
            )
        team.__parent__ = context
        context.add_team(team)
        return HTTPFound(location=request.resource_url(context.__parent__))
    return {
        'form': form.render(),
        'css_resources': css_resources,
        'js_resources': js_resources,
        'logged_in': logged_in,
    }


@view_config(name='edit', context=Team,
    renderer='votingmachine:templates/team_edit.pt', permission='edit')
def edit_team(context, request):
    logged_in = authenticated_userid(request)
    schema = TeamSchema()
    # XXX: this could end badly...
    schema.children[2].widget.values = _team_vocab(context, request)
    schema.children[3].widget.values = _team_vocab(context, request, True)
    form = Form(schema, buttons=('submit',))
    css_resources, js_resources = _form_resources(form)
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            form.validate(controls)
        except (ValidationFailure,), e:
            return {
                'form': e.render(),
                'css_resources': css_resources,
                'js_resources': js_resources,
                'logged_in': logged_in,
            }
        params = parse(controls)
        context.title = params['title']
        context.description = params['description']
        context.members = params['members']
        context.leader = params['leader']
        # TODO: use find by interface here
        voting_booth = context.__parent__.__parent__
        return HTTPFound(location=request.resource_url(voting_booth))
    appstruct = dict(
        title=context.title,
        description=context.description,
        members=context.members,
        leader=context.leader,
    )
    return {
        'form': form.render(appstruct),
        'css_resources': css_resources,
        'js_resources': js_resources,
        'logged_in': logged_in,
    }


@view_config(name='register', context=PollingPlace,
    renderer='votingmachine:templates/registration_form.pt')
def add_profile(context, request):
    logged_in = authenticated_userid(request)
    schema = ProfileAddSchema()
    form = Form(schema, buttons=('submit',))
    css_resources, js_resources = _form_resources(form)
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            form.validate(controls)
        except (ValidationFailure,), e:
            return {
                'form': e.render(),
                'css_resources': css_resources,
                'js_resources': js_resources,
                'logged_in': logged_in,
            }
        params = parse(controls)
        first_name = params['first_name']
        last_name = params['last_name']
        username = params['username']
        email = params['email']
        password = params['password']['value']
        # Create the profile
        profile = Profile(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            )
        # Add the profile object
        profile.__parent__ = context['profiles']
        profile.__name__ = username
        context['profiles'].add_profile(profile)
        # Add the user object
        user_folder = context['users']
        user_folder.add(username, username, password)
        return HTTPFound(location=request.resource_url(context.__parent__))
    return {
        'form': form.render(),
        'css_resources': css_resources,
        'js_resources': js_resources,
        'logged_in': logged_in,
    }


@view_config(name='vote', context=VotingBooth,
    renderer='votingmachine:templates/vote.pt', permission='vote')
def vote_view(context, request):
    logged_in = authenticated_userid(request)
    schema = BallotSchema()
    _add_category_schema(context, request, schema)
    form = Form(schema, buttons=('submit',))
    css_resources, js_resources = _form_resources(form)
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
            return {
                'form': e.render(),
                'css_resources': css_resources,
                'js_resources': js_resources,
                'logged_in': logged_in,
            }
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
    return {
        'form': form.render(appstruct),
        'css_resources': css_resources,
        'js_resources': js_resources,
        'logged_in': logged_in,
    }


@view_config(name='results', context=VotingBooth,
    renderer='votingmachine:templates/results.pt', permission='view')
def results_view(context, request):
    """This is pretty ugly, needs a re-factoring
    """
    logged_in = authenticated_userid(request)
    scores = {}
    # build up the list of weights
    weights = {}
    for category in context.categories:
        weights[category['vote_category']] = float(category['weight'])
    for vote in context.results:
        for team in vote:
            team_id = int(team['team_hidden'])
            team_obj = context['teams'].get(team_id, None)
            if team_obj is None:
                continue
            # WTF is up with the empty key for the rankings?
            vote_levels = team['rankings']['']
            for ranking in vote_levels:
                total = scores.setdefault(team_obj, 0)
                # default to 1.0 if the weight has gone missing
                weight = weights.get(ranking, 1.0)
                new_score = int(vote_levels[ranking]) * weight
                scores[team_obj] = total + new_score
    return {
        'scores': sorted(scores.items(), cmp=lambda x, y: cmp(y[1], x[1])),
        'logged_in': logged_in,
    }
