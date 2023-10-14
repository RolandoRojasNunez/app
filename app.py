from librerias import *

# Declarando nombre de la aplicación e inicializando, crear la aplicación Flask
app = Flask(__name__)
application = app

app.secret_key = '97110c78ae51a45afcb3380af008f90b23a5d1616bf19bc29098105da20fe'

app.config.from_object(Config)

# Creando mi Decorador para el Home
@app.route('/', methods=['GET', 'POST'])
def inicio():
    return render_template('public/index.html')

# Buscar proveedor


@app.route('/buscar-proveedor', methods=['GET', 'POST'])
def BuscarProveedor():
    if request.method == "POST":
        search = request.form['buscar']
        categoria = request.form['categoria']

        database = Database()
        cursor_pointer = database.connection.cursor(dictionary=True)

        query = "SELECT proveedores.proveedor_id, datos.nombre, datos.apellido, proveedores.rutempresa, proveedores.razonsocial, proveedores.nombrecomercial, proveedores.rubro, proveedores.descripcion, proveedores.logo, datos.web, datos.whatsapp, datos.facebook, datos.instagram FROM proveedores INNER JOIN datos ON proveedores.proveedor_id = datos.proveedor_id WHERE"

        if categoria:  # Si se seleccionó una categoría
            query += " proveedores.rubro = %s AND "

        query += " CONCAT(datos.nombre, datos.apellido, proveedores.rutempresa, proveedores.razonsocial, proveedores.nombrecomercial, proveedores.rubro, proveedores.descripcion, proveedores.logo) LIKE %s ORDER BY proveedores.proveedor_id DESC"

        search = search.replace(' ', '%')

        if categoria:  # Si se seleccionó una categoría
            cursor_pointer.execute(query + " LIMIT 0, 25", (categoria, f"%{search}%"))
        else:
            cursor_pointer.execute(query + " LIMIT 0, 25", (f"%{search}%",))

        resultadoBusqueda = cursor_pointer.fetchall()
        # Aleatorizar el orden de los resultados
        random.shuffle(resultadoBusqueda)

        cursor_pointer.close()
        database.connection.close()

        return render_template('public/resultadoBusqueda.html', miData=resultadoBusqueda, busqueda=search)
    return redirect(url_for('inicio'))


# App Login

login_manager_app = LoginManager(app)
csrf = CSRFProtect(app)


@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)


@app.route('/log')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # print(request.form['username'])
        # print(request.form['password'])
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('homelog'))

            else:
                flash("Contraseña invalida")
                return render_template('public/login.html')

        else:
            flash("Usuario no encontrado")
            return render_template('public/login.html')
    else:
        return render_template('public/login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home')
def homelog():
    tiene_registros_sin_proveedor = verificarRegistrosSinProveedor()
    return render_template('public/home.html', tiene_registros_sin_proveedor=tiene_registros_sin_proveedor)


@app.route('/protected')
@login_required
def protected():
    return "<h1>Debes estar logeado para acceder</h1>"


def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return "<h1>Página no encontrada</h1>", 404


# App Users
# Rutas de la aplicación users
@app.route('/users')
@login_required
def home():
    database = Database()
    cursor_pointer = database.connection.cursor()
    cursor_pointer.execute("SELECT * FROM users")
    myresult = cursor_pointer.fetchall()
    
    # Convertir los datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor_pointer.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor_pointer.close()
    
    # Verificar registros sin proveedor
    tiene_registros_sin_proveedor = verificarRegistrosSinProveedor()

    return render_template('public/users.html', data=insertObject, tiene_registros_sin_proveedor=tiene_registros_sin_proveedor)



# Ruta para guardar usuarios en la bd

@app.route('/user', methods=['POST'])
@login_required
def addUser():
    username = request.form['username']
    fullname = request.form['fullname']
    password = request.form['password']
    telefono = request.form['telefono']
    email = request.form['email']

    # Validar clave
    if not validar_clave(password):
        flash('La clave debe tener mínimo 8 caracteres, al menos una mayúscula, un número y un signo especial.')
        return redirect(url_for('home'))

    hashed_password = generate_password_hash(password)

    if username and fullname and hashed_password and telefono and email:
        database = Database()
        cursor_pointer = database.connection.cursor()
        sql = "INSERT INTO users (username, fullname, password, telefono, email) VALUES (%s, %s, %s, %s, %s)"
        data = (username, fullname, hashed_password, telefono, email)
        cursor_pointer.execute(sql, data)
        database.connection.commit()

    return redirect(url_for('home'))

