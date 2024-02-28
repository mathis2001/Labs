from flask import Flask, request, abort
from flask_restful import Api, Resource
from urllib.parse import unquote
import json

app = Flask(__name__)
api = Api(app)

data = json.load(open('users.json', 'r'))
currentUserData = json.load(open('users_detailed.json', 'r'))

class UsersDetails(Resource):
    def get(self, id):
        try:
            return {'user': data['accounts'][id]}
        except:
            return 'Invalid id'

class CurrentUser(Resource):
    def get(self):
        email_cookie = request.cookies.get('email')
        if email_cookie:
            decoded_email = unquote(email_cookie)
            for user_id, user_info in currentUserData['accounts'].items():
                if user_info.get('email') == decoded_email:
                    return {'user': user_info}
            return abort(404, f'User not found: {decoded_email}')
        else:
            return abort(500, 'Cookie not provided: "email"')

api.add_resource(UsersDetails, '/users/<string:id>')
api.add_resource(CurrentUser, '/users/me')

@app.route('/')
def index():
    return '404 not found'

@app.route('/users')
def users():
    return abort(403, 'You are not authorized to access this endpoint.')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337, debug=True)
