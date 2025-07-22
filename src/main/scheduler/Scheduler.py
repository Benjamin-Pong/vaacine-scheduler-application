

from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import random
import re


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    """
    TODO: Part 1
    """
    if len(tokens)!= 3:
        print ("Failed to create user.")
        return
    username = tokens[1]
    password = tokens[2]
    
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)
    
    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)



def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregiver WHERE username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM patient WHERE p_username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['p_username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False



def login_patient(tokens):
    """
    TODO: Part 1
    """
    global current_patient
    
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    
    try:
        patient = Patient(username, password=password).get()
        
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    #print(patient.get_username())
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    
    if current_caregiver is None and current_patient is None:
        print ("Please login first.")
        return
    
    if len(tokens) != 2:
        print ("Please try again.")
        return
            
       
    cm = ConnectionManager()
    conn = cm.create_connection()
        
    date = tokens[1]
        
    #check if date is in the right format
    if bool(re.match(r'(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])-(2[0-9][0-9][0-9])$', date)) is False:
        print("Please try again.")
        return
        
    #queries to get caregiver availability and available vaccines
    caregiver_availabilities = 'SELECT username FROM availabilities WHERE Time = %s ORDER BY username ASC'
    vaccine_availabilities = "SELECT * FROM vaccines WHERE doses > 0"
        
    row = None
        
    try:
        cursor2 = conn.cursor(as_dict=True)
        cursor2.execute (caregiver_availabilities, date)
        row = cursor2.fetchone()
        
        
        #if no vaccines available, or no vaccines or no doses available, there are no appointments.
        if row is None:
            print ("There are no available appointments for this day.")
            print ("Please try again.")
            return
    
        
        cursor = conn.cursor(as_dict=True)
        cursor.execute(caregiver_availabilities, date)
        for row in cursor:
            print(row['username'])
        cursor3 = conn.cursor(as_dict=True)
        cursor3.execute (vaccine_availabilities)
        for r2 in cursor3:
            print (r2['v_name'] + " " + str(r2['doses']))
            
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return
    


#returns apptID, caregiver id
def reserve(tokens):
    """
    TODO: Part 2
    """
    global current_patient
    global current_caregiver
    
    if current_patient is None and current_caregiver is None:
        print ("Please login first.")
        return
    
    if current_patient is None:
        print ("Please login as a patient.")
        return 
    
    if len(tokens) != 3:
        print ('Please try again.')
        return
    
    else:
        row = None
        try:
            date = tokens[1]
            date_tokens = date.split("-")
            month = int(date_tokens[0])
            day = int(date_tokens[1])
            year = int(date_tokens[2])
            v_name = tokens[2]
            
            cm = ConnectionManager()
            conn = cm.create_connection()
            
            #check if date is in the right format
            if bool(re.match(r'(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])-(2[0-9][0-9][0-9])$', date)) is False:
                print("Please enter a valid date in the right format mm-dd-yyyy")
                print("Please try again.")
                return
            
            #checks if for the validity of the vaccine entered - v name exists and doses >0
            vaccine_exists = "SELECT * FROM vaccines WHERE v_name = %s AND doses >0"
            cursorV = conn.cursor(as_dict=True)
            cursorV.execute(vaccine_exists, v_name)
    
            if cursorV.fetchone() is None:
                print("This vaccine is not provided at the moment. Please enter a valid vaccine name.")
                print("To get a valid vaccine name, you may refer to the caregiver sechedule(s) for a particular day.")
                return
            
            #checks if the patient has already made an identical appointment on this day
            appointment_exists = "SELECT * FROM appointments WHERE appt_pusername = %s AND appt_vaccine = %s AND time = %s"
            cursorA = conn.cursor(as_dict=True)
            cursorA.execute(appointment_exists, (current_patient.get_username(), v_name, date))
            if cursorA.fetchone() is not None:
                print ("An appointment for this vaccine, on this day, has already been made.")
                print ("Please try again.")
                return
              
            #extract first caregiver username from the selected date
            #if no caregiver available, there is no available appointment - prints "no caregiver is available") and returns
            caregiver_selected = 'SELECT username FROM availabilities WHERE time = %s ORDER BY username'
            cursorX= conn.cursor(as_dict=True)
            cursorX.execute(caregiver_selected, date)
            caregiver = cursorX.fetchone()
            
            if caregiver is None or caregiver == '':
                print ("No caregiver is available")
                return
          
            #extract number of doses, check if there are enough does. If there are 0 doses, return.
            vaccine_doses = 'SELECT doses FROM vaccines where v_name = %s'
            cursorY = conn.cursor(as_dict = True)
            cursorY.execute(vaccine_doses, v_name)
            avail_doses = cursorY.fetchone()
            if int(avail_doses['doses']) == 0:
                print ("Not enough available doses.")
                return
            
            
            #add an appointment to the appointment relation
            #created apptID by using the date + username's length and a random number from 2 to 100000
            apptID = year + month + day + len(current_patient.get_username()) + random.randint(2, 100000)
            p_username =current_patient.get_username()
            c_username = caregiver['username']
            
            #check if apptID has already been taken
                #if yes, we add some random value to the ID to create a unique ID
                #if not, we insert values into appointments
            check_ID = "SELECT * FROM appointments WHERE apptID = %s"
            cursorC = conn.cursor(as_dict = True)
            cursorC.execute(check_ID, apptID)
            add_appointment = 'INSERT INTO APPOINTMENTS VALUES (%s, %s, %s, %s, %s)'
            
            if cursorC.fetchone() is None:
                cursor = conn.cursor(as_dict = True)
                cursor.execute(add_appointment,(apptID, p_username,  c_username, v_name, date))
                conn.commit()
            else:
                apptID  += random.randint(2, 2450)
                cursor1 = conn.cursor(as_dict = True)
                cursor1.execute(add_appointment, (apptID, p_username,  c_username, v_name, date))
                conn.commit()
              
            print (str(apptID) + " " + c_username)
            
            #remove a tuple date, v_name from availabilities relation
            remove_availability = 'DELETE FROM availabilities WHERE username = %s AND Time = %s'
            cursor0 = conn.cursor(as_dict=True)
            cursor0.execute(remove_availability, (c_username, date))
            conn.commit()
            
            #decrease the number of available doses, only if the number of available doses is more than 0 or else we will get negative doses
            
            vaccine = Vaccine(v_name, avail_doses['doses'])
            if avail_doses['doses'] > 0:
                vaccine.decrease_available_doses(1)
            #print(vaccine.get_available_doses())
            
        except pymssql.Error as e:
            print("Please try again.")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error when reserving appointment")
            print("Error:", e)
            return
        finally:
            cm.close_connection()
    
    
def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again.")
        return

    date = tokens[1]
    # check if input date is hyphenated in the format mm-dd-yyyy
    
    if bool(re.match(r'(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])-(2[0-9][0-9][0-9])$', date)) is True:
        date_tokens = date.split("-")
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])
    elif bool(re.match(r'(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])-(2[0-9][0-9][0-9])$', date)) is False:
        print ("Please try again.")
        return
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
            
        d = datetime.datetime(year, month, day)
        
        #check if the caregiver has an appointment on that day already. If yes, s/he cannot uploading availability for this day will be denied.
        appointment_taken = "SELECT * FROM appointments WHERE time = %s AND appt_cusername = %s"
        cursor = conn.cursor(as_dict=True)
        cursor.execute(appointment_taken, (d, current_caregiver.get_username()))
        if bool(cursor.fetchone()) is False:
            current_caregiver.upload_availability(d)
        else:
            print ("You have already been scheduled for an appointment on this day.")
            return
        
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


