from api import common

@api.route('/users')
def get_users():
    print "v1 /users called"
    return common.get_users()


