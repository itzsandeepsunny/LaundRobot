from flask import Flask, json, request, jsonify, session
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS
from flask_apscheduler import APScheduler
from datetime import datetime, timezone, tzinfo
import random
import sys

sys.path.insert(0, '../local-libs/site-packages')

#
#   Setting up server
#

HOST = '127.0.0.1'
PORT = 5000

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)

socketio = SocketIO(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# TODO: Make Robot a class? (to store various information: status, type, etc)

clients_sid = []
clients_type = []
pickstatus = "disconnected"
picked = 0
sortstatus = "disconnected"
sorted_color1 = 0
sorted_color2 = 0
sorted_color3 = 0
sorted_color4 = 0
colorlist = [1, 2, 3, 4]


@app.route("/")
def index():
    x = """Welcome to the Flask Server<br>
    Links for testing purposes on <b>Local Server</b><br>
    <a href="http://127.0.0.1:5000/getone">getallrobots</a><br>
    <a href="http://127.0.0.1:5000/getpickerinfo">getpickerinfo</a><br>
    <a href="http://127.0.0.1:5000/getsorterinfo">getsorterinfo</a><br>
    <a href="http://127.0.0.1:5000/turnoff">turnoff</a><br>
    <a href="http://127.0.0.1:5000/turnon">turnon</a><br>
    <a href="http://127.0.0.1:5000/settimer">settimer</a><br>
    <a href="http://127.0.0.1:5000/setcolor">setcolor</a><br>"""
    return (x)


@app.route("/getallrobots")
def getallrobots():
    scheduler.add_job(func=scheduled_picker, trigger='interval', seconds=300, id='chrono_picker')
    if (scheduler.get_jobs() != []):
        if (scheduler.get_jobs() != []):
            for job in scheduler.get_jobs():
                if (job.name == 'chrono_picker'):
                    time = job.next_run_time

    print(secondsleft(time))

    x = """{
    "success": true,
    "body": {
        "robots": [
            {
                "id": "1"
                "type" : "1",
                "name": "Name1",
                "status": "idle | disconnected | running"
            },
            {
                "id": "2"
                "type" : "2",
                "name": "Name2",
                "status": "idle | disconnected | running"
            }
        ]
         }
        }"""
    return jsonify(x)


@app.route("/getpickerinfo")
def getpickerinfo():
    time = 0
    set = False
    update_pick_status()
    if (scheduler.get_jobs() != []):
        if id == "1":
            for job in scheduler.get_jobs():
                if (job.name == 'chrono_picker'):
                    time = job.next_run_time
                    set = True
    x = {
        "success": True,
        "body": {
            "name": "Name1",
            "type": "1",
            "status": pickstatus,
            "timer": {
                "set": set,
                "time_left": secondsleft(time)
            },
            "picked_up_items": picked
        }
    }
    return jsonify(x)


@app.route("/getsorterinfo")
def getsorterinfo():
    time = 0
    set = False
    update_sort_status()
    if (scheduler.get_jobs() != []):
        if id == "2":
            for job in scheduler.get_jobs():
                if (job.name == 'chrono_sorter'):
                    time = job.next_run_time
                    set = True

    x = {
        "success": True,
        "body": {
            "name": "Name2",
            "type": "2",
            "status": sortstatus,
            "timer": {
                "set": set,
                "time_left": secondsleft(time)
            },
            "baskets": [
                sorted_color1,
                sorted_color2,
                sorted_color3,
                sorted_color4
            ],
            "colors": colorlist
        }
    }
    return jsonify(x)


@app.route("/getone")
def getone():
    id = request.args.get('robotid')
    time = 0
    set = False
    if id == "1":
        update_pick_status()
        if (scheduler.get_jobs() != []):
            for job in scheduler.get_jobs():
                if (job.name == 'chrono_picker'):
                    time = job.next_run_time
                    set = True
        x = {
            "success": True,
            "body": {
                "id": "1",
                "type": "1",
                "name": "Name1",
                "status": pickstatus,
                "timer": {
                    "set": set,
                    "time_left": secondsleft(time)
                },
                "picked_up_items": str(picked)
            }
        }
    elif id == "2":
        time = 0
        set = False
        update_sort_status()
        if (scheduler.get_jobs() != []):
            for job in scheduler.get_jobs():
                if (job.name == 'chrono_sorter'):
                    time = job.next_run_time
                    set = True
        x = {
            "success": True,
            "body": {
                "id": "2",
                "type": "2",
                "name": "Name2",
                "status": sortstatus,
                "timer": {
                    "set": set,
                    "time_left": secondsleft(time)
                },
                "baskets": [
                    sorted_color1,
                    sorted_color2,
                    sorted_color3,
                    sorted_color4
                ],
                "colors": colorlist
            }
        }
    return jsonify(x)


@app.route('/stop', methods=['GET'])
def stop():
    id = request.args.get('robotid')

    if id == "1":
        stop_pick_robot()
        # insert function here to turn off picker
        print("picker turned off")
        x = {
            "success": True,
            "body": {}
        }

    elif id == "2":
        stop_sort_robot()
        # insert function here to turn off sorter
        print("sorter turned off")
        x = {
            "success": True,
            "body": {}

        }

    else:
        print("++++++++++++++++++++++++++++++++++++++++++")
        print("incorrect robot id")
        print("++++++++++++++++++++++++++++++++++++++++++")
        x = {
            "success": False,
            "body": {"errMessage": "incorrect robot id"}
        }

    return jsonify(x)


@app.route('/start', methods=['GET'])
def start():
    id = request.args.get('robotid')

    if id == "1":
        start_pick_robot()

        # insert function here to turn on picker
        print("picker turned on")
        x = {
            "success": True,
            "body": {
                "timer": {
                    "set": True,
                    "time_left": ""
                }
            }
        }
    elif id == "2":
        start_sort_robot()

        # insert function here to turn on picker
        print("picker turned on")
        x = {
            "success": True,
            "body": {
                "timer": {
                    "set": True,
                    "time_left": ""
                }
            }
        }
    else:
        print("++++++++++++++++++++++++++++++++++++++++++")
        print("incorrect robot id")
        print("++++++++++++++++++++++++++++++++++++++++++")
        x = {
            "success": False,
            "body": {"errMessage": "incorrect robot id"}
        }

    return jsonify(x)


@app.route('/settimer', methods=['POST'])
def settimer():
    time = 180
    set = False
    json_data = request.json
    id = json_data['robot_id']
    set = json_data['set']
    time = json_data['time']
    print(set)

    if set == False:
        if id == "1":
            if (scheduler.get_jobs() != []):
                for job in scheduler.get_jobs():
                    if (job.name == 'chrono_picker'):
                        scheduler.remove_job(id='chrono_picker')

            print('Scheduler reset for picker')
            x = {
                "success": True,
                "body": {
                    "timer": {
                        "set": False,
                        "time_left": 0
                    }
                }
            }
        elif id == "2":
            if (scheduler.get_jobs() != []):
                for job in scheduler.get_jobs():
                    if (job.name == 'chrono_sorter'):
                        scheduler.remove_job(id='chrono_sorter')
            print('Scheduler reset for sorter')
            x = {
                "success": True,
                "body": {
                    "timer": {
                        "set": False,
                        "time_left": 0
                    }
                }
            }
        else:
            print("++++++++++++++++++++++++++++++++++++++++++")
            print("incorrect robot id")
            print("++++++++++++++++++++++++++++++++++++++++++")
            x = {
                "success": False,
                "body": {"errMessage": "incorrect robot id"}
            }


    elif set == True:
        if id == "1":
            if (scheduler.get_jobs() != []):
                for job in scheduler.get_jobs():
                    if (job.name == 'chrono_picker'):
                        scheduler.remove_job(id='chrono_picker')
            scheduler.add_job(func=scheduled_picker, trigger='interval', seconds=int(time), id='chrono_picker')
            # print('Scheduler set for picker for '+time+'seconds')
            x = {
                "success": True,
                "body": {
                    "timer": {
                        "set": True,
                        "time_left": time
                    }
                }
            }
        elif id == "2":
            if (scheduler.get_jobs() != []):
                for job in scheduler.get_jobs():
                    if (job.name == 'chrono_sorter'):
                        scheduler.remove_job(id='chrono_sorter')
            scheduler.add_job(func=scheduled_sorter, trigger='interval', seconds=int(time), id='chrono_sorter')
            # print('Scheduler set for sorter for '+secondsleft(time)+'seconds')
            x = {
                "success": True,
                "body": {
                    "timer": {
                        "set": True,
                        "time_left": time
                    }
                }
            }
        else:
            print("++++++++++++++++++++++++++++++++++++++++++")
            print("incorrect robot id")
            print("++++++++++++++++++++++++++++++++++++++++++")
            x = {
                "success": False,
                "body": {"errMessage": "incorrect robot id"}
            }

    return jsonify(x)


@app.route('/setcolor', methods=['POST'])
def setcolor():
    global colorlist
    json_data = request.json
    id = json_data['robot_id']
    colorlist = json_data['colors']
    if id == "2":
        # Insert function for setting colors
        x = {
            "success": True,
            "body": {
                "colors": colorlist
            }
        }

    else:
        print("incorrect robot id")
        x = {
            "success": False,
            "body": {"errMessage": "incorrect robot id"}
        }

    return jsonify(x)


#
# some functions for the server
#

@socketio.event
def add_client_to_room(client_sid):
    clients_sid.append(client_sid)

    room = session.get('room')
    join_room(room)

    emit('pass_message', client_sid + 'ready', room=clients_sid[clients_sid.index(client_sid)])


def remove_client(client_sid):
    clients_type.remove(clients_type[clients_sid.index(client_sid)])
    clients_sid.remove(client_sid)


def get_pick_robot_id():
    return clients_sid[clients_type.index("pick")]


def get_sort_robot_id():
    return clients_sid[clients_type.index("sort")]


#
# Scheduler Function
#

def scheduled_picker():
    stop_pick_robot()
    if (scheduler.get_jobs() != []):
        for job in scheduler.get_jobs():
            if (job.name == 'chrono_picker'):
                scheduler.remove_job(id='chrono_picker')
    print('Event Triggered')


def scheduled_sorter():
    stop_sort_robot()
    if (scheduler.get_jobs() != []):
        for job in scheduler.get_jobs():
            if (job.name == 'chrono_sorter'):
                scheduler.remove_job(id='chrono_sorter')
    print('Event Triggered')


def secondsleft(scheduled):
    if scheduled == 0:
        return 0
    else:
        scheduled = scheduled.replace(tzinfo=None)
        seconds = int((scheduled - datetime.now()).total_seconds())
        return (seconds)


#
# Client Connection functions
#

@socketio.on('connect', namespace='/pick')
def handle_message():
    print("++++++++++++++++++++++++++++++++++++++++++")
    print("A picking robot client is connected id: " + request.sid)
    print("++++++++++++++++++++++++++++++++++++++++++")

    if clients_type.count("pick") == 0:
        add_client_to_room(request.sid)
        clients_type.append("pick")


@socketio.on('connect', namespace='/sort')
def handle_message():
    print("++++++++++++++++++++++++++++++++++++++++++")
    print("A sorting robot client is connected id: " + request.sid)
    print("++++++++++++++++++++++++++++++++++++++++++")

    if clients_type.count("sort") == 0:
        add_client_to_room(request.sid)
        clients_type.append("sort")


@socketio.on('connect')
def test_connect():
    print("++++++++++++++++++++++++++++++++++++++++++")
    print("A client is connected id: " + request.sid)
    print("++++++++++++++++++++++++++++++++++++++++++")
    socketio.send("Welcome Robot")


@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)


