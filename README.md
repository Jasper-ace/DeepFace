# Face Recognition Authentication System

A comprehensive Django-based face recognition authentication system with real-time face detection, liveness detection, and advanced admin management features.

![Face ID Authentication](https://img.shields.io/badge/Authentication-Face%20ID-brightgreen)
![Django](https://img.shields.io/badge/Django-4.2+-blue)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20PostgreSQL-orange)

## 🚀 Features

- **🔐 Face Recognition Authentication**: Secure biometric login system
- **📱 Apple Face ID Style Interface**: Modern UI with neon animations
- **🎯 Real-time Face Detection**: Live camera feed with confidence scoring
- **👁️ Liveness Detection**: Anti-spoofing measures to prevent photo attacks
- **🛡️ Super Admin Dashboard**: Comprehensive user management system
- **📍 IP Location Tracking**: Monitor user login locations and geographic data
- **📊 Advanced Analytics**: Detailed authentication logs and statistics
- **🌙 Dark Mode Interface**: macOS-inspired design with smooth animations
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **⚡ Scalable Architecture**: Handle thousands of users with pagination

## 📋 Prerequisites

Before installing, ensure you have:

- **Python 3.10+** installed ([Download Python](https://python.org/downloads/))
- **Git** installed ([Download Git](https://git-scm.com/downloads))
- **MySQL Server 8.0+** or **PostgreSQL 12+**
- **Webcam/Camera** for face recognition
- **Modern web browser** with camera support (Chrome, Firefox, Safari, Edge)

## 🛠️ Complete Installation Guide

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/face-recognition-auth.git

# Navigate to project directory
cd face-recognition-auth
```

### Step 2: Set Up Python Virtual Environment

#### On Windows:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
```

#### On macOS/Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
```

### Step 3: Install Python Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**⚠️ Troubleshooting Installation Issues:**

If you encounter errors during installation:

#### Windows:
```bash
# Install Visual Studio Build Tools (required for face_recognition)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Install CMake
# Download from: https://cmake.org/download/

# Alternative: Use conda
conda install -c conda-forge dlib
pip install face_recognition
```

#### macOS:
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install cmake
brew install dlib
pip install face_recognition
```

#### Ubuntu/Debian:
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y cmake libopenblas-dev liblapack-dev 
sudo apt-get install -y libx11-dev libgtk-3-dev python3-dev
sudo apt-get install -y build-essential cmake pkg-config
vcodec-dev libavformat-dev libswscale-dev

# Then install Python packages
pip install -r requirements.txt
```

### Step 4: Database Setup

#### Option A: MySQL (Recommended for Local Development)

1. **Install MySQL Server**:
   - **Windows**: Download from [MySQL Downloads](https://dev.mysql.com/downloads/mysql/)
   - **macOS**: `brew install mysql`
   - **Ubuntu**: `sudo apt-get install mysql-server`

2. **Start MySQL Service**:
   ```bash
   # Windows (as Administrator)
   net start mysql
   
   # macOS
ervices start mysql
   
   # Ubuntu
   sudo systemctl start mysql
   ```

3. **Create Database and User**:
   ```bash
   # Login to MySQL
   mysql -u root -p
   ```
   
   ```sql
   -- Create database
   CREATE DATABASE deepface CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
   -- Create user (optional but recommended)
   CREATE USER 'deepface_user'@'localhost' IDENTIFIED BY 'secure_password_123';
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON deepface.* TO 'deepface_user'@'localhost';
   FLUSH PRIVILEGES;
   
   -- Verify database creation
   SHOW DATABASES;
   
   -- Exit MySQL
   EXIT;
   ```

4. **Update Database Configuration**:
   
   Edit `face_auth_project/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'deepface',
           'USER': 'deepface_user',  # or 'root'
           'PASSWORD': 'secure_password_123',  # your password
           'HOST': 'localhost',
           'PORT': '3306',
           'OPTIONS': {
               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
           },
       }
   }
   ```

#### Option B: PostgreSQL (Production Ready)

1. **Install PostgreSQL**:
   - **Windows**: Download from [PostgreSQL Downloads](https://www.postgresql.org/download/)
   - **macOS**: `brew install postgresql`
   - **Ubuntu**: `sudo apt-get install postgresql postgresql-contrib`

2. **Create Database**:
   ```bash
   # Switch to postgres user
   sudo -u postgres psql
   ```
   
   ```sql
   -- Create database
   ATE DATABASE deepface;
   
   -- Create user
   CREATE USER deepface_user WITH PASSWORD 'secure_password_123';
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE deepface TO deepface_user;
   
   -- Exit PostgreSQL
   \q
   ```

3. **Update settings.py**:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'deepface',
           'USER': 'deepface_user',
           'PASSWORD': 'secure_password_123',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

#### Option C: SQLite (Quick Testing Only)

For quick testing without setting up MySQL/PostgreSQL:

```python
# In settings.py, replace DATABASES with:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Step 5: Environment Configuration

1. **Create Environment File**:
   ```bash
   # Copy the example file
   cp .env.example .env
   ```

2. **Edit .env file** with your settings:
   ```env
   # Django Settings
   SECRET_KEY=your-very-secure-secret-key-here-make-it-long-and-random
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
   
   # Database (if using environment variables)
   DB_NAME=deepface
   DB_USER=deepface_user
   DB_PASSWORD=secure_password_123
   DB_HOST=localhost
   DB_PORT=3306
   
   # Face Recognition Settings
   FACE_CONFIDENCE_THRESHOLD=0.6
   LIVENESS_DETECTION=True
   
   # Security
   SESSION_COOKIE_AGE=1800
   ```

### Step 6: Initialize Database

```bash
# Create and apply database migrations
python manage.py makemigrations
python manage.py migrate

# Verify migrations were successful
python manage.py showmigrations
```

### Step 7: Create Initial Superuser

```bash
# Create initial admin user
python manage.py create_initial_superuser --username=admin --email=admin@example.com

# Or create manually
python manage.py shell -c "
from face_auth_app.models import FaceUser
import json
user = FaceUser.objects.create(
    username='admin',
    email='admin@example.com',
    is_superadmin=True,
    is_active=True,
    face_encoding=json.dumps([0.0] * 128)  # Placeholder
)
print('Admin user created successfully')
"
```

### Step 8: Collect Static Files

```bash
# Collect all static files
python manage.py collectstatic --noinput

# Verify static files were collected
ls staticfiles/  # Should show admin/ and css/ directories
```

### Step 9: Test the Installation

```bash
# Run system check
python manage.py check

# Test database connection
python manage.py s"
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('Database connection successful!')
"
```

### Step 10: Start the Development Server

```bash
# Start server on localhost
python manage.py runserver

# Or start on all interfaces (accessible from network)
python manage.py runserver 0.0.0.0:8000

# Or use custom port
python manage.py runserver 8080
```

**🎉 Success!** The application should now be running at:
- **Local**: http://127.0.0.1:8000
//your-ip-address:8000
e Registration Process**:nfiguration & Customizatiohon manage.py collectstatic --noinput

# Run server
python manage.py runserver
```

Visit http://127.0.0.1:8000 and start using face recognition authentication!

---

**⭐ Star this repository if you found it helpful!**

**🐛 Found a bug? [Report it here](https://github.com/yourusername/face-recognition-auth/issues)**

**💡 Have a feature idea? [Suggest it here](https://github.com/yourusername/face-recognition-auth/discussions)**otstrap.com/)** - CSS framework

---

## 🚀 Quick Start Summary

For experienced developers, here's the quick setup:

```bash
# Clone and setup
git clone https://github.com/yourusername/face-recognition-auth.git
cd face-recognition-auth
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Database setup (MySQL)
mysql -u root -p -e "CREATE DATABASE deepface;"

# Django setup
python manage.py migrate
python manage.py create_initial_superuser
pytre`
6. **Open Pull Request** with detailed description

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Technologies Used:
- **[Django](https://djangoproject.com/)** - Web framework
- **[face_recognition](https://github.com/ageitgey/face_recognition)** - Face recognition library
- **[OpenCV](https://opencv.org/)** - Computer vision library
- **[dlib](http://dlib.net/)** - Machine learning library
- **[Bootstrap](https://getboents:

**Minimum**:
- 4GB RAM
- 2GB storage
- Webcam (720p)
- Python 3.10+

**Recommended**:
- 8GB RAM
- 5GB storage
- HD Webcam (1080p)
- SSD storage
- Stable internet connection

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** and test thoroughly
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-featuprocessing** - face recognition happens on your server
- **Audit trail** - all authentication attempts logged

## 📞 Support & Community

### Getting Help:

1. **Check Documentation**: Read this README thoroughly
2. **Search Issues**: Look through [GitHub Issues](https://github.com/yourusername/face-recognition-auth/issues)
3. **Browser Console**: Check for JavaScript errors (F12)
4. **Server Logs**: Check Django console output for errors
5. **Create Issue**: Report bugs with detailed information

### System Requiremailable)
- **Heroku** (Easy deployment)
- **DigitalOcean** (VPS hosting)
- **AWS** (Enterprise scale)

## 🔒 Security Features

### Data Protection:
- **Face encodings are encrypted** before database storage
- **No raw images stored** - only mathematical representations
- **Session security** with automatic timeout
- **IP logging** for security monitoring
- **CSRF protection** enabled by default

### Privacy Compliance:
- **GDPR compliant** - users can delete their data
- **No third-party data sharing**
- **Local Not Detected

**Symptoms**: "Could not detect face" error

**Solutions**:
- **Improve lighting**: Use bright, even lighting
- **Position face properly**: Center face in camera view
- **Remove obstructions**: Take off glasses, hat, mask
- **Check camera quality**: Use HD camera if possible
- **Try different angles**: Face camera directly

## 🌐 Production Deployment

For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to:

- **Render.com** (Recommended - Free tier avql

# Ubuntu
sudo systemctl start mysql
sudo systemctl status mysql

# Test connection
mysql -u root -p -e "SELECT 1"
```

#### 3. Camera Not Working

**Symptoms**: Black screen, "Camera access denied"

**Solutions**:
- **Check browser permissions**: Click camera icon in address bar
- **Try different browser**: Chrome is most reliable
- **Check camera usage**: Close other apps using camera
- **Use HTTPS or localhost**: Required for camera access
- **Restart browser**: Sometimes permissions get stuck

#### 4. Face lation Fails

**Error**: `Microsoft Visual C++ 14.0 is required`

**Solution**:
```bash
# Windows: Install Visual Studio Build Tools
# Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Alternative: Use pre-compiled wheels
pip install --upgrade pip
pip install dlib-binary
pip install face_recognition
```

#### 2. Database Connection Errors

**Error**: `Can't connect to MySQL server`

**Solution**:
```bash
# Check if MySQL is running
# Windows
net start mysql

# macOS
brew services start mys

1. **Find your IP address**:
   ```bash
   # Windows
   ipconfig
   
   # macOS/Linux
   ifconfig
   ```

2. **Start server on all interfaces**:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

3. **Update ALLOWED_HOSTS** in settings.py:
   ```python
   ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-ip-address', '*']
   ```

4. **Access from other devices**:
   ```
   http://your-ip-address:8000
   ```

## 🚨 Troubleshooting Guide

### Common Installation Issues

#### 1. Face Recognition Instaln

### Face Recognition Settings

Edit `face_auth_project/settings.py`:

```python
# Recognition sensitivity (0.0 = very strict, 1.0 = very lenient)
FACE_CONFIDENCE_THRESHOLD = 0.6

# Number of frames to capture during registration
FACE_CAPTURE_FRAMES = 25

# Enable anti-spoofing liveness detection
LIVENESS_DETECTION = True

# Session timeout in seconds (1800 = 30 minutes)
SESSION_COOKIE_AGE = 1800
```

### Network Access Configuration

To access from other devices on your network:
from face_auth_app.models import FaceUser
user = FaceUser.objects.get(username='your_username')
user.is_superadmin = True
user.save()
print(f'{user.username} is now a super admin')
"
```

Then access admin features:
- **Dashboard**: http://127.0.0.1:8000/dashboard/
- **Super Admin**: http://127.0.0.1:8000/superadmin/
- **User Management**: http://127.0.0.1:8000/superadmin/users/
- **System Logs**: http://127.0.0.1:8000/superadmin/logs/
- **IP Location**: http://127.0.0.1:8000/superadmin/location/

## ⚙️ Co
   - Look directly at the camera
   - Keep your face centered in the circle
   - Move your head slowly: left → right → up → down
   - Blink naturally during the process
   - Wait for "Face ID setup complete" message

### 4. Test Face Authentication

1. **Click "Sign In"**
2. **Look at the camera**
3. **Blink naturally**
4. **System should recognize you** and log you in automatically

### 5. Access Super Admin Features

Make your user a super admin:

```bash
python manage.py shell -c "
## 🎯 First Time Setup & Usage

### 1. Access the Application

Open your web browser and navigate to:
```
http://127.0.0.1:8000
```

### 2. Allow Camera Permissions

When prompted by your browser:
1. Click **"Allow"** for camera access
2. If blocked, click the camera icon in address bar
3. Select **"Always allow"** for this site

### 3. Register Your First User

1. **Click "Set Up Face ID"**
2. **Enter Details**:
   - Username: `your_username`
   - Email: `your_email@example.com`
3. **Fac