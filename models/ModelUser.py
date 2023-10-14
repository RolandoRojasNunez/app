from .entities.User import User
from confiDB import Database

class ModelUser():

    @classmethod
    def login(self, db, user):
        try:
            database = Database()
            cursor_pointer = database.connection.cursor()
            sql = """SELECT id, username, password, fullname FROM users WHERE username = '{}'""".format(user.username)
            cursor_pointer.execute(sql)
            row = cursor_pointer.fetchone()
            if row != None:
                user = User(row[0], row[1], User.check_password(row[2], user.password), row[3])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(self, db, id):
        try:
            database = Database()
            cursor_pointer = database.connection.cursor()
            sql = "SELECT id, username, fullname FROM users WHERE id = {}".format(id)
            cursor_pointer.execute(sql)
            row = cursor_pointer.fetchone()
            if row != None:
                return User(row[0], row[1], None, row[2])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
