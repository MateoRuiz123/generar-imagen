from flask import Flask, request
from src.application.service.aplication import convertHtmlToImgMasivo, generarImagen
from src.config.config import config
from src.util.PubDataDecode import decode
import traceback

app = Flask(__name__)
from route import RUTA
prefix = '/cm-generar-imagen-guia'

@app.route(prefix+'/generar-imagen-guia', methods=['POST'])
def index():
    try:
        data = request.get_json()
        jsonData = decode(data)
        resultado = generarImagen(jsonData['codigo_remision'])
        print(f"✅ Resultado: {resultado}")
        return resultado
    except Exception as ex:
        error_completo = f'Error api generacion imagen: {str(ex)}\n{traceback.format_exc()}'
        print(f"❌ ERROR COMPLETO:\n{error_completo}")
        return error_completo, 500

@app.route(prefix+'/generar-imagen-masivo', methods=['POST'])
def masivo():
    try:
        data = request.get_json()
        jsonData = decode(data)
        return convertHtmlToImgMasivo(jsonData['guias'])
    except Exception as ex:
        error_completo = f'Error api generacion imagen masivo: {str(ex)}\n{traceback.format_exc()}'
        print(f"❌ ERROR COMPLETO:\n{error_completo}")
        return error_completo, 500

@app.route(prefix+'/', methods=['GET'])
def ping():
    try:
        return 'OK'
    except Exception as ex:
        return f'Error: {str(ex)}', 500

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()