def validar_clave(clave):
    # Verificar longitud mínima de 8 caracteres
    if len(clave) < 8:
        return False
    
    # Verificar si hay al menos una mayúscula
    if not re.search(r"[A-Z]", clave):
        return False
    
    # Verificar si hay al menos un número
    if not re.search(r"\d", clave):
        return False
    
    # Verificar si hay al menos un signo especial
    if not re.search(r"[!@#$%^&*()-_=+{}[\]|\\:;\"'<>/?]", clave):
        return False
    
    return True


@app.route('/delete/<string:id>')
@login_required
def delete(id):
    database = Database()
    cursor_pointer = database.connection.cursor()
    sql = "DELETE FROM users WHERE id=%s"
    data = (id,)
    cursor_pointer.execute(sql, data)
    database.connection.commit()
    return redirect(url_for('home'))


@app.route('/edit/<string:id>', methods=['POST'])
@login_required
def edit(id):
    username = request.form['username']
    fullname = request.form['fullname']
    password = request.form['password']
    telefono = request.form['telefono']
    email = request.form['email']

    hashed_password = generate_password_hash(password)

    if username and fullname and hashed_password and telefono and email:
        database = Database()
        cursor_pointer = database.connection.cursor()
        sql = "UPDATE users SET username = %s, fullname = %s, password = %s , telefono = %s , email = %s WHERE id = %s"
        data = (username, fullname, hashed_password, telefono, email, id)
        cursor_pointer.execute(sql, data)
        database.connection.commit()
    return redirect(url_for('home'))


# Rutas de la aplicación proveedores
@app.route('/proveedor')
@login_required
def homep():
    database = Database()
    cursor_pointer = database.connection.cursor()
    cursor_pointer.execute("SELECT p.*, d.nombre, d.apellido, d.instagram, d.facebook, d.whatsapp, d.web FROM proveedores p JOIN datos d ON p.proveedor_id = d.proveedor_id")
    myresult = cursor_pointer.fetchall()
    # Convertir los datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor_pointer.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor_pointer.close()

    # Verificar registros sin proveedor
    tiene_registros_sin_proveedor = verificarRegistrosSinProveedor()

    return render_template('public/proveedor.html', data=insertObject, tiene_registros_sin_proveedor=tiene_registros_sin_proveedor)


# Ruta para guardar proveedores en la bd
@app.route('/proveedor', methods=['GET', 'POST'])
@login_required
def addProveedor():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    rutempresa = request.form['rutempresa']
    razonsocial = request.form['razonsocial']
    nombrecomercial = request.form['nombrecomercial']
    rubro = request.form['rubro']
    descripcion = request.form['descripcion']
    Instagram = request.form['Instagram']
    Facebook = request.form['Facebook']
    Whatsapp = request.form['Whatsapp']
    web = request.form['web']

    # Verificar si se envió el archivo "logo"
    logo_filename = None
    if 'logo' in request.files:
        logo = request.files['logo']
        if logo and allowed_file(logo.filename):
            filename = secure_filename(logo.filename)
            #logo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            logo.save(os.path.join(app.config['PUBLIC_PATH'], filename))
            logo_filename = filename
        else:
            # Manejar el caso en que no se envíe un archivo válido
            return 'Error al subir el archivo'
    else:
        # Manejar el caso en que no se envíe el archivo "logo"
        logo = None

    if nombre and apellido and rutempresa and razonsocial and nombrecomercial and rubro and descripcion and Instagram and Facebook and Whatsapp and web:
        database = Database()
        cursor_pointer = database.connection.cursor()

        # Insertar datos en la tabla "proveedores"
        sql_proveedores = "INSERT INTO proveedores (rutempresa, razonsocial, nombrecomercial, rubro, descripcion, logo, proveedor_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        
        # Generar proveedor_id encriptado
        proveedor_id = hashlib.sha256(str.encode(rutempresa + nombrecomercial)).hexdigest()
        
        data_proveedores = (rutempresa, razonsocial, nombrecomercial, rubro, descripcion, logo_filename, proveedor_id)
        cursor_pointer.execute(sql_proveedores, data_proveedores)
        database.connection.commit()

        # Insertar datos en la tabla "datos" relacionados al proveedor por su proveedor_id encriptado
        sql_datos = "INSERT INTO datos (proveedor_id, nombre, apellido, instagram, facebook, whatsapp, web) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        data_datos = (proveedor_id, nombre, apellido, Instagram, Facebook, Whatsapp, web)
        cursor_pointer.execute(sql_datos, data_datos)
        database.connection.commit()

    return redirect(url_for('homep'))


