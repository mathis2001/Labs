from flask import Flask, request, abort
from flask_restful import Api, Resource, reqparse
from flasgger import Swagger, swag_from
import requests
import json

app = Flask(__name__)
api = Api(app)

swagger = Swagger(app)

missioninfo = json.load(open('missioninfo.json', 'r'))

def jsonresponse(data):
    response = app.response_class(
            response=json.dumps(data, indent=2),
            status=200,
            mimetype='application/json'
            )
    return response

class missionCrewV2(Resource):
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
        - in: query
          name: memberID
          required: true
          schema:
            type: object
            properties:
              name:
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
                return f'Member not found for id: {args.memberID}', 404
        except KeyError:
            return 'Invalid mission id', 404



class missionIdV2(Resource):
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
        Replace the current callback url for communications between the ground control and the crew (under development)
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
                        response = requests.post(callback_url, data=messages_content)

                        if response.status_code == 200:
                            return 'Callback URL changed successfully', 200
                        else:
                            return f'Error sending request to {callback_url}', response.status_code
                    else:
                        return 'Invalid url'
                else:
                    return 'Communications system not found for the given mission id', 404
            except KeyError:
                return 'Invalid mission id', 404
        else:
            return abort(404, 'Rocket not launched')

class missionPublicV2(Resource):
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

@app.route('/')
def index():
    return '404 not found'

@app.route('/api/v1/IsAuthorized')
def IsAuthorized():
    return '{"IsAuthorized":false}'

@app.route('/api/v2/<path:subpath>')
@app.route('/api/v1/<path:subpath>')
def Unauthorized(subpath):
    if subpath:
        return abort(403, 'You are not authorized to access this endpoint.')     
    else:
        return abort(404, 'The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.') 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337, debug=True)
