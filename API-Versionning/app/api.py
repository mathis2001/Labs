from flask import Flask, request, abort, Response
from flask_restful import Api, Resource, reqparse
from flasgger import Swagger, swag_from
from functools import wraps
import jwt
import re
import random
import requests
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "SUPER_SECURE_SECRET"
api = Api(app)

missioninfo = json.load(open('missioninfo.json', 'r'))

access_count = 0


class User:
    def __init__(self):
        self.file_path = 'users.json'

    def find_by_email(self, email):
        with open(self.file_path, 'r') as f:
            users = json.load(f)
            for user in users:
                if user['email'] == email:
                    return user
        return None

        def login(self, email, password):
            return self.find_by_email(email)

def validate_email(email):
    if not email:
        return "Email is required"
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Invalid email format"
    return True

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
                "message": "Your are not authenticated.",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data
        except jwt.ExpiredSignatureError:
            return {'message': 'Token is expired!'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Token is invalid!'}, 401

        return f(current_user, *args, **kwargs)

    return decorated

def requires_basic_auth(f):

    def check_auth(username, password):
        return username == "guest" and password == "guest"

    def authenticate():
        return Response(
            "Authentication required.", 401,
            {"WWW-Authenticate": "Basic realm='Login Required'"},
        )

    @wraps(f)
    def decorated(*args, **kwargs):
        if __name__ != "__main__":
            return f(*args, **kwargs)

        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated

swagger = Swagger(app, decorators=[ requires_basic_auth ])

@app.route("/api/token", methods=["POST"])
def login():
    try:
        data = request.json
        if not data or not data.get('email'):
            return {
                "message": "Please provide a valid email",
                "data": None,
                "error": "Bad request"
            }, 400

        email = data.get('email')
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {
                "message": "Invalid email format",
                "data": None,
                "error": "Bad request"
            }, 400

        user = User().find_by_email(email)
        if user:
            try:
                token_payload = {
                    "email": email,
                    "name": user["name"],
                    "function": user["function"],
                    "mission": user["mission"],
                    "active": user["active"],
                    "launchSite": user["launchSite"],
                    "role": user["role"]
                }
                token = jwt.encode(
                    token_payload,
                    app.config["SECRET_KEY"],
                    algorithm="HS256"
                )

                return {
                    "message": "Successfully fetched auth token",
                    "data": {
                        "user": email,
                        "token": token
                    }
                }, 200
            except Exception as e:
                return {
                    "error": "Something went wrong",
                    "message": str(e)
                }, 500
        else:
            return {
                "message": "User not found",
                "data": None,
                "error": "Unauthorized"
            }, 404

    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500


def jsonresponse(data):
    response = app.response_class(
            response=json.dumps(data, indent=2),
            status=200,
            mimetype='application/json'
            )
    return response

class CurrentUser(Resource):
    method_decorators = [token_required]

    def get(self, current_user):
        """
        This endpoint show the current user information. (Contact John at the following email to create an account john.doe@example.xyz)
        ---
        tags:
          - Users
        responses:
          200:
            description: ...
          500:
            description: Something went wrong
        """
        try:
            role = current_user.get("role")

            if role == "admin":
                current_user["role"] = "flag{Weak_4uth_Everywhere}"
            return {
                "data": {
                    "user": current_user,
                    "flag": "flag{S3cured_But_N0t_Secur3d}"
                }
            }, 200
        except Exception as e:
            return {
                "error": "Something went wrong",
                "message": str(e)
            }, 500


class missionCrewV2(Resource):
    method_decorators = [token_required]
    def get(self, id):
        """
        View the details of the crew for a specific mission
        ---
        tags:
          - Crew
        parameters:
        - in: path
          name: id
          required: true
          type: string
        responses:
          200:
            description: Mission Crew details
          403:
            description: You are not authorized to access this endpoint
          500:
            description: An error occured
        """
        return abort(403, 'You are not authorized to access this endpoint')

    def post(self, id):
        """
        Successfully added crew member to the mission
        ---
        tags:
          - Crew
        parameters:
        - in: path
          name: id
          required: true
          type: string
        - in: body
          name: crew
          consumes:
            - application/json
          required: true
          schema:
            type: object
            properties:
              name:
                type: string
              role:
                type: string
              background:
                type: string
              missions:
                type: integer
        responses:
          201:
            description: Crew member successfully added
          403:
            description: You are not authorized to access this endpoint
          500:
            description: An error occured
        """
        return abort(403, 'You are not authorized to create a new crew member for the mission')

    def delete(self, id):
        """
        Successfully deleted crew member from the mission
        ---
        tags:
          - Crew
        parameters:
        - in: path
          name: id
          required: true
          type: string
        - in: body
          name: memberID
          consumes:
            - application/json
          required: true
          schema:
            type: object
            properties:
              memberID:
                type: string
        responses:
          200:
            description: Crew member successfully deleted
          403:
            description: You are not authorized to access this endpoint
          404:
            description: Member not found
          500:
            description: An error occured
        """
        return abort(403, 'You are not authorized to delete crew member from the mission')

class missionCrewV1(Resource):
    def get(self, id):
        try:
            mission_part = {
                'mission': missioninfo['missions'][id]['missionName'],
                'isLaunched': missioninfo['missions'][id]['isLaunched']
            }
            crew_part = {'Operation crew': missioninfo['missions'][id]['crew']}
        
            full_part = {"mission details": mission_part, "crew details": crew_part}
        
            response = jsonresponse(full_part)
        
            return response
        except:
            return abort(404, 'Invalid Id')

    def post(self, id):
        return abort(500, 'An error occured')

    def delete(self,id):
        parser = reqparse.RequestParser()
        parser.add_argument('memberID', type=str, required=True, help='parameter is missing: memberID')
        args = parser.parse_args()

        try:
            mission = missioninfo['missions'][id]
            crew_members = mission['crew']
            member_index = next((index for (index, member) in enumerate(crew_members) if member['memberID'] == args.memberID), None)

            if member_index is not None:
                del crew_members[member_index]
                return 'Successfully deleted crew member from the mission, well done ! flag{N0_St4rs_4nym0re}', 200
            else:
                return abort(404, f'Member not found for id: {args.memberID}')
        except KeyError:
            return abort(404, 'Invalid mission id')



class missionIdV2(Resource):
    method_decorators = [token_required]
    def get(self, id):
        """
        View the details of a specific mission
        ---
        tags:
          - Missions Details
        parameters:
        - in: path
          name: id
          required: true
          type: string
        responses:
          200:
            description: View the confidential mission details
          403:
            description: You are not authorized to access this endpoint
          404:
            description: Invalid Id
          500:
            description: An error occured
        """
        return abort(403, 'You are not authorized to access this endpoint')


class missionIdV1(Resource):
    def get(self, id):
        details = {'mission': missioninfo['missions'][id]}
        response = jsonresponse(details)
        try:
            return response
        except:
            return abort(404, 'Invalid Id')

class missionDetailsV2(Resource):
    method_decorators = [token_required]
    def get(self):
        """
        View the full details of a mission
        ---
        tags:
          - Missions Details
        responses:
          200:
            description: View the confidential missions details
          403:
            description: You are not authorized to access this endpoint
          500:
            description: An error occured         
        """
        return abort(403, 'You are not authorized to access this endpoint')

class missionDetailsV1(Resource):
    def get(self):

        fullmissioninfo = json.load(open('missioninfo.json', 'r'))

        for mission_id, mission_data in fullmissioninfo['missions'].items():
            if request.path == '/api/v1/confidential/missions':
                encryption_key = mission_data.get('systems').get('Communications').get('encryption').get('encryptionKey')
                mission_data['systems']['Communications']['encryption']['encryptionKey'] = '*' * len(encryption_key)
            else:
                pass

        details = {'mission': fullmissioninfo['missions']}

        details = {'mission': missioninfo['missions']}
        response = jsonresponse(details)
        try:
            return response
        except:
            return abort(500, 'An error occured')

class missionComV2(Resource):
    method_decorators = [token_required]
    def get(self, id):
        """
        View the communications details about a mission
        ---
        tags:
          - Communications
        parameters:
        - in: path
          name: id
          required: true
          type: string
        responses:
          200:
            description: View the mission details about communications
          403:
            description: You are not authorized to access this endpoint
          500:
            description: An error occured
        """
        return abort(403, 'You are not authorized to access this endpoint')
    def patch(self, id):
        """
        This endpoint have been deprecated (hackers loves deprecated features ;p)
        ---
        tags:
          - Communications
        parameters:
        - in: path
          name: id
          required: true
          type: string
        - in: body
          consumes:
            - application/json
          name: xxx
          required: true
          type: string
          description: Maybe you should think to fuzz that endpoint
        responses:
          200:
            description: ...
          403:
            description: You are not authorized to access this endpoint
          500:
            description: An error occured
        """
        return abort(403, 'You are not authorized to access this endpoint')

class missionComV1(Resource):
    def get(self, id):
        try:
            mission_part = {
                'mission': missioninfo['missions'][id]['missionName'],
                'isLaunched': missioninfo['missions'][id]['isLaunched']
            }
            com_part = {'Communications': missioninfo['missions'][id]['systems']['Communications']}
        
            full_part = {"mission details": mission_part, "Communications details": com_part}
        
            response = jsonresponse(full_part)
        
            return response
        except:
            return abort(404, 'Invalid Id')

    def patch(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('callback', type=str, required=False)
        args = parser.parse_args()
        if id == "1":
            try:
                mission = missioninfo['missions'][id]
                callback_url = args['callback']

                if 'Communications' in mission['systems']:
                    mission['systems']['Communications']['messages']['callback'] = callback_url

                    with open('messages.txt', 'r') as messages_file:
                        messages_content = messages_file.read()

                    if callback_url.startswith("https://internal-communications.example.xyz"):
                        headers = {
                            'user-agent': 'StellarOS/4.2.3',
                            'X-Satellite': '2',
                            'X-Rocket': 'Stellar Explorer'
                        }
                        response = requests.post(callback_url, data=messages_content, headers=headers)

                        if response.status_code == 200:
                            return 'Callback URL changed successfully', 200
                        else:
                            return f'Error sending request to {callback_url}', response.status_code
                    else:
                        return abort(403, 'Invalid callback_url')
                else:
                    return abort(404, 'Communications system not found for the given mission id')
            except KeyError:
                return abort(404, 'Invalid mission id')
        else:
            return abort(404, 'Rocket not launched')

class missionPublicV2(Resource):
    method_decorators = [token_required]
    def get(self):
        """
        View the Public missions details
        ---
        tags:
          - Public
        responses:
          200:
            description: View the Public missions details
          500:
            description: An error occured
        """
        mission_public = {}
        for mission_id, mission_data in missioninfo['missions'].items():
            mission_details = {
                'missionName': mission_data.get('missionName'),
                'isLaunched': mission_data.get('isLaunched'),
                'rocket': mission_data['rocket'].get('name'),
                'launchSite': mission_data.get('launchSite')
            }
            mission_public[mission_id] = mission_details

        full_part = {"mission details": mission_public}
        
        response = jsonresponse(full_part)
        try:
            return response
        except:
            return abort(500, 'An error occured')

class missionPublicV1(Resource):
    def get(self):
        mission_public = {}
        for mission_id, mission_data in missioninfo['missions'].items():
            mission_details = {
                'missionName': mission_data.get('missionName'),
                'isLaunched': mission_data.get('isLaunched'),
                'rocket': mission_data['rocket'].get('name'),
                'launchSite': mission_data.get('launchSite')
            }
            mission_public[mission_id] = mission_details

        full_part = {"mission details": mission_public}
        
        response = jsonresponse(full_part)
        try:
            return response
        except:
            return abort(500, 'An error occured')

class weatherPublicV2(Resource):
    def post(self):
        """
        This endpoint use a third party service to check weather. Take care, it is limited to 25 free request by day and +1€ for each additional request...
        ---
        tags:
          - Weather
        parameters:
        - in: body
          consumes:
            - application/json
          name: city
          required: true
          schema:
            type: object
            properties:
              city:
                type: string
        responses:
          200:
            description: ...
          500:
            description: An error occured
        """
        global access_count
        data = request.get_json()
        city = data.get('city', None)
        access_count += 1

        if city:
            if access_count > 25:
                return 'Lack of rate limiting can cost money... flag{N0_M0n3y_D0wn}', 200

            else:

                weather_conditions = ['Sunny', 'Cloudy', 'Partly Cloudy', 'Rainy', 'Stormy', 'Snowy']
                temperature = random.randint(-10, 35)

                weather = random.choice(weather_conditions)

                weather_data = {
                    'city': city,
                    'weather': weather,
                    'temperature': f'{temperature} degrees'
                }

        try:
            return jsonresponse(weather_data)
        except:
            return abort(500, 'An error occured')

api.add_resource(missionCrewV1, '/api/v1/confidential/missions/<string:id>/crew')
api.add_resource(missionCrewV2, '/api/v2/confidential/missions/<string:id>/crew')
api.add_resource(missionIdV1, '/api/v1/confidential/missions/<string:id>/details')
api.add_resource(missionIdV2, '/api/v2/confidential/missions/<string:id>/details')
api.add_resource(missionComV1, '/api/v1/confidential/missions/<string:id>/communications')
api.add_resource(missionComV2, '/api/v2/confidential/missions/<string:id>/communications')
api.add_resource(missionDetailsV1, '/api/v1/confidential/missions')
api.add_resource(missionDetailsV2, '/api/v2/confidential/missions')
api.add_resource(missionPublicV2, '/api/v2/public/missions')
api.add_resource(missionPublicV1, '/api/v1/public/missions')
api.add_resource(weatherPublicV2, '/api/v2/public/weather')
api.add_resource(CurrentUser, '/api/v2/users/me')

@app.route('/')
def index():
    return '404 not found'

@app.route('/api/v2/<path:subpath>')
@app.route('/api/v1/<path:subpath>')
def Unauthorized(subpath):
    if subpath:
        return abort(403, 'You are not authorized to access this endpoint.')     
    else:
        return abort(404, 'The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.') 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337)