#prints "appointment canceled!"
#updates availabilities, available doses, and removes appointments from the Appointments table
def cancel(tokens):
    """
    TODO: Extra Credit
    """
    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print ("Please login first")
        return
    
    if len(tokens) != 2:
        print ("Please try again.")
        return
    
    apptID = tokens[1]
    
    cm = ConnectionManager()
    conn = cm.create_connection()
        
    
    try:
        
        #caregiver, patient can only cancel appointments that they have been scheduled for
        #check for the validity of the apptID and whe
        if current_caregiver:
            check_id = "SELECT * FROM appointments WHERE apptID = %s AND appt_cusername = %s"
            cursor = conn.cursor(as_dict=True)
            cursor.execute(check_id, (apptID, current_caregiver.get_username()))
            if cursor.fetchone() is None:
                print ("Please enter a valid appointment ID.")
                return
            
        
        if current_patient:
            check_pid = "SELECT * FROM appointments WHERE apptID = %s AND appt_pusername = %s"
            cursor1 = conn.cursor(as_dict=True)
            cursor1.execute(check_pid, (apptID, current_patient.get_username()))
            if cursor1.fetchone() is None:
                print ("Please enter a valid appointment ID.")
                return
        
        #extract the caregiver, vaccine time to update availabilities and doses later
        get_caregiver = "SELECT appt_cusername, appt_vaccine, time FROM appointments WHERE apptID = %s"
        cursor2 = conn.cursor(as_dict = True)
        cursor2.execute(get_caregiver, apptID)
        row = cursor2.fetchone()
        CID = row['appt_cusername']
        d = row['time']
        vaccine = row['appt_vaccine']
        #print (CID)
        #print (d)
        #print (vaccine)
        
        #remove appointment from appointments table by querying for the apptID since apptID is the primary key
        remove_appointment = " DELETE FROM appointments WHERE apptID = %s"
        cursor3 = conn.cursor(as_dict = True)
        cursor3.execute(remove_appointment, apptID)
        conn.commit()
        #since an appointment was canceled, we update/add the caregiver's availability
        add_availabilities = "INSERT INTO availabilities VALUES (%s, %s)"
        cursor4 = conn.cursor(as_dict = True)
        cursor4.execute(add_availabilities, (CID, d))
        conn.commit()
        
        
        #add available doses for the vaccine
        get_doses = 'SELECT doses FROM vaccines WHERE v_name = %s'
        cursor5 = conn.cursor(as_dict = True)
        cursor5.execute(get_doses, (vaccine))
        V = Vaccine(vaccine, cursor5.fetchone()['doses'])
        V.increase_available_doses(1)
        #print(V.get_available_doses())
           
    except pymssql.Error as e:
        print("Please try again.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error when cancelling appointment")
        print("Error:", e)
        return
    finally:
        cm.close_connection()
    print ("Appointment canceled!")
    
    