@app.route('/deletep/<string:proveedor_id>')
@login_required
def deletep(proveedor_id):
    database = Database()
    cursor_pointer = database.connection.cursor()

    # Eliminar registro de la tabla "proveedores"
    sql_proveedores = "DELETE FROM proveedores WHERE proveedor_id=%s"
    data_proveedores = (proveedor_id,)
    cursor_pointer.execute(sql_proveedores, data_proveedores)

    # Eliminar registro de la tabla "datos"
    sql_datos = "DELETE FROM datos WHERE proveedor_id=%s"
    data_datos = (proveedor_id,)
    cursor_pointer.execute(sql_datos, data_datos)
        
    database.connection.commit()
    flash('Registro eliminado exitosamente', 'success')
    return redirect(url_for('homep'))


@app.route('/editp/<string:proveedor_id>', methods=['POST'])
@login_required
def editp(proveedor_id):
    # Obtener los datos del formulario
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    rutempresa = request.form['rutempresa']
    dv = request.form['dv']
    razonsocial = request.form['razonsocial']
    nombrecomercial = request.form['nombrecomercial']
    rubro = request.form['rubro']
    descripcion = request.form['descripcion']
    Instagram = request.form['Instagram']
    Facebook = request.form['Facebook']
    Whatsapp = request.form['Whatsapp']
    web = request.form['web']

    # Verificar si se envió un archivo de logo nuevo
    logo_filename = None
    if 'logo' in request.files:
        logo = request.files['logo']
        if logo and allowed_file(logo.filename):
            # Guardar el nuevo archivo de logo
            filename = secure_filename(logo.filename)
            #logo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            logo.save(os.path.join(app.config['PUBLIC_PATH'], filename))
            logo_filename = filename

    # Actualizar los datos en la base de datos
    database = Database()
    cursor_pointer = database.connection.cursor()
    sql_proveedores = "UPDATE proveedores SET rutempresa = %s, dv = %s, razonsocial = %s, nombrecomercial = %s, rubro = %s, descripcion = %s"
    data_proveedores = (rutempresa, dv, razonsocial, nombrecomercial, rubro, descripcion)

    # Actualizar el campo 'logo' solo si se adjunta un nuevo archivo
    if logo_filename:
        sql_proveedores += ", logo = %s"
        data_proveedores += (logo_filename,)

    sql_proveedores += " WHERE proveedor_id = %s"
    data_proveedores += (proveedor_id,)

    cursor_pointer.execute(sql_proveedores, data_proveedores)

    sql_datos = "UPDATE datos SET nombre = %s, apellido = %s, instagram = %s, facebook = %s, whatsapp = %s, web = %s WHERE proveedor_id = %s"
    data_datos = (nombre, apellido, Instagram, Facebook, Whatsapp, web, proveedor_id)
    cursor_pointer.execute(sql_datos, data_datos)

    database.connection.commit()

    return redirect(url_for('homep'))


# Redireccionando cuando la página no existe
@app.errorhandler(404)
def not_found(error):
    return redirect(url_for('inicio'))


