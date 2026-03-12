# Installation Guide for Face Recognition Authentication System

This guide provides step-by-step instructions for setting up the Face Recognition Authentication System on a new computer.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Windows Installation](#windows-installation)
3. [macOS Installation](#macos-installation)
4. [Linux Installation](#linux-installation)
5. [Database Setup](#database-setup)
6. [Configuration](#configuration)
7. [First Run](#first-run)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **MySQL Server 8.0+** - [Download MySQL](https://dev.mysql.com/downloads/mysql/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Web Browser** - Chrome, Firefox, Safari, or Edge

### Hardware Requirements
- **Webcam or built-in camera**
- **Minimum 4GB RAM**
- **2GB free disk space**
- **Internet connection** (for initial setup)

## Windows Installation

### Step 1: Install Prerequisites

1. **Install Python 3.8+**
   ```bash
   # Download from https://www.python.org/downloads/
   # Make sure to check "Add Python to PATH" during installation
   ```

2. **Install MySQL Server**
   ```bash
   # Download MySQL Installer from https://dev.mysql.com/downloads/installer/
   # Choose "Developer Default" setup
   # Remember your root password!
   ```

3. **Install Git**
   ```bash
   # Download from https://git-scm.com/download/win
   # Use default settings during installation
   ```

### Step 2: Clone and Setup Project

1. **Open Command Prompt or PowerShell**
   ```cmd
   # Press Win + R, type "cmd", press Enter
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/Jasper-ace/DeepFace.git
   cd DeepFace
   ```

3. **Run the automated setup**
   ```bash
   # Double-click start_server.bat
   # OR run manually:
   start_server.bat
   ```

4. **If automated setup fails, run manually:**
   ```bash
   # Create virtual environment
   python -m venv venv
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Setup database (make sure MySQL is running)
   mysql -u root -p deepface < setup_mysql.sql
   
   # Run Django setup
   python manage.py makemigrations
   python manage.py migrate
   python manage.py collectstatic --noinput
   
   # Start server
   python manage.py runserver
   ```

## macOS Installation

### Step 1: Install Prerequisites

1. **Install Homebrew** (if not already installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python**
   ```bash
   brew install python@3.9
   ```

3. **Install MySQL**
   ```bash
   brew install mysql
   brew services start mysql
   
   # Secure MySQL installation
   mysql_secure_installation
   ```

4. **Install Git**
   ```bash
   brew install git
   ```

### Step 2: Clone and Setup Project

1. **Open Terminal**
   ```bash
   # Press Cmd + Space, type "Terminal", press Enter
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/Jasper-ace/DeepFace.git
   cd DeepFace
   ```

3. **Setup the project**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Setup database
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS deepface;"
   mysql -u root -p deepface < setup_mysql.sql
   
   # Run Django setup
   python manage.py makemigrations
   python manage.py migrate
   python manage.py collectstatic --noinput
   
   # Start server
   python manage.py runserver
   ```

## Linux Installation (Ubuntu/Debian)

### Step 1: Install Prerequisites

1. **Update system packages**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Python and pip**
   ```bash
   sudo apt install python3 python3-pip python3-venv -y
   ```

3. **Install MySQL**
   ```bash
   sudo apt install mysql-server -y
   sudo mysql_secure_installation
   ```

4. **Install Git and other dependencies**
   ```bash
   sudo apt install git build-essential libmysqlclient-dev -y
   ```

### Step 2: Clone and Setup Project

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jasper-ace/DeepFace.git
   cd DeepFace
   ```

2. **Setup the project**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Setup database
   sudo mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS deepface;"
   mysql -u root -p deepface < setup_mysql.sql
   
   # Run Django setup
   python manage.py makemigrations
   python manage.py migrate
   python manage.py collectstatic --noinput
   
   # Start server
   python manage.py runserver
   ```

## Database Setup

### Option 1: Create New MySQL Database

1. **Connect to MySQL**
   ```bash
   mysql -u root -p
   ```

2. **Create database and user**
   ```sql
   CREATE DATABASE deepface;
   CREATE USER 'faceauth'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON deepface.* TO 'faceauth'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

3. **Run setup script**
   ```bash
   mysql -u faceauth -p deepface < setup_mysql.sql
   ```

### Option 2: Use Existing Database

If you already have a MySQL database:

1. **Import the schema**
   ```bash
   mysql -u your_username -p your_database < setup_mysql.sql
   ```

2. **Update settings** in `.env` file

## Configuration

### Step 1: Create Environment File

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-very-secret-key-here-change-this-in-production
DEBUG=True

# Database Settings
DB_NAME=deepface
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# Face Recognition Settings
FACE_CONFIDENCE_THRESHOLD=0.6
LIVENESS_DETECTION=False
FACE_CAPTURE_FRAMES=25

# Session Settings
SESSION_COOKIE_AGE=1800
```

### Step 2: Update Django Settings

If needed, modify `face_auth_project/settings.py`:

```python
# For production, set DEBUG = False
DEBUG = False

# Add your domain to ALLOWED_HOSTS
ALLOWED_HOSTS = ['yourdomain.com', 'localhost', '127.0.0.1']
```

## First Run

### Step 1: Start the Server

```bash
# Activate virtual environment (if not already active)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Start Django server
python manage.py runserver
```

### Step 2: Access the Application

1. **Open your web browser**
2. **Navigate to:** `http://localhost:8000`
3. **Allow camera permissions** when prompted

### Step 3: Register Your First User

1. **Click "Set Up Face ID"**
2. **Enter username and email**
3. **Follow the face registration process:**
   - Look directly at the camera
   - Move your head slowly for multi-angle capture
   - Blink naturally when prompted
   - Wait for "Face ID setup complete" message

### Step 4: Test Authentication

1. **Click "Sign In"**
2. **Look at the camera**
3. **Blink naturally**
4. **Wait for authentication to complete**

## Troubleshooting

### Common Installation Issues

**Python not found:**
```bash
# Windows: Make sure Python is in PATH
# Add Python to system PATH or reinstall with "Add to PATH" checked

# macOS/Linux: Use python3 instead of python
python3 --version
```

**MySQL connection failed:**
```bash
# Check if MySQL is running
# Windows:
net start mysql80

# macOS:
brew services start mysql

# Linux:
sudo systemctl start mysql
```

**Permission denied errors:**
```bash
# Run with administrator/sudo privileges
# Windows: Run Command Prompt as Administrator
# macOS/Linux: Use sudo for system commands
```

**Camera not working:**
- Check browser permissions (click lock icon in address bar)
- Close other applications using the camera
- Try a different browser
- Restart the browser

**Face not detected:**
- Ensure good lighting
- Position face clearly in camera view
- Check camera is working in other applications
- Try different angles

### Performance Issues

**Slow face recognition:**
- Ensure good lighting conditions
- Close unnecessary applications
- Check system resources (CPU, RAM)
- Lower the confidence threshold in settings

**High CPU usage:**
- Reduce `FACE_CAPTURE_FRAMES` in settings
- Close other resource-intensive applications
- Consider upgrading hardware

### Database Issues

**Migration errors:**
```bash
# Reset migrations
python manage.py migrate --fake-initial

# Or delete migration files and recreate
rm face_auth_app/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

**Database connection timeout:**
- Check MySQL server status
- Verify credentials in `.env` file
- Increase connection timeout in MySQL settings

## Getting Help

If you encounter issues not covered here:

1. **Check the main [README.md](README.md)**
2. **Search existing [GitHub Issues](https://github.com/Jasper-ace/DeepFace/issues)**
3. **Create a new issue** with:
   - Operating system and version
   - Python version
   - Error messages (full traceback)
   - Steps to reproduce the problem

## Next Steps

After successful installation:

1. **Customize the interface** - Modify templates and CSS
2. **Configure security settings** - Update SECRET_KEY, enable HTTPS
3. **Set up production deployment** - Use proper web server (nginx, Apache)
4. **Enable additional features** - Liveness detection, multi-factor auth
5. **Monitor and maintain** - Regular backups, security updates

---

**🎉 Congratulations! Your Face Recognition Authentication System is now ready to use!**