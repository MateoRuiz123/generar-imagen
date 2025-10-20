from flask import Flask, request
from src.application.service.aplication import  convertHtmlToImgMasivo, generarImagen
from src.config.config import config
from src.util.PubDataDecode import decode

app = Flask(__name__)
from route import RUTA
prefix = '/cm-generar-imagen-guia'

@app.route(prefix+'/generar-imagen-guia', methods = ['POST'])
def index():
    try:
        data = request.get_json()
        jsonData = decode(data)
        return generarImagen(jsonData['codigo_remision'])
    except Exception as ex:
        return 'Error api generacion imagen'

@app.route(prefix+'/generar-imagen-masivo', methods = ['POST'])
def masivo():
    try:
        data = request.get_json()
        jsonData = decode(data)
        return convertHtmlToImgMasivo(jsonData['guias'])
    except Exception as ex:
        return 'Error api generacion imagen'
        
@app.route(prefix+'/', methods = ['GET'])
def ping():
    try:
        return 'OK'
    except Exception as ex:
        return 'Error api generacion imagen'

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()