# Registro de Proveedores por parte del usuario

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    nombrer = request.form.get('nombreregistro')
    apellidor = request.form.get('apellidoregistro')
    rutempresar = request.form.get('rutempresaregistro')
    dvr = request.form.get('dvregistro')
    razonsocialr = request.form.get('razonsocialregistro')
    nombrecomercialr = request.form.get('nombrecomercialregistro')
    rubror = request.form.get('rubroregistro')
    descripcionr = request.form.get('descripcionregistro')
    instagramr = request.form.get('Instagramregistro')
    facebookr = request.form.get('Facebookregistro')
    whatsappr = request.form.get('Whatsappregistro')
    webr = request.form.get('webregistro')

    # Verificar si se envió el archivo "logoregistro"
    logoregistro_filename = ''
    if 'logoregistro' in request.files:
        logoregistro = request.files['logoregistro']
        if logoregistro and allowed_file(logoregistro.filename):
            filename = secure_filename(logoregistro.filename)
            #logoregistro.save(os.path.join(app.config['UPLOAD_FOLDER_REGISTRO'], filename))
            logoregistro.save(os.path.join(app.config['REGISTRO_PATH'], filename))
            logoregistro_filename = filename
        else:
            # Manejar el caso en que no se envíe un archivo válido
            return 'Error al subir el archivo'
    else:
        # Manejar el caso en que no se envíe el archivo "logoregistro"
        logoregistro_filename = None

    if nombrer and apellidor and rutempresar and dvr and razonsocialr and nombrecomercialr and rubror and descripcionr and instagramr and facebookr and whatsappr and webr:
        # Verificar si el RUT ya está registrado
        if verificarRutExistente(rutempresar):
            flash('El RUT ya está registrado', 'error')
            return redirect(url_for('registro'))  # Redirecciona al formulario nuevamente
        else:
            # Continuar con el proceso de registro
            database = Database()
            cursor_pointer = database.connection.cursor()

            # Generar proveedor_id encriptado
            proveedorregistro_id = hashlib.sha256(str.encode(rutempresar + nombrecomercialr)).hexdigest()

            # Insertar datos en la tabla "registro"
            sql_proveedores = "INSERT INTO registro (proveedorregistro_id, rutempresa, dv, razonsocial, nombrecomercial, rubro, descripcion, logo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            data_proveedores = (proveedorregistro_id, rutempresar, dvr, razonsocialr, nombrecomercialr, rubror, descripcionr, logoregistro_filename)
            cursor_pointer.execute(sql_proveedores, data_proveedores)
            database.connection.commit()

            # Insertar datos en la tabla "datosregistro" relacionados al proveedor por su proveedorregistro_id encriptado
            sql_datos = "INSERT INTO datosregistro (proveedorregistro_id, nombrer, apellidor, instagramr, facebookr, whatsappr, webr) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            data_datos = (proveedorregistro_id, nombrer, apellidor, instagramr, facebookr, whatsappr, webr)
            cursor_pointer.execute(sql_datos, data_datos)
            database.connection.commit()

            if cursor_pointer.rowcount > 0:
                # Se agregó una fila
                time.sleep(1)  # Esperar 1 segundo
                solicitud_emprendedores.append(razonsocialr) #Registrar en la variable, los emprendedores que esten esperando validacion
                print(solicitud_emprendedores)
                return redirect(url_for('registroexitoso'))
                
            else:
                # No se agregó ninguna fila
                return redirect(url_for('registro'))
        
    else:
        return render_template('public/registro.html')


def verificarRutExistente(rut):
    database = Database()
    cursor = database.connection.cursor()

    # Verificar si el RUT existe en la tabla "registro"
    sql = "SELECT COUNT(*) FROM registro WHERE rutempresa = %s"
    cursor.execute(sql, (rut,))
    count = cursor.fetchone()[0]

    if count > 0:
        # El RUT ya está registrado
        return True
    else:
        # El RUT no está registrado
        return False


# Ruta para la página de registro exitoso

@app.route('/public/registroexitoso')
def registroexitoso():
    return render_template('public/registroexitoso.html')

@app.route('/revisionsolicitudes')
@login_required
def revisionsolicitudes():
    database = Database()
    cursor_pointer = database.connection.cursor()
    cursor_pointer.execute("SELECT registro.proveedorregistro_id, datosregistro.nombrer, datosregistro.apellidor, registro.rutempresa, registro.dv, registro.razonsocial, registro.nombrecomercial, registro.rubro,registro.descripcion, registro.logo, datosregistro.webr, datosregistro.whatsappr, datosregistro.facebookr, datosregistro.instagramr FROM registro INNER JOIN datosregistro ON registro.proveedorregistro_id = datosregistro.proveedorregistro_id")
    myresult = cursor_pointer.fetchall()
    # Convertir los datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor_pointer.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor_pointer.close()

    # Obtener el valor de rutempresa desde el HTML (suponiendo que es parte de la lista 'insertObject')

    for data in insertObject:
        rutempresa = str(data['rutempresa'])
        # Verificar si el registro existe en la base de datos
        # registro = verificar_registro(rutempresa)
        # Realizar las operaciones adicionales con los datos encontrados
        # Aquí puedes realizar las consultas o acciones adicionales que desees para cada dato encontrado en la tabla "registro"
        data['registrado'] = verificar_registro(rutempresa)

    # Verificar registros sin proveedor
    tiene_registros_sin_proveedor = verificarRegistrosSinProveedor()

    return render_template('public/revisiondesolicitudes.html', data=insertObject, tiene_registros_sin_proveedor=tiene_registros_sin_proveedor)


