from bson import ObjectId
from flask import Flask, jsonify, request
from mongo_setup import clubs, users
from testudo_api import verify_conflict
app = Flask(__name__)


#######################################################################################
############################# ORGANIZER FUNCTIONS #####################################
#######################################################################################

@app.route('/api/check_conflict/<start_time>/<end_time>/', methods=['GET'])
def check_conflicts(start_time, end_time):
    school = request.args.get('school')

    if school:
        data = jsonify(verify_conflict(start_time, end_time, school))
    else:
        data = jsonify(verify_conflict(start_time, end_time))
        
    return data, 200

def index():
    return 'Hello, World!'


@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/isUserAssociated/<email>', methods=['GET'])
def isUserAssociated(email):

    foundUser = clubs.find_one({'club_organizer_associated_email': email})

    if foundUser:
        return jsonify({'associated': True,
                        'club_organizer_associated_email': foundUser['club_organizer_associated_email'],
                        'club_name': foundUser['club_name'],
                        'club_description': foundUser['club_description'],
                        # 'club_category': foundUser['club_category'],
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
    club_category = data.get('club_category')

    try:

        exists = clubs.find_one({'club_name': club_name})

        if exists:
            return jsonify({'message': 'Club already exists'}), 500

        clubs.insert_one({'club_organizer_associated_email': club_organizer_associated_email,
                          'club_name': club_name,
                          'club_description': club_description,
                          'club_category': club_category,
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

        event_id = ObjectId()

    
        new_event = {
            '_id': event_id,
            'event_club': club_name,
            'event_title': event_title,
            'event_description': event_description,
            'event_location': event_location,
            'event_date': event_date,
            'event_time': event_time,
            'registered': []
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

    try: 
        club = clubs.find_one({'club_name': club_name})
        
        if club:
                events = []

                for event in club['events']:
                    event['_id'] = str(event['_id'])
                    events.append(event)

                return jsonify({'events': events}), 200

    except Exception as error:
        print(error)
    
    return jsonify({'events': []}), 409

@app.route('/fetchEventAttendees/<club_name>/<event_id>', methods=['GET'])
def fetchEventAttendees(club_name, event_id):

    print("in fetcheventattendees")
    try: 
        club = clubs.find_one({'club_name': club_name})
        print(club)

        if club:
            members = []

            for event in club['events']:
                print(event)
                if event['_id'] == ObjectId(event_id):
                    print("matched")
                    for member_id in event['registered']:
                        curr_member = users.find_one({'_id': ObjectId(member_id)})
                        print(curr_member)
                        curr_member['_id'] = str(curr_member['_id'])
                        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                        members.append(curr_member)

            return jsonify({'members': members}), 200

    except Exception as error:
        print(error)
        return jsonify({'members': []}), 409
    
@app.route('/fetchClubMembers/<club_name>', methods=['GET'])
def fetchClubMembers(club_name):

    try: 
        club = clubs.find_one({'club_name': club_name})
        
        if club:
            members = []

            for member in club['members']:
                curr_Member = users.find_one({'_id': ObjectId(member['member_id'])})
                curr_Member['_id'] = str(curr_Member['_id'])
                members.append(curr_Member)

            return jsonify({'members': members}), 200

    except Exception as error:
        print(error)
        return jsonify({'members': []}), 409



#######################################################################################
############################# MEMBER FUNCTIONS ########################################
#######################################################################################
    

@app.route('/createMember', methods=['POST'])
def createMember():
  
    data = request.get_json()

    member_firebase_uid = data.get('member_firebase_uid')
    member_firstname = data.get('member_firstname')
    member_lastname = data.get('member_lastname')
    member_email = data.get('member_email')


    try: 
        users.insert_one({'member_firebase_uid': member_firebase_uid, 'member_firstname': member_firstname, 'member_lastname': member_lastname, 'member_email': member_email, 'clubs_enrolled_in': [], 'events_attending': []})
        return jsonify({'message': 'member created successfully'}), 201
    
    except Exception as error:
        print(error)
        return jsonify({'message': 'member creation failed'}), 500
    

@app.route('/fetchMemberProfile/<email>', methods=['GET'])
def fetchMemberProfile(email):

    member_profile = users.find_one({'member_email': email})
    member_profile['_id'] = str(member_profile['_id'])

    if member_profile:
        return jsonify({'member_profile': member_profile}), 201
    else:
        return jsonify({'message':'Error fetchingMemberProfile'}), 400


@app.route('/fetchClub/<club_name>', methods=['GET'])
def fetchClub(club_name):
    
    club = clubs.find_one({"club_name": club_name}, {"_id": False, "members": False, "events": False})

    print(club)

    if club:
        return jsonify({'club': club}), 200
    else:
        return jsonify({'club': None}), 409



@app.route('/fetchClubs/<category>', methods=['GET'])
def fetchClubs(category):

    if category == "All_Clubs":
        clubs_Found = clubs.find({}, {'_id': False, 'members': False, 'events': False})
    else:
        category = category.replace("_", " ")
        clubs_Found = clubs.find({'club_category': category}, {'_id': False, 'members': False, 'events': False})

    clubs_list = [club for club in clubs_Found]

    if clubs_list:
        return jsonify({'clubs': clubs_list}), 200
    else:
        return jsonify({'clubs': []}), 409

@app.route('/joinClub/<club_name>/<member_id>', methods=['POST'])
def joinClub(club_name, member_id):

    # data = request.get_json()

    # member_email = data.get('member_email')
    # member_firstname = data.get('member_firstname')
    # member_lastname = data.get('member_lastname')

    club = clubs.find_one({'club_name': club_name})
    user = users.find_one({'_id': ObjectId(member_id)})

    if club and user:
        
        club_id = club['_id']
        user_id = user['_id']

        joining_member = {
            'member_id': user_id,
        }

        try:
            wasAddedToClub = clubs.update_one(
                            {'_id': club_id},
                            {'$addToSet': {'members': joining_member}})
            
            updatedUsersClubList = users.update_one(
                {'_id': user_id},
                {'$addToSet': {'clubs_enrolled_in': club_name}})

            if wasAddedToClub.modified_count >= 1 and updatedUsersClubList.modified_count >= 1:
                return jsonify({'message': 'updating club roster and users club list was successful'}), 201
            else:
                return jsonify({'message': 'updating club and users club list was not successful'}), 409
        
        except Exception as error:
            print(error)
    
    return jsonify({'message': 'joining member failed'}), 500
    

@app.route('/leaveClub/<club_name>', methods=['POST'])
def leaveClub(club_name):
    
    data = request.get_json()

    member_id = data.get('member_id')

    club = clubs.find_one({'club_name': club_name})
    user = users.find_one({'_id': ObjectId(member_id)})

    if club and user:

        club_id = club['_id']
        user_id = user['_id']

        try:
            wasRemovedFromClub = clubs.update_one(
                            {'_id': ObjectId(club_id)},
                            {'$pull': {'members': {'member_id': ObjectId(user_id)}}})
            
            updatedUsersClubList = users.update_one(
                {'_id': user_id},
                {'$pull': {'clubs_enrolled_in': club_name}})

            if wasRemovedFromClub.modified_count >= 1 and updatedUsersClubList.modified_count >= 1:
                return jsonify({'message': 'updating club roster and users club list was successful'}), 201
            else:
                return jsonify({'message': 'updating club and users club list was not successful'}), 409
        
        except Exception as error:
            print(error)
            return jsonify({'message': 'removing member failed'}), 500

@app.route('/attendEvent/<club_name>/<event_id>/<member_id>', methods=['POST'])
def attendEvent(club_name, event_id, member_id):

    try:
        club_event = clubs.update_one({'club_name': club_name, 'events._id': ObjectId(event_id)},{'$push': {'events.$.registered': member_id}})
        
        user_modified = users.update_one({'_id': ObjectId(member_id)}, {'$push': {'events_attending': event_id}})

        if club_event.modified_count < 1 or user_modified.modified_count < 1:
            return jsonify({'message': 'Failed to add {member_id} to {event_id}'}), 500
        else:
            return jsonify({'message': 'successfully added {member_id} to {event_id}'}), 201


    except Exception as e:
        print(e)
        return jsonify({'message': 'Failed to add {member_id} to {event_id}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
