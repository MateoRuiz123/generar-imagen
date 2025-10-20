def marcarGuiaProcesada(guia, db):
    querySession = "SELECT func_registrar_sesion('suite_logistica_user','UPDATE');"
    query = "UPDATE estado_imagenes SET estado_sincronizacion = true, estado_proceso ='terminado' WHERE guia ='" + guia+"'"
    cursor = db.cursor()
    cursor.execute(querySession)
    cursor.execute(query)
    cursor.close()
    
def obtenerHtml(guia, db):
    query = "SELECT html FROM estado_imagenes WHERE guia ='" +guia+"'"
    cursor = db.cursor()
    cursor.execute(query)
    response = cursor.fetchone()
    cursor.close()
    return response

def guardarPath(guia, path, db):
    querySession = "SELECT func_registrar_sesion('suite_logistica_user','INSERT');"
    queryImagen = "SELECT codigo_remision FROM public.imagenes WHERE codigo_remision = '"+guia+"'"
    cursor = db.cursor()
    cursor.execute(queryImagen)
    response = cursor.fetchone()
    cursor.execute(querySession)
    if response:
        query = "UPDATE imagenes SET path = '"+path+"', last_date = current_date, last_time = current_time WHERE codigo_remision = '"+guia+"'"
        cursor.execute(query)
    else:
        query = "INSERT INTO public.imagenes (codigo_remision, path, last_dbuser, last_app, last_date, last_time, last_ip_address) VALUES ('"+guia+"', '"+path+"','suite_logistica_user', 'SUIT', current_date, current_time, '192.168.222.4')"
        cursor.execute(query)
    cursor.close()