def verificar_registro(rutempresa):
    database = Database()
    cursor_pointer = database.connection.cursor()
    # Consulta SQL para verificar si el registro existe
    query = "SELECT COUNT(*) as id FROM proveedores WHERE rutempresa = %s"
    cursor_pointer.execute(query, (rutempresa,))
    count = cursor_pointer.fetchone()[0]
    database.connection.close()
    if count > 0:
        return True
    else:
        return False


@app.route('/deletes/<string:proveedorregistro_id>')
@login_required
def deleter(proveedorregistro_id):
    database = Database()
    cursor_pointer = database.connection.cursor()

    # Eliminar registro de la tabla "registro"
    sql_registro = "DELETE FROM registro WHERE proveedorregistro_id=%s"
    data_registro = (proveedorregistro_id,)
    cursor_pointer.execute(sql_registro, data_registro)

    # Eliminar registro de la tabla "datosregistro"
    sql_datosregistro = "DELETE FROM datosregistro WHERE proveedorregistro_id=%s"
    data_datosregistro = (proveedorregistro_id,)
    cursor_pointer.execute(sql_datosregistro, data_datosregistro)

    database.connection.commit()
    return redirect(url_for('revisionsolicitudes'))


@app.route('/editr/<string:proveedorregistro_id>', methods=['POST'])
@login_required
def editr(proveedorregistro_id):
    # Obtener los datos del formulario
    nombreregistro = request.form['nombreregistro']
    apellidosregistro = request.form['apellidosregistro']
    rutempresaregistro = request.form['rutempresaregistro']
    dvregistro = request.form['dvregistro']
    razonsocialregistro = request.form['razonsocialregistro']
    nombrecomercialregistro = request.form['nombrecomercialregistro']
    rubroregistro = request.form['rubroregistro']
    descripcionregistro = request.form['descripcionregistro']
    Instagramregistro = request.form['Instagramregistro']
    Facebookregistro = request.form['Facebookregistro']
    Whatsappregistro = request.form['Whatsappregistro']
    webregistro = request.form['webregistro']

    # Verificar si se envió un archivo de logo nuevo
    logoregistro_filename = None

    # Verificar si se envió un archivo de logo nuevo
    if 'logo' in request.files:
        logoregistro = request.files['logo']
        if logoregistro and allowed_file(logoregistro.filename):
            # Guardar el nuevo archivo de logo
            filename = secure_filename(logoregistro.filename)
            #logoregistro.save(os.path.join(app.config['UPLOAD_FOLDER_REGISTRO'], filename))
            logoregistro.save(os.path.join(app.config['REGISTRO_PATH'], filename))
            logoregistro_filename = filename

    # Actualizar los datos en la base de datos
    database = Database()
    cursor_pointer = database.connection.cursor()

    sql_proveedores = "UPDATE registro SET rutempresa = %s, dv = %s, razonsocial = %s, nombrecomercial = %s, rubro = %s, descripcion = %s"
    data_proveedores = (rutempresaregistro, dvregistro, razonsocialregistro, nombrecomercialregistro, rubroregistro, descripcionregistro)
    if logoregistro_filename:
        sql_proveedores += ", logo = %s"
        data_proveedores += (logoregistro_filename,)
    sql_proveedores += " WHERE proveedorregistro_id = %s"
    data_proveedores += (proveedorregistro_id,)
    cursor_pointer.execute(sql_proveedores, data_proveedores)

    sql_datos = "UPDATE datosregistro SET nombrer = %s, apellidor = %s, instagramr = %s, facebookr = %s, whatsappr = %s, webr = %s WHERE proveedorregistro_id = %s"
    data_datos = (nombreregistro, apellidosregistro, Instagramregistro, Facebookregistro, Whatsappregistro, webregistro, proveedorregistro_id)
    cursor_pointer.execute(sql_datos, data_datos)

    database.connection.commit()

    return redirect(url_for('revisionsolicitudes'))



