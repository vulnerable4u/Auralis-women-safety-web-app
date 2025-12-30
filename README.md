# Women Safety Assistant

A comprehensive, real-time women safety application with threat monitoring, emergency SOS, AI-powered safety guidance, and trusted contact management. Built with modern web technologies for reliability and ease of use.

## 🌟 Features

### Core Safety Features
- **Real-time Threat Monitoring** - Continuous assessment combining motion and audio analysis
- **One-Click SOS Emergency** - Instant alert system with location sharing to all emergency contacts
- **AI Safety Chatbot** - Intelligent assistant providing safety recommendations and emergency guidance
- **Trusted Contact Management** - Securely store and manage up to 10 emergency contacts

### Technical Features
- **Dual-Camera Support** - Server-rendered stream for desktop, dual camera for mobile
- **Interactive Safe Places Map** - Find nearby police stations, hospitals, and safe zones
- **Real-time Analytics** - Live threat visualization with historical charts
- **Comprehensive Logging** - Color-coded event logging with severity levels

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Webcam for video features
- Modern browser with geolocation support

### Installation

```bash
# Navigate to project directory
cd WOMEN-SAFETY-APP

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies (uses virtual environment to avoid externally-managed-environment error)
pip install -r requirements.txt

# Start the server
python server_backend.py

# Open in browser
# http://127.0.0.1:5000
```

> **Note:** If you encounter the `externally-managed-environment` error, this is because Python 3.12+ enforces PEP 668 which prevents pip from installing packages system-wide. Always activate the virtual environment (`source venv/bin/activate`) before running pip commands, or use the provided build scripts:
> ```bash
> # For local development
> ./run.sh
>
> # For Render deployment, use the build and start commands in Procfile
> ```

### Default Access
- **Admin Dashboard**: `admin` / `admin`
- **User Registration**: Available on first visit

## 📱 User Guide

### Setting Up Your Account

1. **First Launch**
   - You'll be redirected to the registration page
   - Create your account with a username and secure password

2. **Emergency Contacts Setup** (Required)
   - Add **minimum 4 trusted contacts**
   - Include name, India mobile number (+91), and relationship
   - Optional: email address for additional notification

3. **Dashboard Overview**
   - View real-time threat level indicator
   - Access SOS emergency button
   - Interact with safety chatbot
   - Explore nearby safe places on the map

### Using Safety Features

#### Threat Monitoring
- Click "Start Monitoring" to begin
- View live threat score (0-100)
- Monitor speech and motion detection levels
- Threat levels: SAFE → LOW → MEDIUM → HIGH → CRITICAL

#### Emergency SOS
- Red SOS button for instant emergencies
- Triggers CRITICAL threat level
- Notifies all emergency contacts with your location
- Logs event with timestamp

#### Safe Places Map
- Automatically detects your location
- Shows nearby safe places within 5km
- Color-coded markers:
  - 🏥 Hospitals (green)
  - 🚔 Police stations (blue)
  - 🛡️ Safe zones (purple)

#### AI Safety Chatbot
- Click the floating chatbot widget
- Ask for safety recommendations
- Get nearest emergency service directions
- Learn emergency procedures

### Admin Dashboard
- View all registered users
- Monitor system activity
- Manage user accounts

## 🔐 Security & Privacy

### Data Protection
- Passwords are securely hashed using Werkzeug
- Emergency contacts are encrypted at rest
- Session-based authentication with secure cookies

### Privacy Commitment
- Your location is never stored permanently
- Emergency contacts are only notified during SOS events
- All data stays on your local server
- No third-party data sharing

### Security Recommendations (Production)
- Change the Flask secret key in `server_backend.py`
- Use HTTPS in production
- Implement rate limiting for API endpoints
- Use environment variables for sensitive config

## 🛠️ Technical Architecture

### Backend Stack
- **Flask** - Web framework
- **OpenCV** - Camera and video processing
- **Werkzeug** - Security and password hashing

### Frontend Stack
- **HTML5/CSS3** - Modern responsive design
- **Vanilla JavaScript** - Interactive features
- **Chart.js** - Real-time threat visualization
- **Leaflet** - Interactive maps
- **Font Awesome** - Icons

### Project Structure
```
WOMEN-SAFETY-APP/
├── server_backend.py         # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── templates/                # HTML templates
│   ├── index.html           # Main dashboard
│   ├── login.html           # User login
│   ├── onboarding.html      # Contact setup
│   └── admin.html           # Admin dashboard
├── static/                   # Static assets
│   ├── css/                 # Stylesheets
│   └── js/                  # JavaScript modules
├── src/                      # Core modules
│   ├── threat_assessment/   # Threat analysis
│   ├── map_integration/     # Safe places
│   ├── motion_detection/    # Motion analysis
│   └── speech_analysis/     # Audio processing
├── config/                   # Configuration
└── data/                     # Data storage
```

## 📡 API Reference

### Public Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main dashboard |
| GET | `/video_feed` | MJPEG video stream |
| GET | `/api/threat_status` | Current threat status |
| GET | `/api/safe_places` | Nearby safe places |

### Authenticated Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/start_monitoring` | Start threat monitoring |
| POST | `/api/stop_monitoring` | Stop monitoring |
| POST | `/api/trigger_sos` | Trigger emergency SOS |

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/login` | User login |
| GET/POST | `/register` | User registration |
| GET | `/logout` | End session |

## 🔧 Configuration

### Emergency Services
Edit `config/emergency_config.json`:
```json
{
    "emergency_numbers": ["100", "112", "1091"],
    "sms_template": "EMERGENCY! I need help. Location: {location}",
    "call_delay": 30
}
```

### Safe Places
Edit `config/safe_places_config.json`:
```json
{
    "search_radius_km": 5,
    "place_types": ["hospital", "police", "fire_station"]
}
```

## 🔮 Future Enhancements

- [ ] ML-powered emotion detection
- [ ] Push notifications for mobile
- [ ] Integration with real maps API (Google/Apple)
- [ ] Database migration (SQLite/PostgreSQL)
- [ ] Two-factor authentication
- [ ] Voice-triggered SOS commands
- [ ] Wearable device integration

## 🐛 Troubleshooting

### Camera Issues
- Check webcam is connected and not in use
- Ensure browser has camera permissions
- App shows placeholder if camera unavailable

### Location Not Detected
- Enable browser location access
- Check device GPS/location services
- Uses default location if unavailable

### Map Not Loading
- Verify internet connection
- Check OpenStreetMap accessibility
- CDN required for Leaflet maps

## 📄 License

This project is created for educational purposes as a Final Year Project.

## 🤝 Support

For questions or issues:
- Review the documentation
- Check troubleshooting section
- Contact the development team

---

**Built with ❤️ for Women's Safety**

*Your safety is our priority.*

