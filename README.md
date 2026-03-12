# Face Recognition Authentication System

A modern web-based authentication system using facial recognition technology, built with Django and featuring an Apple Face ID-style interface.

![Face ID Authentication](https://img.shields.io/badge/Authentication-Face%20ID-brightgreen)
![Django](https://img.shields.io/badge/Django-4.2+-blue)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![MySQL](https://img.shields.io/badge/Database-MySQL-orange)

## Features

- 🔐 **Secure Face Recognition Authentication**
- 📱 **Apple Face ID Style Interface** with neon green animations
- 🎯 **Real-time Face Detection** with confidence scoring
- 👁️ **Liveness Detection** to prevent spoofing
- 📊 **Authentication Logs & Analytics**
- 🌙 **Dark Mode macOS-style Dashboard**
- 🔒 **Session Management** with automatic timeout
- 📱 **Responsive Design** for all devices

## Screenshots

### Home Page
Modern Face ID interface with animated scanning rings and detection points.

### Registration Process
Multi-angle face capture with Apple-style progress indicators and blink detection.

### Dashboard
macOS-inspired dark interface with authentication statistics and activity logs.

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.8 or higher**
- **MySQL Server 8.0+**
- **Git**
- **Webcam/Camera** for face recognition
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Jasper-ace/DeepFace.git
cd DeepFace
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. MySQL Database Setup

#### Option A: Create New Database
```sql
# Connect to MySQL
mysql -u root -p

# Create database
CREATE DATABASE deepface;
USE deepface;

# Run the setup script
source setup_mysql.sql;
```

#### Option B: Use Existing Database
If you already have a `deepface` database, just run:
```bash
mysql -u root -p deepface < setup_mysql.sql
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=deepface
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
FACE_CONFIDENCE_THRESHOLD=0.6
LIVENESS_DETECTION=False
```

### 6. Run Django Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 8. Start the Development Server

```bash
# Windows
start_server.bat

# Or manually
python manage.py runserver
```

### 9. Access the Application

Open your web browser and navigate to:
```
http://localhost:8000
```

## Quick Start Guide

### For Windows Users

1. **Double-click `start_server.bat`** - This will automatically:
   - Create virtual environment
   - Install dependencies
   - Run migrations
   - Start the server

2. **Visit `http://localhost:8000`**

3. **Allow camera permissions** when prompted

4. **Register a new user:**
   - Click "Set Up Face ID"
   - Enter username and email
   - Follow the face registration process
   - Move your head slowly for multi-angle capture

5. **Test authentication:**
   - Click "Sign In"
   - Look at the camera
   - Blink naturally during authentication

## Project Structure

```
DeepFace/
├── face_auth_app/          # Main Django application
│   ├── models.py           # Database models
│   ├── views.py            # View controllers
│   ├── face_recognition_utils.py  # Face recognition logic
│   ├── middleware.py       # Authentication middleware
│   └── decorators.py       # Custom decorators
├── face_auth_project/      # Django project settings
│   ├── settings.py         # Configuration
│   └── urls.py            # URL routing
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── home.html          # Landing page
│   ├── register.html      # Face registration
│   ├── login.html         # Face authentication
│   ├── dashboard.html     # User dashboard
│   └── logs.html          # Authentication logs
├── static/                 # Static files (CSS, JS)
├── requirements.txt        # Python dependencies
├── setup_mysql.sql        # Database setup script
├── start_server.bat       # Windows startup script
└── README.md              # This file
```

## Configuration

### Face Recognition Settings

Edit `face_auth_project/settings.py`:

```python
# Face Recognition Settings
FACE_CONFIDENCE_THRESHOLD = 0.6  # Adjust for sensitivity (0.0-1.0)
FACE_CAPTURE_FRAMES = 25         # Number of frames to capture
LIVENESS_DETECTION = False       # Enable/disable liveness detection
```

### Session Settings

```python
# Session Configuration
SESSION_COOKIE_AGE = 1800        # 30 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

## Troubleshooting

### Common Issues

**Camera not working:**
- Allow camera permissions in browser
- Check if camera is being used by another application
- Try a different browser

**Database connection error:**
- Ensure MySQL server is running
- Verify credentials in `.env` file
- Check if `deepface` database exists

**Face not detected:**
- Ensure good lighting conditions
- Position face clearly in camera view
- Try different angles

**Low confidence scores:**
- Improve lighting
- Re-register with better positioning
- Ensure face is clearly visible

**Import errors:**
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Browser Compatibility

Recommended browsers:
- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

### Performance Tips

- Use good lighting for better face detection
- Keep face centered in camera view
- Move slowly during registration
- Ensure stable internet connection
- Close other applications using the camera

## Security Features

- **Face Encoding Encryption** - Face data is encoded and stored securely
- **Session Management** - Automatic session timeout and validation
- **IP Tracking** - Login attempts are logged with IP addresses
- **Confidence Thresholds** - Configurable authentication sensitivity
- **Browser Navigation Protection** - Prevents unauthorized access via browser history

## API Endpoints

### Authentication
- `POST /register_face/` - Register new user with face data
- `POST /authenticate_face/` - Authenticate user with face
- `POST /logout/` - Logout user

### Dashboard
- `GET /dashboard/` - User dashboard (requires authentication)
- `GET /logs/` - Authentication logs (requires authentication)

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) UNIQUE,
    face_encoding LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Recognition Logs Table
```sql
CREATE TABLE recognition_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    confidence FLOAT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

**Created by:**
- Jasper Ace N. Lapitan
- Christian Paul G. Cudal  
- Donn Franckie Whilliaem J. Licudine

## Acknowledgments

- **face_recognition** library for facial recognition capabilities
- **OpenCV** for computer vision processing
- **Django** web framework
- **Apple** for Face ID interface inspiration

## Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [Issues](https://github.com/Jasper-ace/DeepFace/issues) page
3. Create a new issue with detailed information

## Version History

- **v1.0.0** - Initial release with basic face recognition
- **v1.1.0** - Added Apple Face ID style interface
- **v1.2.0** - Implemented macOS-style dashboard
- **v1.3.0** - Enhanced security and session management

---

**⭐ Star this repository if you found it helpful!**