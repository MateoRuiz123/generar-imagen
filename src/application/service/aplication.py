from html2image import Html2Image
from src.infraestructure.repository.dao.ImagenesRepository import marcarGuiaProcesada, obtenerHtml, guardarPath
from src.infraestructure.SFTPrepository.adapter.adapter import connectSFTP
from src.infraestructure.repository.adapter.adapter import pool
from src.util.Envs import RUTA_IMAGENES
from os import remove
import moment
from route import RUTA
import threading
from src.scripts.SubProcess import MAIN as subProcess

hti = Html2Image(custom_flags=['--no-sandbox', '--headless', '--hide-scrollbars'])
hti.output_path='./src/files/'


def generarImagen(guia):
    try:
        db = pool.getconn()
        db.autocommit = True
        sftp = connectSFTP()
        date = moment.utcnow().timezone("America/Bogota").format('YYYYMMDD')
        rutaRemota = RUTA_IMAGENES+date
        nombreImagen = guia+'_imagen.jpg'
        rutaImagenLocal= './src/files/'+nombreImagen
        html = obtenerHtml(guia, db)
        hti.screenshot(html_str=html[0], save_as=guia+'_imagen.jpg', size=[(1024, 1200)])
        if sftp.exists(rutaRemota):
            sftp.put(localpath=rutaImagenLocal, remotepath=rutaRemota+'/'+nombreImagen)
        else:
            sftp.makedirs(rutaRemota)
            sftp.put(localpath=rutaImagenLocal, remotepath=rutaRemota+'/'+nombreImagen)
        marcarGuiaProcesada(guia, db)
        guardarPath(guia, 'imagenes_entregas/'+date+'/'+nombreImagen, db)
        remove(rutaImagenLocal)
        pool.putconn(db)
        sftp.close()
        return 'imagenes procesadas correctamente'
    except Exception as ex:
        return 'Error api generacion imagen: '+ str(ex)


def convertHtmlToImgMasivo(guias):
    proceso = threading.Thread(target=subProcess, args=(guias,))
    proceso.start()
    return 'OK'