@socketio.on('disconnect', namespace='/pick')
def test_connect():
    print("++++++++++++++++++++++++++++++++++++++++++")
    print("A picking robot was disconnected")
    print("++++++++++++++++++++++++++++++++++++++++++")
    remove_client(get_pick_robot_id())


@socketio.on('disconnect', namespace='/sort')
def test_connect():
    print("++++++++++++++++++++++++++++++++++++++++++")
    print("A sorting was disconnected")
    print("++++++++++++++++++++++++++++++++++++++++++")
    remove_client(get_sort_robot_id())


@socketio.on('disconnect')
def test_connect():
    print("++++++++++++++++++++++++++++++++++++++++++")
    print("A client was disconnected")
    print("++++++++++++++++++++++++++++++++++++++++++")


@socketio.on('update_status', namespace='/pick')
def handle_json(data):
    print('received json: ' + str(data))
    global pickstatus
    global picked
    pickstatus = data['status']
    picked = data['picked']

    print(pickstatus)
    print(picked)

    # TODO: show above information to GUI


@socketio.on('update_status', namespace='/sort')
def handle_json(data):
    print('received json: ' + str(data))
    global sortstatus
    global sorted_color1
    global sorted_color2
    global sorted_color3
    global sorted_color4
    sortstatus = data['status']
    sorted_color1 = data['sorted_color1']
    sorted_color2 = data['sorted_color2']
    sorted_color3 = data['sorted_color3']
    sorted_color4 = data['sorted_color4']

    print(sortstatus)
    print(sorted_color1);
    print(sorted_color2);
    print(sorted_color3);
    print(sorted_color4);

    # TODO: show above information to GUI


