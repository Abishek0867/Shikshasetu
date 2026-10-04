-- ShikshaSetu Production MySQL Database Schema DDL
-- Create Database
CREATE DATABASE IF NOT EXISTS shikshasetu CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE shikshasetu;

-- 1. Scholarship Schemes Table
CREATE TABLE IF NOT EXISTS schemes (
  id INT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(50) NOT NULL,
  name VARCHAR(255) NOT NULL,
  portal VARCHAR(100) NOT NULL,
  levels VARCHAR(255) NOT NULL,
  income_limit INT DEFAULT 0,
  amount INT NOT NULL,
  needs_net TINYINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Official Government Student Registry Table (Stand-in for APAAR & UDISE+)
CREATE TABLE IF NOT EXISTS gov_registry (
  apaar_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  tribe VARCHAR(100),
  is_st TINYINT DEFAULT 1,
  st_cert_valid TINYINT DEFAULT 1,
  income INT,
  income_cert_valid TINYINT DEFAULT 1,
  institution VARCHAR(255),
  institution_recognised TINYINT DEFAULT 1,
  level VARCHAR(50),
  enrolled TINYINT DEFAULT 1,
  net_jrf TINYINT DEFAULT 0,
  state VARCHAR(100),
  district VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Students Table
CREATE TABLE IF NOT EXISTS students (
  apaar_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  state VARCHAR(100),
  district VARCHAR(100),
  family_id INT,
  lang VARCHAR(10) DEFAULT 'en',
  FOREIGN KEY (apaar_id) REFERENCES gov_registry(apaar_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Scholarship Applications Table
CREATE TABLE IF NOT EXISTS applications (
  id INT PRIMARY KEY AUTO_INCREMENT,
  apaar_id VARCHAR(50) NOT NULL,
  scheme_id INT NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'SUBMITTED',
  remarks TEXT,
  created_at VARCHAR(30),
  updated_at VARCHAR(30),
  FOREIGN KEY (apaar_id) REFERENCES students(apaar_id) ON DELETE CASCADE,
  FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. DigiLocker Document Wallet Table
CREATE TABLE IF NOT EXISTS documents (
  id INT PRIMARY KEY AUTO_INCREMENT,
  apaar_id VARCHAR(50) NOT NULL,
  doc_type VARCHAR(100) NOT NULL,
  source VARCHAR(100) DEFAULT 'DigiLocker',
  ref VARCHAR(255),
  fetched_at VARCHAR(30),
  FOREIGN KEY (apaar_id) REFERENCES students(apaar_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Verification Results Table
CREATE TABLE IF NOT EXISTS verification_results (
  id INT PRIMARY KEY AUTO_INCREMENT,
  application_id INT NOT NULL,
  source VARCHAR(50) NOT NULL,
  check_name VARCHAR(100) NOT NULL,
  result VARCHAR(50) NOT NULL,
  detail TEXT,
  FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Officer Manual Review Queue Table
CREATE TABLE IF NOT EXISTS review_queue (
  id INT PRIMARY KEY AUTO_INCREMENT,
  application_id INT NOT NULL,
  reason TEXT,
  status VARCHAR(50) DEFAULT 'OPEN',
  officer_note TEXT,
  FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Direct Benefit Transfer (DBT) Disbursements Table
CREATE TABLE IF NOT EXISTS disbursements (
  id INT PRIMARY KEY AUTO_INCREMENT,
  application_id INT NOT NULL,
  amount INT NOT NULL,
  dbt_status VARCHAR(50) DEFAULT 'SUCCESS',
  date VARCHAR(20),
  FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
  id INT PRIMARY KEY AUTO_INCREMENT,
  apaar_id VARCHAR(50) NOT NULL,
  message TEXT NOT NULL,
  created_at VARCHAR(30),
  FOREIGN KEY (apaar_id) REFERENCES students(apaar_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. System Audit Log Table
CREATE TABLE IF NOT EXISTS audit_log (
  id INT PRIMARY KEY AUTO_INCREMENT,
  actor VARCHAR(100) NOT NULL,
  action VARCHAR(100) NOT NULL,
  detail TEXT,
  ts VARCHAR(30)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
