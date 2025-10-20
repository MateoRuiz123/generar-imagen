from html2image import Html2Image
from src.infraestructure.repository.dao.ImagenesRepository import marcarGuiaProcesada, obtenerHtml, guardarPath
from src.infraestructure.SFTPrepository.adapter.adapter import connectSFTP
from src.util.Envs import RUTA_IMAGENES
from os import remove, makedirs, chmod
from os.path import exists
from route import RUTA
import moment
from src.infraestructure.repository.adapter.adapter import pool
import time
import traceback

# Crear directorio si no existe
output_dir = './src/files/'
if not exists(output_dir):
    makedirs(output_dir, mode=0o777, exist_ok=True)
else:
    chmod(output_dir, 0o777)

hti = Html2Image(custom_flags=['--no-sandbox', '--headless', '--hide-scrollbars', '--disable-dbus'])
hti.output_path = output_dir

def ejecutarProcesos(guias):
    db = None
    sftp = None

    try:
        db = pool.getconn()
        db.autocommit = True
        sftp = connectSFTP()
        date = moment.utcnow().timezone("America/Bogota").format('YYYYMMDD')
        rutaRemota = RUTA_IMAGENES + date
        print(rutaRemota + '--------------------------> remote')

        for i in guias:
            rutaImagenLocal = None
            try:
                nombreImagen = i + '_imagen.jpg'
                rutaImagenLocal = output_dir + nombreImagen

                html = obtenerHtml(i, db)
                hti.screenshot(html_str=html[0], save_as=nombreImagen, size=[(1024, 1200)])

                # Dar permisos al archivo
                if exists(rutaImagenLocal):
                    chmod(rutaImagenLocal, 0o666)

                if not sftp.exists(rutaRemota):
                    sftp.makedirs(rutaRemota)

                sftp.put(localpath=rutaImagenLocal, remotepath=rutaRemota + '/' + nombreImagen)
                marcarGuiaProcesada(i, db)
                guardarPath(i, 'imagenes_entregas/' + date + '/' + nombreImagen, db)
                remove(rutaImagenLocal)

            except Exception as ex_guia:
                print(f"❌ Error procesando guía {i}: {str(ex_guia)}\n{traceback.format_exc()}")
                # Intentar eliminar archivo si quedó
                if rutaImagenLocal and exists(rutaImagenLocal):
                    try:
                        remove(rutaImagenLocal)
                    except:
                        pass

        return 'imagenes procesadas correctamente'

    except Exception as ex:
        error_msg = f'Error api generacion imagen: {str(ex)}\n{traceback.format_exc()}'
        print(error_msg)
        return error_msg

    finally:
        if db:
            pool.putconn(db)
        if sftp:
            sftp.close()

def MAIN(guias):
    start = time.time()
    resultado = ejecutarProcesos(guias)
    print("Ejecucion de subproceso exitosa - tiempo ejecucion: " + str(time.time() - start))
    return resultado
