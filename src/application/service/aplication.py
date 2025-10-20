from html2image import Html2Image
from src.infraestructure.repository.dao.ImagenesRepository import marcarGuiaProcesada, obtenerHtml, guardarPath
from src.infraestructure.SFTPrepository.adapter.adapter import connectSFTP
from src.infraestructure.repository.adapter.adapter import pool
from src.util.Envs import RUTA_IMAGENES
from os import remove, makedirs, chmod
from os.path import exists
import moment
from route import RUTA
import threading
from src.scripts.SubProcess import MAIN as subProcess
import traceback

# Crear directorio si no existe
output_dir = './src/files/'
if not exists(output_dir):
    makedirs(output_dir, mode=0o777, exist_ok=True)
else:
    # Asegurar permisos si ya existe
    chmod(output_dir, 0o777)

hti = Html2Image(custom_flags=['--no-sandbox', '--headless', '--hide-scrollbars', '--disable-dbus'])
hti.output_path = output_dir


def generarImagen(guia):
    db = None
    sftp = None
    rutaImagenLocal = None

    try:
        print(f"🔹 Iniciando generación de imagen para guía: {guia}")

        db = pool.getconn()
        db.autocommit = True

        print(f"🔹 Conectando SFTP...")
        sftp = connectSFTP()

        date = moment.utcnow().timezone("America/Bogota").format('YYYYMMDD')
        rutaRemota = RUTA_IMAGENES + date
        nombreImagen = guia + '_imagen.jpg'
        rutaImagenLocal = output_dir + nombreImagen

        print(f"🔹 Obteniendo HTML de la base de datos...")
        html = obtenerHtml(guia, db)

        print(f"🔹 Generando screenshot en: {rutaImagenLocal}")
        hti.screenshot(html_str=html[0], save_as=nombreImagen, size=[(1024, 1200)])

        # Verificar que la imagen se creó
        if not exists(rutaImagenLocal):
            raise Exception(f"La imagen no se generó en {rutaImagenLocal}")

        print(f"✅ Imagen generada: {rutaImagenLocal}")

        # Dar permisos al archivo generado
        chmod(rutaImagenLocal, 0o666)

        print(f"🔹 Verificando ruta remota SFTP: {rutaRemota}")
        if not sftp.exists(rutaRemota):
            print(f"🔹 Creando directorio remoto: {rutaRemota}")
            sftp.makedirs(rutaRemota)

        print(f"🔹 Subiendo imagen por SFTP...")
        sftp.put(localpath=rutaImagenLocal, remotepath=rutaRemota + '/' + nombreImagen)
        print(f"✅ Imagen subida exitosamente")

        print(f"🔹 Marcando guía como procesada...")
        marcarGuiaProcesada(guia, db)

        print(f"🔹 Guardando path en base de datos...")
        guardarPath(guia, 'imagenes_entregas/' + date + '/' + nombreImagen, db)

        print(f"🔹 Eliminando archivo local...")
        remove(rutaImagenLocal)
        print(f"✅ Archivo eliminado")

        return 'imagenes procesadas correctamente'

    except Exception as ex:
        error_detallado = f"Error en paso específico: {str(ex)}\n{traceback.format_exc()}"
        print(f"❌ ERROR: {error_detallado}")

        # Intentar limpiar archivo local si existe
        if rutaImagenLocal and exists(rutaImagenLocal):
            try:
                remove(rutaImagenLocal)
                print(f"🧹 Archivo temporal eliminado después del error")
            except Exception as cleanup_ex:
                print(f"⚠️ No se pudo eliminar archivo temporal: {cleanup_ex}")

        return f'Error api generacion imagen: {str(ex)}'

    finally:
        # Cerrar conexiones
        if db:
            try:
                pool.putconn(db)
            except Exception as e:
                print(f"⚠️ Error cerrando conexión DB: {e}")

        if sftp:
            try:
                sftp.close()
            except Exception as e:
                print(f"⚠️ Error cerrando conexión SFTP: {e}")


def convertHtmlToImgMasivo(guias):
    proceso = threading.Thread(target=subProcess, args=(guias,))
    proceso.start()
    return 'OK'
