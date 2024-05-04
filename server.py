from flask import Flask, jsonify, request
from mongo_setup import client, clubs

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/isUserAssociated/<email>', methods=['GET'])
def isUserAssociated(email):

    print("im here in isUserAssociated")
    foundUser = clubs.find_one({'club_organizer_associated_email': email})
    
    print(foundUser)

    if foundUser:
        return jsonify({'associated': True,
                        'club_organizer_associated_email': foundUser['club_organizer_associated_email'],
                        'club_name': foundUser['club_name'],
                        'club_descripton': foundUser['club_descripton'],
                        # 'club_members': foundUser['members'],
                        # 'club_events': foundUser['events']
                        }), 200
    else:
        return jsonify({'associated': False}), 200


@app.route('/createClub', methods=['POST'])
def createClub():
   
    data = request.get_json()

    club_organizer_associated_email = data.get('user_email')
    club_name = data.get('club_name')
    club_description = data.get('club_description')

    try:
        clubs.insert_one({'club_organizer_associated_email': club_organizer_associated_email,
                          'club_name': club_name,
                          'club_descripton': club_description,
                          'members': [],
                          'events': []})
        return jsonify({'message': 'Club created successfully'}), 201
    
    except Exception as error:
        print(error)
        return jsonify({'message': 'Club creation failed'}), 500

@app.route('/addEvent', methods=['POST'])
def addEvent():

    data = request.get_json()

    club_name = data.get('club_name')
    event_title = data.get('event_title')
    event_description = data.get('event_description')
    event_location = data.get('event_location')
    event_date = data.get('event_date')
    event_time = data.get('event_time')

    club = clubs.find_one({'club_name': club_name})

    if club:

        club_id = club['_id']

        new_event = {
            'event_title': event_title,
            'event_description': event_description,
            'event_location': event_location,
            'event_date': event_date,
            'event_time': event_time,
            'registered': 0
        }

        try:
            result = clubs.update_one(
                            {'_id': club_id},
                            {'$addToSet': {'events': new_event}})

            if result.modified_count >= 1:
                return jsonify({'message': 'Event created successfully'}), 201
            else:
                return jsonify({'message': 'Event creation failed'}), 409
        
        except Exception as error:
            print(error)
            return jsonify({'message': 'Event creation failed'}), 500

@app.route('/fetchClubEvents/<club_name>', methods=['GET'])
def fetchClubEvents(club_name):

    club = clubs.find_one({'club_name': club_name})
    
    if club:
            return jsonify({'events': club['events']}), 201
    else:
            return jsonify({'events': []}), 409




if __name__ == '__main__':
    app.run(debug=True)
