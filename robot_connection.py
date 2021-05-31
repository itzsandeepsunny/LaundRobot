import socketio

sio = socketio.Client()

serverip = "https://laundrobo.herokuapp.com:5000/"

@sio.event
def connect():
    print("Conneted to server")
    sio.send("Robot has connected")

@sio.event
def connect_error():
    print("Error")

@sio.event
def disconnect():
    print("Disconnected!")


@sio.on('message')
def on_message(data):
    print('I received a message!:' +data)


if __name__ == "__main__":
    sio.connect(serverip)
    sio.send("Hello Server")

    try:
        while True:
            pass

    except KeyboardInterrupt:
        sio.disconnect()
        print("Disconnect button was pressed")
