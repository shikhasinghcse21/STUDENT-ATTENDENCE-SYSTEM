-- create database (run once)
CREATE DATABASE IF NOT EXISTS teacher_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE teacher_db;

-- TEACHERS
CREATE TABLE IF NOT EXISTS teachers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  email VARCHAR(150) UNIQUE,
  password VARCHAR(255) NOT NULL,
  status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- STUDENTS
CREATE TABLE IF NOT EXISTS students (
  roll_no VARCHAR(50) PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  branch VARCHAR(100),
  email VARCHAR(150) UNIQUE,
  password VARCHAR(255) NOT NULL,
  year VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- SUBJECTS
CREATE TABLE IF NOT EXISTS subjects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  branch VARCHAR(100),
  teacher_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_subject_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ATTENDANCE
CREATE TABLE IF NOT EXISTS attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_roll_no VARCHAR(50) NOT NULL,
  subject_id INT NOT NULL,
  teacher_id INT,
  date DATE NOT NULL,
  status ENUM('Present','Absent') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_att_student FOREIGN KEY (student_roll_no) REFERENCES students(roll_no)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_att_subject FOREIGN KEY (subject_id) REFERENCES subjects(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_att_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  UNIQUE KEY uniq_attendance_per_day (student_roll_no, subject_id, date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Optional: admins table (if you want DB-based admin accounts)
CREATE TABLE IF NOT EXISTS admins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  name VARCHAR(150),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- SAMPLE DATA (safe to run — adjust passwords later)
-- Insert a teacher sample (will be Pending by default)
INSERT INTO teachers (name, email, password, status)
VALUES ('Sample Teacher', 'teacher1@example.com', 'pass123', 'Approved');

-- Insert a sample student
INSERT INTO students (roll_no, name, branch, email, password, year)
VALUES ('2025CSE001', 'Demo Student', 'CSE', 'student1@example.com', 'stud123', '2nd');

-- Insert a sample subject assigned to teacher id 1 (adjust teacher id if different)
INSERT INTO subjects (name, branch, teacher_id)
VALUES ('Database Systems', 'CSE', 1);

-- Insert an admin account into admins (optional)
INSERT INTO admins (username, password, name) VALUES ('admin', 'admin123', 'Site Admin');

-- Create a dump file command (run in shell) -- shown below in instructions

SELECT * FROM students;


-- yha se teacher attendence session create krega

-- Attendance sessions / links created by teacher
CREATE TABLE IF NOT EXISTS attendance_sessions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  teacher_id INT NOT NULL,
  subject_id INT NOT NULL,
  token VARCHAR(128) NOT NULL UNIQUE,
  latitude DECIMAL(10,7) NOT NULL,
  longitude DECIMAL(10,7) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  is_active TINYINT(1) DEFAULT 1,
  max_radius_m INT DEFAULT 20,
  session_note VARCHAR(255),
  FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Store which student marked via session (to show session attendees)
CREATE TABLE IF NOT EXISTS session_attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  session_id INT NOT NULL,
  student_roll_no VARCHAR(50) NOT NULL,
  marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status ENUM('Present','Absent') DEFAULT 'Present',
  ip_addr VARCHAR(45),
  latitude DECIMAL(10,7),
  longitude DECIMAL(10,7),
  UNIQUE KEY uniq_session_student (session_id, student_roll_no),
  FOREIGN KEY (session_id) REFERENCES attendance_sessions(id) ON DELETE CASCADE,
  FOREIGN KEY (student_roll_no) REFERENCES students(roll_no) ON DELETE CASCADE
);
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    branch VARCHAR(50),
    teacher_id INT,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
);