@app.route('/migrate', methods=['POST'])
@csrf.exempt
def migrate_to_portal():
    try:
        print(request.get_json())
        data = json.loads(request.data)
        selected_ids = data['id']  # Cambio el nombre de la variable a selected_ids

        database = Database()
        cursor_pointer = database.connection.cursor()

        for selected_id in selected_ids:  # Cambio el nombre de la variable a selected_id
            sql = "SELECT registro.proveedorregistro_id, datosregistro.nombrer, datosregistro.apellidor, registro.rutempresa, registro.dv, registro.razonsocial, registro.nombrecomercial, registro.rubro,registro.descripcion, registro.logo, datosregistro.webr, datosregistro.whatsappr, datosregistro.facebookr, datosregistro.instagramr FROM registro INNER JOIN datosregistro ON registro.proveedorregistro_id = datosregistro.proveedorregistro_id WHERE registro.proveedorregistro_id = %s"
            data = (selected_id,)
            cursor_pointer.execute(sql, data)
            myresult = cursor_pointer.fetchall()

            # Convertir los datos a diccionario
            resultadoregistro = []
            columnNames = [column[0] for column in cursor_pointer.description]
            for record in myresult:
                resultadoregistro.append(dict(zip(columnNames, record)))

            

            for seleccionado in resultadoregistro:
                nombre = seleccionado['nombrer']
                apellido = seleccionado['apellidor']
                rutempresa = seleccionado['rutempresa']
                dv = seleccionado['dv']
                razonsocial = seleccionado['razonsocial']
                nombrecomercial = seleccionado['nombrecomercial']
                rubro = seleccionado['rubro']
                descripcion = seleccionado['descripcion']
                Instagram = seleccionado['instagramr']
                Facebook = seleccionado['facebookr']
                Whatsapp = seleccionado['whatsappr']
                web = seleccionado['webr']
                logo = seleccionado['logo']

                # Obtener la ubicación del directorio del archivo "logo"
                #logo_directory = app.config["UPLOAD_FOLDER_REGISTRO"]
                logo_directory = app.config['REGISTRO_PATH']


                # Verificar si se envió el archivo "logo"
                logo_filename = seleccionado['logo']

                #logoyruta = (logo_directory + "\\" + logo_filename)
                logoyruta =  os.path.join(app.config['REGISTRO_PATH'], logo_filename)

                if logo_filename:
                    if os.path.exists(logoyruta):
                        logo_ruta_archivo = os.path.join(logo_directory, logo_filename)
                        #nueva_carpeta_destino = app.config["UPLOAD_FOLDER"]
                        nueva_carpeta_destino = app.config['PUBLIC_PATH']
                        nuevo_nombre_archivo = rutempresa + "_" + nombrecomercial + os.path.splitext(logo_filename)[1]
                        nuevo_ruta_archivo = os.path.join(nueva_carpeta_destino, nuevo_nombre_archivo)
                        shutil.copy2(logo_ruta_archivo, nuevo_ruta_archivo)
                        logo_nuevo = nuevo_nombre_archivo
                        
                if nombre and apellido and rutempresa and dv and razonsocial and nombrecomercial and rubro and descripcion and Instagram and Facebook and Whatsapp and web:
                    database = Database()
                    cursor_pointer = database.connection.cursor()

                    # Insertar datos en la tabla "proveedores"
                    sql_proveedores = "INSERT INTO proveedores (proveedor_id, rutempresa, dv, razonsocial, nombrecomercial, rubro, descripcion, logo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    
                    # Generar proveedor_id encriptado
                    proveedor_id = hashlib.sha256(str.encode(rutempresa + nombrecomercial)).hexdigest()
                    
                    data_proveedores = (proveedor_id, rutempresa, dv, razonsocial, nombrecomercial, rubro, descripcion, logo_nuevo)
                    cursor_pointer.execute(sql_proveedores, data_proveedores)
                    database.connection.commit()

                    # Insertar datos en la tabla "datos" relacionados al proveedor por su proveedor_id encriptado
                    sql_datos = "INSERT INTO datos (proveedor_id, nombre, apellido, instagram, facebook, whatsapp, web) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    data_datos = (proveedor_id, nombre, apellido, Instagram, Facebook, Whatsapp, web)
                    cursor_pointer.execute(sql_datos, data_datos)
                    database.connection.commit()

                    whatsapp.sendTemplate(Whatsapp, "welcome", nombrecomercial)    
                    

        cursor_pointer.close()

        return jsonify({'message': 'Solicitud procesada exitosamente'})

    except Exception as e:
        # Captura cualquier excepción y envía una respuesta de error
        error_message = 'Ha ocurrido un error: {}'.format(str(e))
        return jsonify({'error': error_message}), 500



def allowed_file(logoregistro_filename):
    allowed_extensions = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    return '.' in logoregistro_filename and logoregistro_filename.rsplit('.', 1)[1].lower() in allowed_extensions

allowed_extensions = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


@app.errorhandler(400)
def handle_bad_request(e):
    return 'Bad request: {}'.format(e),400



if __name__ == "__main__":
    app.run(debug=True, port=8000)
    #app.config.from_object(config['development'])
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    csrf.init_app(app)