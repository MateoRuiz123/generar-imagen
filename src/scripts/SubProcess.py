from html2image import Html2Image
from src.infraestructure.repository.dao.ImagenesRepository import marcarGuiaProcesada, obtenerHtml, guardarPath
from src.infraestructure.SFTPrepository.adapter.adapter import connectSFTP
from src.util.Envs import RUTA_IMAGENES
from os import remove
from route import RUTA
import moment
from src.infraestructure.repository.adapter.adapter import pool
from src.infraestructure.SFTPrepository.adapter.adapter import connectSFTP
import time
hti = Html2Image(custom_flags=['--no-sandbox', '--headless', '--hide-scrollbars'])
hti.output_path='./src/files/'

def ejecutarProcesos(guias):
    try:
        db = pool.getconn()
        db.autocommit = True
        sftp = connectSFTP()
        date = moment.utcnow().timezone("America/Bogota").format('YYYYMMDD')
        rutaRemota = RUTA_IMAGENES+date
        print(rutaRemota +'--------------------------> remote')
        for i in guias:
            nombreImagen = i+'_imagen.jpg'
            rutaImagenLocal= './src/files/'+nombreImagen
            html = obtenerHtml(i, db)
            hti.screenshot(html_str=html[0], save_as=i+'_imagen.jpg', size=[(1024, 1200)])
            if sftp.exists(rutaRemota):
                sftp.put(localpath=rutaImagenLocal, remotepath=rutaRemota+'/'+nombreImagen)
            else:
                sftp.makedirs(rutaRemota)
                sftp.put(localpath=rutaImagenLocal, remotepath=rutaRemota+'/'+nombreImagen)
            marcarGuiaProcesada(i, db)
            guardarPath(i, 'imagenes_entregas/'+date+'/'+nombreImagen, db)
            remove(rutaImagenLocal)
        pool.putconn(db)
        sftp.close()
        return 'imagenes procesadas correctamente'
    except Exception as ex:
        return 'Error api generacion imagen: '+ str(ex)

def MAIN(guias):
    start = time.time()
    resultado = ejecutarProcesos(guias)
    print ("Ejecucion de subproceso exitosa - tiempo ejecucion: "+str(time.time() - start))
    return(resultado)
