PRAGMA foreign_keys = ON;

CREATE TABLE Patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL, -- YYYY-MM-DD
    gender TEXT CHECK (gender IN ('M', 'F', 'O')),
    contact_number TEXT,
    address TEXT,
    email TEXT,
    medical_history TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    risk_score INTEGER
);

CREATE INDEX idx_patient_name ON Patients(last_name, first_name);

CREATE TABLE Doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    contact_number TEXT,
    email TEXT,
    available_schedule TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_specialty ON Doctors(specialty);

CREATE TABLE Departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT,
    location TEXT
);

CREATE TABLE Doctor_Department (
    doctor_id INTEGER,
    department_id INTEGER,
    PRIMARY KEY (doctor_id, department_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE CASCADE
);

CREATE TABLE Appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER,
    appointment_date TEXT NOT NULL, -- YYYY-MM-DD
    appointment_time TEXT NOT NULL, -- HH:MM:SS
    purpose TEXT,
    status TEXT DEFAULT 'Scheduled',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id) ON DELETE SET NULL
);

CREATE INDEX idx_appointment_date ON Appointments(appointment_date, appointment_time);

CREATE TABLE Medical_Records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER,
    appointment_id INTEGER,
    diagnosis TEXT,
    treatment TEXT,
    prescription TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id) ON DELETE SET NULL,
    FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id)
);

CREATE INDEX idx_record_patient ON Medical_Records(patient_id);

CREATE TABLE Cpts (
    code VARCHAR(10) PRIMARY KEY,
    description TEXT
);

CREATE TABLE Billing (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    appointment_id INTEGER,
    total_amount NUMERIC NOT NULL,
    payment_status TEXT DEFAULT 'Pending',
    payment_date TEXT, -- YYYY-MM-DD
    insurance_provider TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    cpt_code VARCHAR(10),
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id),
    FOREIGN KEY (cpt_code) REFERENCES Cpts(code)
);


CREATE INDEX idx_payment_status ON Billing(payment_status);

CREATE TABLE Staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    role TEXT NOT NULL CHECK (role IN ('Nurse', 'Worker', 'Admin', 'Pharmacist', 'Technician', 'Lab Assistant', 'Driver')),
    department_id INTEGER,
    contact_number TEXT,
    email TEXT,
    address TEXT,
    hire_date TEXT, -- YYYY-MM-DD
    FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE SET NULL
);

CREATE INDEX idx_staff_role ON Staff(role);

CREATE TABLE Nurses (
    nurse_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    specialization TEXT,
    shift_hours TEXT,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id) ON DELETE CASCADE
);

CREATE TABLE Workers (
    worker_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER,
    job_title TEXT,
    work_schedule TEXT,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id) ON DELETE CASCADE
);

CREATE TABLE Medicine (
    medicine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    brand TEXT,
    type TEXT CHECK (type IN ('Tablet', 'Capsule', 'Liquid', 'Injection', 'Ointment')),
    dosage TEXT,
    stock_quantity INTEGER CHECK (stock_quantity >= 0),
    expiry_date TEXT, -- YYYY-MM-DD
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_medicine_type ON Medicine(type);
CREATE INDEX idx_medicine_expiry ON Medicine(expiry_date);

CREATE TABLE Pharmacy (
    pharmacy_id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_id INTEGER,
    patient_id INTEGER,
    quantity INTEGER,
    prescription_date TEXT, -- YYYY-MM-DD
    FOREIGN KEY (medicine_id) REFERENCES Medicine(medicine_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE
);

CREATE TABLE Blood_Bank (
    blood_id INTEGER PRIMARY KEY AUTOINCREMENT,
    blood_type TEXT CHECK (blood_type IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    stock_quantity INTEGER CHECK (stock_quantity >= 0),
    last_updated TEXT -- YYYY-MM-DD
);

CREATE INDEX idx_blood_type ON Blood_Bank(blood_type);

CREATE TABLE Room_Types (
    room_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_type_name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE Rooms (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number TEXT UNIQUE NOT NULL,
    room_type_id INTEGER,
    capacity INTEGER,
    status TEXT CHECK (status IN ('Available', 'Occupied', 'Under Maintenance')),
    last_serviced TEXT, -- YYYY-MM-DD
    FOREIGN KEY (room_type_id) REFERENCES Room_Types(room_type_id) ON DELETE SET NULL
);

CREATE TABLE Room_Assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER,
    staff_id INTEGER,
    patient_id INTEGER,
    assignment_date TEXT DEFAULT CURRENT_TIMESTAMP,
    end_date TEXT,
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id) ON DELETE SET NULL,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE SET NULL
);

CREATE TABLE Cleaning_Service (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER,
    service_date TEXT DEFAULT CURRENT_DATE,
    service_time TEXT DEFAULT CURRENT_TIME,
    staff_id INTEGER,
    notes TEXT,
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id),
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
);

CREATE TABLE Prescription (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    prescription_date TEXT DEFAULT CURRENT_DATE,
    medication_name TEXT,
    dosage TEXT,
    frequency TEXT,
    duration TEXT,
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)
);

CREATE TABLE Ambulance (
    ambulance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ambulance_number TEXT UNIQUE,
    availability TEXT CHECK (availability IN ('Available', 'On Duty', 'Maintenance')),
    driver_id INTEGER,
    last_service_date TEXT, -- YYYY-MM-DD
    FOREIGN KEY (driver_id) REFERENCES Staff(staff_id)
);

CREATE TABLE Ambulance_Log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ambulance_id INTEGER,
    patient_id INTEGER,
    pickup_location TEXT,
    dropoff_location TEXT,
    pickup_time TEXT,   -- YYYY-MM-DD HH:MM:SS
    dropoff_time TEXT,  -- YYYY-MM-DD HH:MM:SS
    status TEXT CHECK (status IN ('Completed', 'In Progress', 'Canceled')),
    FOREIGN KEY (ambulance_id) REFERENCES Ambulance(ambulance_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE
);

CREATE TABLE Medical_Records_Medicine (
    record_id INTEGER,
    medicine_id INTEGER,
    dosage TEXT,
    PRIMARY KEY (record_id, medicine_id),
    FOREIGN KEY (record_id) REFERENCES Medical_Records(record_id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES Medicine(medicine_id) ON DELETE CASCADE
);