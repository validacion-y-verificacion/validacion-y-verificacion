from flask import Flask, render_template, request, redirect, url_for
from markupsafe import escape
import datetime
import requests


app = Flask(__name__)

global store
store = {'usuario': '', 'destinatario': '', 'recibidos': []}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        store['usuario'] = request.form['usuario']
        store['destinatario'] = request.form['destinatario']
        return redirect(url_for('messages'))
    return render_template('user.html')

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':
        message = request.form['message']
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        store['recibidos'].append((store['usuario'], store['destinatario'], message, timestamp))
        try:
            response = requests.post('http://localhost:5001/enviar', json={'usuario':store['usuario'],'destinatario':store['destinatario'],'message': message, 'timestamp': timestamp})
        except Exception as e:
            print(e)
    return render_template('index.html', store= store) 


@app.route('/enviar', methods=['POST'])
def enviar():
    message = request.json['message']
    usuario = request.json['usuario']
    destinatario = request.json['destinatario']
    timestamp = request.json['timestamp']
    store['recibidos'].append(( usuario, destinatario, message, timestamp))
    return 'OK', 200



if __name__ == '__main__':
    app.run(host='localhost', port=5001)