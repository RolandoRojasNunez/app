from confiDB import Database

def verificarRegistrosSinProveedor():
    database = Database()
    cursor = database.connection.cursor()

    # Obtener los RUTs de la tabla "registro"
    sql_registro = "SELECT DISTINCT rutempresa FROM registro"
    cursor.execute(sql_registro)
    ruts_registro = [row[0] for row in cursor.fetchall()]

    count_ruts_sin_proveedor = 0
    count_ruts_pendientes = 0

    # Verificar cada RUT en la tabla "proveedores"
    for rut in ruts_registro:
        sql_proveedores = "SELECT COUNT(*) FROM proveedores WHERE rutempresa = %s"
        cursor.execute(sql_proveedores, (rut,))
        count_proveedores = cursor.fetchone()[0]

        if count_proveedores == 0:
            count_ruts_sin_proveedor += 1
        else:
            count_ruts_pendientes += 1

    return count_ruts_sin_proveedor