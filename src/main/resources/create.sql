CREATE table PATIENT(
p_username varchar(255) PRIMARY KEY,
p_hash BINARY(16),
p_salt BINARY (16))

CREATE table CAREGIVER(
username varchar(255) PRIMARY KEY,
salt BINARY (16),
Hash binary(16))

CREATE table vaccines(
v_name varchar(255) PRIMARY KEY,
doses INT)

CREATE table AVAILABILITIES(
username varchar(255) REFERENCES Caregiver,
Time date,
PRIMARY KEY(username, time))

CREATE table APPOINTMENTS(
apptID INT PRIMARY KEY, 
appt_pusername varchar(255) REFERENCES PATIENT,
appt_cusername varchar(255) REFERENCES CAREGIVER,
appt_vaccine varchar(255) REFERENCES VACCINES,
time date)


