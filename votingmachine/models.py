from persistent import Persistent
from persistent.mapping import PersistentMapping
from zope.interface import Interface
from zope.interface import implements
from pyramid.security import Allow
from pyramid.security import Everyone
from repoze.folder import Folder
from repoze.who.plugins.zodb.users import Users


class PollingPlace(PersistentMapping):
    __parent__ = __name__ = None
    __acl__ = [
        (Allow, Everyone, 'view'),
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


class IVotingBooth(Interface):
    """Marker interface for voting booth"""


class VotingBooth(Folder):
    implements(IVotingBooth)

    winner = None

    def __init__(self, title, start, end, categories):
        """The container for a FedEx day vote"""
        # initialize the folder settings
        super(VotingBooth, self).__init__()
        self.title = title
        self.start = start
        self.end = end
        self.categories = categories
        self.results = []


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

    def __init__(self, title, description=None):
        """A FedEx day team"""
        self.title = title
        self.description = description


class IUserFolder(Interface):
    """Marker interface for the user folder"""


class UserFolder(Users):
    implements(IUserFolder)


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = PollingPlace()
        zodb_root['app_root'] = app_root
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
        import transaction
        transaction.commit()
    return zodb_root['app_root']
