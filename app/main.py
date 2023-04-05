
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'
socketio = SocketIO(app)

@app.route('/')
def sessions():
    return render_template('index.html')

def messageReceived(methods=['GET', 'POST']):
    print('Recieved')

@socketio.on('event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received: ' + str(json))
    socketio.emit('Response', json, callback=messageReceived)

if __name__ == '__main__':
    socketio.run(app)