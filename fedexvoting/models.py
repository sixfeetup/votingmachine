from persistent.mapping import PersistentMapping

class PollingPlace(PersistentMapping):
    __parent__ = __name__ = None

def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = PollingPlace()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']
