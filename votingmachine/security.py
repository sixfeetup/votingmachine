def groupfinder(userid, request):
    root = request.root
    user_folder = root['users']
    user = user_folder.get(userid)
    if user is None:
        return []
    return user['groups']


def callback(content, info):
    return