def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first.")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again.")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    global current_caregiver
    global current_patient
    
    if current_caregiver is None and current_patient is None:
        print ("Please login first.")
    
    else:
        cm = ConnectionManager()
        conn = cm.create_connection()
        
        #check if logged in as caregiver or patient. Each corresponds to a different output.
        try:
            
            appointment_exists = "SELECT * FROM appointments WHERE appt_cusername = %s"
            if current_caregiver:
                caregiver_username = current_caregiver.get_username()
                appointment_exists = "SELECT * FROM appointments WHERE appt_cusername = %s"
                cursorA = conn.cursor(as_dict = True)
                cursorA.execute(appointment_exists, caregiver_username)
                #if no appointments at all, print ('There are no scheduled appointments')
                if cursorA.fetchone() is None:
                    print ("There are no scheduled appointments for this day")
                    return
                show_appt = "SELECT apptID, appt_pusername, appt_vaccine, time FROM appointments WHERE appt_cusername = %s ORDER BY apptID"
                cursor1 = conn.cursor(as_dict = True)
                cursor1.execute(show_appt, caregiver_username)
                for row in cursor1.fetchall():
                    print (str(row['apptID']) + " " + str(row['appt_vaccine']) + " " +  str(row['time']) + " "+ str(row['appt_pusername']))
                
            elif current_patient:
                
                patient_username = current_patient.get_username()
                appointment_exists = "SELECT * FROM appointments WHERE appt_pusername = %s"
                cursorB = conn.cursor(as_dict = True)
                cursorB.execute(appointment_exists, patient_username)
                #if no appointments at all, print ('There are no scheduled appointments')
                if cursorB.fetchone() is None:
                    print ("There are no scheduled appointments for this day")
                    return
                show_appt = "SELECT apptID, appt_vaccine, time, appt_cusername FROM appointments WHERE appt_pusername = %s ORDER BY apptID"
                cursor2 = conn.cursor(as_dict = True)
                cursor2.execute(show_appt, patient_username)
                for row in cursor2.fetchall():
                    print (str(row['apptID']) + " " + str(row['appt_vaccine']) + " " +  str(row['time']) + " "+ str(row['appt_cusername']))
        
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
                
        

def logout(tokens):
    """
    TODO: Part 2
    """
    
    global current_patient
    global current_caregiver
    
    if current_patient is not None or current_caregiver is not None:
        current_patient = None
        current_caregiver = None
        print ("Successfully logged out.")
        
        
def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == 'cancel':
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
