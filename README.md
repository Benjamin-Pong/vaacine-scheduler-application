# Vaccine Appointment System with Azure SQL 
#  Overview
Developed during the pandemic peak, this system enables:

- Patients to book/cancel/view vaccination appointments

- Caregivers to manage availability and vaccine inventory

- Secure authentication via salted password hashing

# Technical Implementation
Backend: Python with pymssql for Azure SQL Server integration

Database: Designed schema for patients, caregivers, vaccines, and appointments

Core Features:

Patient/caregiver account creation & login

Appointment scheduling with caregiver auto-assignment (alphabetical priority)

Real-time vaccine dose tracking

Role-based views for appointments

# File Structure
```text
src/
├── main/
│   ├── scheduler/
│   │   └── Scheduler.py          # CLI entry point (command parser/handler)
│   ├── db/
│   │   └── ConnectionManager.py  # Azure DB connector (handles connections/cursors)
│   ├── model/                    # Database entity classes
│   │   ├── Caregiver.py          # Caregiver CRUD operations (provided)
│   │   ├── Vaccine.py            # Vaccine inventory management (provided)
│   │   └── Patient.py            # Patient operations (implemented by student)
│   └── resources/
│       ├── create.sql            # SQL schema definitions
│       └── design.pdf            # ER diagram (student-submitted)
```

# Relational Database Design

Database Architecture
1. Entity-Relationship Diagram

Visual schema showing relationships between entities

2. Schema Implementation
Key tables created via create.sql

