import pymysql
import json
import os
import hashlib
from flask_login import UserMixin

class User(UserMixin):
     def __init__(self, id_, name, email):
        self.id = id_
        self.name = name
        self.email = email




class UserResource:

    def __int__(self):
        pass

    @staticmethod
    def _get_connection():

        usr = os.environ.get("DBUSER")
        pw = os.environ.get("DBPW")
        h = os.environ.get("DBHOST")

        conn = pymysql.connect(
            user=usr,
            password=pw,
            host=h,
            port=3306,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return conn

    @staticmethod
    def getUser(id):
        sql = "select * FROM users.users where ID=%s;"
        conn = UserResource._get_connection()
        cursor = conn.cursor()
        res = cursor.execute(sql, (id))

        if res >= 1:
            result = cursor.fetchall()
        else:
            result = None
        conn.close()
        return result

    @staticmethod
    def getUsers():
        sql = "select * FROM users.users"
        conn = UserResource._get_connection()
        cursor = conn.cursor()
        res = cursor.execute(sql)

        if res >= 1:
            result = cursor.fetchall()
        else:
            result = None
        conn.close()
        return result

    @staticmethod
    def getUserSSO(id):
        sql = "select * FROM users.users where ID=%s;"
        conn = UserResource._get_connection()
        cursor = conn.cursor()
        res = cursor.execute(sql, (id))

        if res >= 1:
            result = cursor.fetchall()
        else:
            result = None
            conn.close()
            return None
        user = User(id_=result[0]["ID"], name=result[0]["FirstName"], email=result[0]["Email"])
        conn.close()
        return user

    
    @staticmethod
    def addUserSSO(user):
        if UserResource.getUserSSO(user.id) is None:

            values = "(" + "'" + user.id + "'" + ", " +"'" + user.email + "'" + ", " + "'" + user.name + "'" + ", " +  "'" + user.name + "'" + ")"
            columns = "(ID, Email, FirstName, LastName)"
            sql = "INSERT INTO users.users  " + columns +  " VALUES  " + values +  ";"
            conn = UserResource._get_connection()
            cursor = conn.cursor()
            res = cursor.execute(sql)

            conn.commit()

            conn.close()


    @staticmethod
    def addUser(new_resource):
        hash_object = hashlib.sha1(new_resource["Email"].encode())
        hex_dig = hash_object.hexdigest()
        values = "(" + "'" + hex_dig + "'" + ", " +"'" +new_resource["Email"] + "'" + ", " + "'" +new_resource["FirstName"] + "'" + ", " +  "'" +new_resource["LastName"] + "'" + ")"
        columns = "(ID, Email, FirstName, LastName)"
        sql = "INSERT INTO users.users  " + columns +  " VALUES  " + values +  ";"
        print(sql)
        conn = UserResource._get_connection()
        cursor = conn.cursor()
        res = cursor.execute(sql)

        conn.commit()
        conn.close()
        return hex_dig

        pass

    @staticmethod
    def updatePlaylist(id, new_values):

        column_string = []
        i = 1
        for key, val in new_values.items():
            if i < len(new_values):
                column_string.append(key + "=" + '"' + str(val) + '"' + ",")
                i += 1
            else:
                column_string.append(key + "=" + '"' + str(val) + '"')
        column_string = " ".join(column_string)
        sql = "UPDATE users.users" + " SET " + column_string + " where ID=%s"
        conn = UserResource._get_connection()
        cursor = conn.cursor()
     
        res = cursor.execute(sql, (id))
        conn.commit()
        conn.close()
        return 1
 
        pass

    @staticmethod
    def DeleteUser(id):
        sql = "DELETE FROM users.users WHERE ID=" + "'" + id + "'"
        print(sql)
        conn = UserResource._get_connection()
        cursor = conn.cursor()

        try:
            res = cursor.execute(sql)
            conn.commit()
            conn.close()
            return 1
        except:
            conn.close()
            return 0

        pass
