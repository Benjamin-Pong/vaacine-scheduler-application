

import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
  

class Patient:
    def __init__(self, username, password=None, salt=None, hash=None):
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash
             
    #getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict = True)
        
        get_patient_details = "SELECT p_salt, p_hash FROM PATIENT WHERE p_username = %s"
        try:
            cursor.execute(get_patient_details, self.username)
            for row in cursor:
                curr_salt = row['p_salt']
                curr_hash = row['p_hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    #print ("Incorrect password")
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    cm.close_connection()
                    return self
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
        return None
    
    def get_username(self):
        return self.username
    def get_salt(self):
        return self.salt
    def get_hash(self):
        return self.hash
    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        add_patients = "INSERT INTO patient VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_patients, (self.username, self.hash, self.salt))
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()
            

  
            
