from persistent import Persistent
from persistent.mapping import PersistentMapping
from zope.interface import Interface
from zope.interface import implements
from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import Authenticated
from pyramid.security import has_permission
from pyramid.threadlocal import get_current_request
from pyramid.traversal import find_root
from repoze.folder import Folder
from repoze.who.plugins.zodb.users import Users


class PollingPlace(PersistentMapping):
    __parent__ = __name__ = None
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'add:team'),
        (Allow, Authenticated, 'vote'),
        (Allow, 'group:administrators', 'add:booth'),
        (Allow, 'group:administrators', 'edit'),
    ]


class IVotingBoothFolder(Interface):
    """Marker interface for voting booth folder"""


class VotingBoothFolder(Folder):
    implements(IVotingBoothFolder)

    current_id = -1

    def add_booth(self, booth):
        newid = self.current_id + 1
        self.current_id = newid
        booth_id = str(newid)
        self[booth_id] = booth
        return booth_id

    def can_add_booth(self):
        """This seems totally wrong...
        """
        request = get_current_request()
        permission = has_permission('add:booth', self, request)
        return permission.boolval


class IVotingBooth(Interface):
    """Marker interface for voting booth"""


class VotingBooth(Folder):
    implements(IVotingBooth)

    winner = None

    def __init__(self, title, start, end, categories):
        """The container for a vote"""
        # initialize the folder settings
        super(VotingBooth, self).__init__()
        self.title = title
        self.start = start
        self.end = end
        self.categories = categories
        self.results = {}

    def can_edit_booth(self):
        """This seems totally wrong...
        """
        request = get_current_request()
        permission = has_permission('add:booth', self, request)
        return permission.boolval

    def can_add_team(self):
        """This seems totally wrong...
        """
        request = get_current_request()
        permission = has_permission('add:team', self, request)
        return permission.boolval

    def can_vote(self):
        """This seems totally wrong...
        """
        request = get_current_request()
        permission = has_permission('vote', self, request)
        return permission.boolval


class ITeamFolder(Interface):
    """Marker interface for team folder"""


class TeamFolder(Folder):
    implements(ITeamFolder)

    current_id = -1

    def add_team(self, team):
        newid = self.current_id + 1
        self.current_id = newid
        team_id = str(newid)
        self[team_id] = team
        return team_id


class Team(Persistent):

    def __init__(self, title, description=None, members=None, leader=None):
        """A team"""
        self.title = title
        self.description = description
        if members is None:
            self.members = []
        else:
            self.members = members
        self.leader = leader

    @property
    def __acl__(self):
        """Allow the leader to edit the team
        """
        if self.leader:
            return [(Allow, self.leader, 'edit')]
        return []

    def member_fullname(self, username):
        root = find_root(self)
        profile = root['profiles'].get(username)
        if profile is None:
            return ''
        return "%s %s" % (profile.first_name, profile.last_name)

    def member_names(self):
        names = []
        for member in self.members:
            names.append(self.member_fullname(member))
        return names

    def can_edit(self):
        """This seems totally wrong...
        """
        request = get_current_request()
        permission = has_permission('edit', self, request)
        return permission.boolval


class IUserFolder(Interface):
    """Marker interface for the user folder"""


class UserFolder(Users):
    implements(IUserFolder)


class IProfile(Interface):
    """Marker interface for a profile"""


class Profile(Persistent):
    implements(IProfile)

    def __init__(self, first_name, last_name, email, username):
        """User Profile"""
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username


class IProfileFolder(Interface):
    """Marker interface for profile folder"""


class ProfileFolder(Folder):
    implements(IProfileFolder)

    def add_profile(self, profile):
        # XXX: check for existing username
        self[profile.username] = profile
        return profile.username


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = PollingPlace()
        zodb_root['app_root'] = app_root
        # set up the folder for the votes
        voting_booth = VotingBoothFolder()
        voting_booth.__name__ = 'votes'
        voting_booth.__parent__ = app_root
        app_root['votes'] = voting_booth
        # set up the user folder
        user_folder = UserFolder()
        user_folder.__name__ = 'users'
        user_folder.__parent__ = app_root
        app_root['users'] = user_folder
        # add a default admin user
        app_root['users'].add('admin', 'admin', 'admin')
        app_root['users'].add_user_to_group('admin', 'group:administrators')
        # profiles folder
        profile_folder = ProfileFolder()
        profile_folder.__name__ = 'profiles'
        profile_folder.__parent__ = app_root
        app_root['profiles'] = profile_folder
        import transaction
        transaction.commit()
    return zodb_root['app_root']