#
# Below are functions to control the robot via sending messages
# to clients (will be called by interacting with the web app GUI)
#

# @socketio.event
# def start_robot(robotid):
#     if (clients_type(robotid) == "pick"):
#         start_pick_robot()
#     if (clients_type(robotid) == "sort"):
#         start_sort_robot()


# @socketio.event
# def stop_robot(robotid):
#     if (clients_type(robotid) == "pick"):
#         stop_pick_robot()
#     if (clients_type(robotid) == "sort"):
#         stop_sort_robot()


# @socketio.event
# def update_status(robotid):     # call this function when you need to update information on GUI
#     if (clients_type(robotid) == "pick"):
#         update_pick_status()
#     if (clients_type(robotid) == "sort"):
#         update_sort_status()


@socketio.event
def start_pick_robot():
    emit('pass_message', 'pick let go', namespace='/pick', room=get_pick_robot_id())
    emit('control', 'start', namespace='/pick', room=get_pick_robot_id())


@socketio.event
def stop_pick_robot():
    emit('pass_message', 'pick pls stop', namespace='/pick', room=get_pick_robot_id())
    emit('control', 'stop', namespace='/pick', room=get_pick_robot_id())


@socketio.event
def start_sort_robot():
    emit('pass_message', 'sort let go', namespace='/sort', room=get_sort_robot_id())
    emit('control', 'start', namespace='/sort', room=get_sort_robot_id())


