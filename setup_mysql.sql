-- MySQL Setup for Face Recognition Authentication System
-- Database: deepface (existing)
-- User: root
-- Password: 1234

-- Connect to your existing database
USE deepface;

-- Drop tables if they exist (to recreate them)
DROP TABLE IF EXISTS recognition_logs;
DROP TABLE IF EXISTS login_sessions;
DROP TABLE IF EXISTS users;

-- Users Table (stores registered users and facial data)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) UNIQUE,
    face_encoding LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_active (is_active)
);

-- Recognition Logs Table (stores detection events)
CREATE TABLE recognition_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    confidence FLOAT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_detected_at (detected_at),
    INDEX idx_confidence (confidence)
);

-- Login Sessions Table (tracks login sessions)
CREATE TABLE login_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP NULL,
    session_key VARCHAR(40) UNIQUE,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_login_time (login_time),
    INDEX idx_session_key (session_key)
);

-- Show created tables
SHOW TABLES;

-- Show table structures
DESCRIBE users;
DESCRIBE recognition_logs;
DESCRIBE login_sessions;

SELECT 'Database setup completed successfully!' as Status;