# Python Application for Vaccine Scheduler
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