@socketio.event
def stop_sort_robot():
    emit('pass_message', 'sort pls stop', namespace='/sort', room=get_sort_robot_id())
    emit('control', 'stop', namespace='/sort', room=get_sort_robot_id())


@socketio.event
def update_pick_status():
    if clients_type.count("pick") == 1:
        emit('pass_message', 'pick pls update', namespace='/pick', room=get_pick_robot_id())
        emit('control', 'get status', namespace='/pick', room=get_pick_robot_id())
    else:
        global pickstatus
        global picked
        pickstatus = "disconnected"
        picked = 0


@socketio.event
def update_sort_status():
    if clients_type.count("sort") == 1:
        emit('pass_message', 'sort pls update', namespace='/sort', room=get_sort_robot_id())
        emit('control', 'get status', namespace='/sort', room=get_sort_robot_id())
    else:
        global sortstatus
        global sorted_color1
        global sorted_color2
        global sorted_color3
        global sorted_color4
        sortstatus = "disconnected"
        sorted_color1 = 0
        sorted_color2 = 0
        sorted_color3 = 0
        sorted_color4 = 0


@socketio.event
def move_pick_forward(time):
    emit('pass_message', 'pick go forward ' + str(time), namespace='/pick', room=get_pick_robot_id())
    emit('forward', str(time), namespace='/pick', room=get_pick_robot_id())


@socketio.event
def move_pick_backward(time):
    emit('pass_message', 'pick go backward ' + str(time), namespace='/pick', room=get_pick_robot_id())
    emit('backward', str(time), namespace='/pick', room=get_pick_robot_id())


@socketio.event
def turn_left_pick(angle):
    emit('pass_message', 'pick turn left ' + str(angle), namespace='/pick', room=get_pick_robot_id())
    emit('turn left', str(angle), namespace='/pick', room=get_pick_robot_id())


@socketio.event
def turn_right_pick(angle):
    emit('pass_message', 'pick turn right ' + str(angle), namespace='/pick', room=get_pick_robot_id())
    emit('turn right', str(angle), namespace='/pick', room=get_pick_robot_id())


@socketio.event
def break_robot():
    pass


@socketio.event
def pick_pickup():
    pass


@socketio.event
def pick_putdown():
    pass


@socketio.event
def reset(robotid):
    if (clients_type(robotid) == "pick"):
        emit('pass_message', 'pick pls reset', namespace='/pick', room=get_pick_robot_id())
        emit('control', 'reset status', namespace='/pick', room=get_pick_robot_id())
    if (clients_type(robotid) == "sort"):
        emit('pass_message', 'sort pls reset', namespace='/sort', room=get_sort_robot_id())
        emit('control', 'reset status', namespace='/sort', room=get_sort_robot_id())


if __name__ == '__main__':
    socketio.run(app, host=HOST, port=PORT)
