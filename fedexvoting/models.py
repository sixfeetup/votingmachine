from persistent import Persistent
from persistent.mapping import PersistentMapping
from repoze.folder import Folder


class PollingPlace(PersistentMapping):
    __parent__ = __name__ = None


class VotingBoothFolder(Folder):

    current_id = -1

    def add_booth(self, booth):
        newid = self.current_id + 1
        self.current_id = newid
        booth_id = str(newid)
        self[booth_id] = booth
        return booth_id


class VotingBooth(Persistent):

    def __init__(self, title, start, end):
    def __init__(self, title, start, end, categories):
        """The container for a FedEx day vote"""
        self.title = title
        self.start = start
        self.end = end
        self.categories = categories
def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = PollingPlace()
        zodb_root['app_root'] = app_root
        voting_booth = VotingBoothFolder()
        voting_booth.__name__ = 'votes'
        voting_booth.__parent__ = app_root
        app_root['votes'] = voting_booth
        import transaction
        transaction.commit()
    return zodb_root['app_root']
