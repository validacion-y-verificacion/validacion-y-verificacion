from flask import Flask, flash, render_template, request, redirect, url_for
from markupsafe import escape
import datetime
import requests
import logging


logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.INFO) 
logger=logging.getLogger()

app = Flask(__name__)

global store
store = {'usuario': '', 'destinatario': '', 'recibidos': []}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            store['usuario'] = request.form['usuario']
            logger.info('Usuario ingresado')
            store['destinatario'] = request.form['destinatario']
            logger.info('Destinatario ingresado')
        except Exception as e:
            logger.warning(e)
            logger.warning('No se logró ingresar usuario o destinatario')
        return redirect(url_for('messages'))
    return render_template('user.html')

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':
        message = request.form['message']
        if len(message) < 1:
            logger.warning('Mensaje vacío no permitido')
        elif len(message) > 350:
            logger.warning('Mensaje excede el límite de caracteres permitidos (350)')
        else:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            store['recibidos'].append((store['usuario'], store['destinatario'], message, timestamp))
            try:
                response = requests.post('http://127.0.0.1:5001/enviar', json={'usuario':store['usuario'],'destinatario':store['destinatario'],'message': message, 'timestamp': timestamp})
                logger.info('Mensaje enviado')
            except Exception as e:
                logger.warning(e)
                logger.warning('No se logró enviar mensaje')
    return render_template('index.html', store= store) 


@app.route('/enviar', methods=['POST'])
def enviar():
    logger.info('Mensaje recibido')
    message = request.json['message']
    usuario = request.json['usuario']
    destinatario = request.json['destinatario']
    timestamp = request.json['timestamp']
    store['recibidos'].append(( usuario, destinatario, message, timestamp))
    return 'OK', 200



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)