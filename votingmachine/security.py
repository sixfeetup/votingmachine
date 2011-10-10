USERS = {'editor':'editor', 'viewer':'viewer'}
GROUPS = {'editor':['group:administrators']}


def groupfinder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])
