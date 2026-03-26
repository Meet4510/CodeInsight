-- Database SQL for CodeInsight
-- Create Database
CREATE DATABASE IF NOT EXISTS code_reviewer;
USE code_reviewer;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    plan VARCHAR(20) NOT NULL DEFAULT 'free',
    bio TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Uploaded Files Table
CREATE TABLE IF NOT EXISTS uploaded_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_upload_date (upload_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Analysis Results Table
CREATE TABLE IF NOT EXISTS analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT NOT NULL,
    score INT DEFAULT 0,
    complexity FLOAT DEFAULT 0,
    maintainability FLOAT DEFAULT 0,
    issues LONGTEXT,
    suggestions LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES uploaded_files(id) ON DELETE CASCADE,
    UNIQUE KEY unique_file_analysis (file_id),
    INDEX idx_score (score),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample user (optional)
-- Password: 'password123' (hashed with werkzeug)
INSERT INTO users (name, email, password) VALUES 
('Demo User', 'demo@example.com', 'pbkdf2:sha256:600000$...$...');

ALTER TABLE users ADD COLUMN avatar VARCHAR(255) DEFAULT 'default.png';
