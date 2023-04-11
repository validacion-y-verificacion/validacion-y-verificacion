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

        #Obtiene usuario y destinatario
        try:
            store['usuario'] = request.form['usuario']
            store['destinatario'] = request.form['destinatario']
        except Exception as e:
            logger.warning(e)
            logger.warning('No se logró ingresar usuario o destinatario')
            return render_template('user.html')

        # Verifica que no sean vacíos
        if store['usuario'] == '' or store['destinatario'] == '':
            logger.warning('Usuario o destinatario vacío')
            return render_template('user.html')
        
        # Verifica que exista el destinatario    
        try:
            response = requests.post('http://127.0.0.1:5001/check')
            if response.status_code == 200:
                logger.info('Handshake')
                if response.text != store['destinatario']:
                    logger.warning('No se encontró destinatario')
                    return render_template('user.html') 
                logger.info('Usuario ingresado')
                logger.info('Destinatario ingresado')
        except Exception as e:
            logger.warning(e)
            logger.warning('No se logró enviar handshake')
            return render_template('user.html')
        
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

            # Revisa que exista el destinatario
            try:
                response = requests.post('http://127.0.0.1:5001/check')
                if response.status_code == 200:
                    logger.info('Handshake')
                    if response.text != store['destinatario']:
                        logger.warning('No se encontró destinatario')
                        return render_template('user.html')
            except Exception as e:
                logger.warning(e)
                logger.warning('No se logró enviar handshake')
                return render_template('user.html')

            # Se envia el mensaje
            try:
                response = requests.post('http://127.0.0.1:5001/enviar', json={'usuario':store['usuario'],'destinatario':store['destinatario'],'message': message, 'timestamp': timestamp})
                if response.status_code == 200:
                    store['recibidos'].append((store['usuario'], store['destinatario'], message, timestamp))
                    logger.info('Mensaje enviado')
                else:
                    logger.warning('No se logró enviar mensaje')
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
    return destinatario


@app.route('/check', methods=['POST'])
def check_usuario():
    logger.info('Handshake recibido')
    return store['usuario']



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)