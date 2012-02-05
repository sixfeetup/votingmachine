def groupfinder(userid, request):
    root = request.root
    user_folder = root['users']
    user = user_folder.get(userid)
    return user['groups']
