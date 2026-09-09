CREATE DATABASE silambam_db;

USE silambam_db;

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    dob DATE,
    gender VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(150),
    course VARCHAR(100),
    batch VARCHAR(50),
    join_date DATE,
    address TEXT,
    status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);