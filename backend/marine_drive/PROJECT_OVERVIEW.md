# Marine Drive - Embedded Intelligent Microscopy System

## Project Overview

Marine Drive is a comprehensive web application backend for an **Embedded Intelligent Microscopy System** designed for identification and counting of microscopic marine organisms. The system integrates live microscope feeds with machine learning models to provide real-time organism detection, classification, and analysis.

## System Architecture

### Backend (Django): `marine_drive`
- **Framework**: Django 4.2 with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Real-time Communication**: Django Channels for WebSocket support
- **API**: RESTful API for frontend communication

### Frontend (Planned): Next.js
- **Framework**: Next.js for modern React-based frontend
- **Real-time Features**: WebSocket integration for live feeds
- **Data Visualization**: Charts and graphs for organism analysis

### Edge Device: Raspberry Pi
- **ML Model**: Real-time organism detection and classification
- **Camera Integration**: Phone camera connected to microscope
- **Communication**: HTTP/WebSocket API calls to Django backend

## Key Features & Problems Solved

### 1. Fisheries & Aquaculture
- **Automated Plankton Monitoring**: Real-time detection of fish food sources
- **Feeding Optimization**: Prevents overstocking/underfeeding by predicting food availability
- **Harmful Algal Bloom Detection**: Early warning system for fish farm protection

### 2. Marine Ecology & Conservation
- **Biodiversity Tracking**: Automated identification of microscopic organisms
- **Ecosystem Health Monitoring**: Tracks changes in marine microorganism populations
- **Blockchain Registry**: Secure storage of biodiversity data for researchers
- **Climate Change Detection**: Monitors population shifts due to environmental changes

### 3. Scientific Research
- **Automated Analysis**: Reduces manual microscope work for marine biologists
- **Large-scale Datasets**: Provides real-time data for ecological modeling
- **Global Collaboration**: Open datasets for worldwide research communities
- **Food Chain Dynamics**: Understanding microscopic level ecosystem interactions

### 4. Public Health & Safety
- **Toxic Plankton Detection**: Early warning for red tide events
- **Seafood Safety**: Protects consumers from contaminated marine products
- **Real-time Alerts**: Immediate notifications for harmful organism detection

### 5. Smart Automation & Efficiency
- **24/7 Monitoring**: Continuous analysis without human intervention
- **Cost Reduction**: Automated system reduces monitoring program costs
- **High Accuracy**: ML-based identification reduces human error

### 6. Climate & Environmental Monitoring
- **Carbon Sink Tracking**: Monitors marine microorganisms' role in carbon cycle
- **Environmental Stress Detection**: Identifies pollution and climate impacts
- **Ocean Health Assessment**: Real-time environmental parameter monitoring

## Database Schema

### Core Apps and Models

#### 1. Organisms App
- **TaxonomyRank**: Hierarchical classification system (Kingdom → Species)
- **MarineOrganism**: Complete organism database with taxonomic information
- **OrganismDetectionProfile**: ML model parameters and detection statistics

#### 2. Detection App
- **DetectionSession**: Microscope analysis sessions with environmental data
- **DetectionResult**: Individual organism detections with ML confidence scores
- **LiveDetectionAlert**: Real-time alerts for harmful organisms or unusual concentrations
- **DetectionStatistics**: Aggregated analytics for sessions

#### 3. Analysis App
- **AnalysisReport**: Comprehensive analysis reports for research
- **BiodiversityAnalysis**: Detailed biodiversity assessments
- **EnvironmentalCorrelation**: Environmental factor analysis
- **TrendAnalysis**: Temporal population trend analysis
- **ComparativeAnalysis**: Cross-location/time comparisons

#### 4. Streaming App
- **StreamingConfiguration**: Video streaming settings and parameters
- **LiveStream**: Active streaming sessions with quality metrics
- **StreamViewer**: User viewing sessions and interaction tracking
- **StreamRecording**: Recorded sessions for later analysis

#### 5. Users App
- **UserProfile**: Extended profiles for marine research professionals
- **ResearchGroup**: Collaborative research teams and data sharing
- **UserActivityLog**: Activity tracking and audit trails
- **UserNotification**: In-app notification system

## API Endpoints

### Organisms API (`/api/organisms/`)
- `GET /` - List organisms with filtering
- `POST /` - Create new organism
- `GET /<id>/` - Get organism details
- `POST /search/` - Advanced organism search
- `GET /statistics/` - Database statistics
- `GET /taxonomy/` - Taxonomy hierarchy
- `GET /detection-profiles/` - ML detection profiles

### Detection API (`/api/detection/`)
- `GET /sessions/` - List detection sessions
- `POST /sessions/` - Start new session
- `GET /sessions/<id>/` - Session details
- `POST /sessions/<id>/end/` - End session
- `GET /results/` - List detection results
- `POST /results/` - Create detection result
- `POST /results/bulk-create/` - Bulk create from ML model
- `POST /results/<id>/verify/` - Verify detection
- `GET /alerts/` - Live alerts
- `GET /trends/` - Detection trends

### Analysis API (`/api/analysis/`)
- Coming soon: Report generation and analysis endpoints

### Streaming API (`/api/streaming/`)
- Coming soon: Live streaming and recording endpoints

### Users API (`/api/users/`)
- Coming soon: User management and profile endpoints

## Data Flow

### 1. Live Detection Process
```
Microscope → Phone Camera → Raspberry Pi ML Model → Django API → Next.js Frontend
```

### 2. Detection Session Workflow
1. **Session Start**: User creates detection session with sample metadata
2. **Live Feed**: Raspberry Pi streams video and detection results
3. **Real-time Analysis**: ML model identifies organisms and sends to API
4. **Alert System**: Automatic alerts for harmful organisms or unusual concentrations
5. **Session End**: Calculate statistics and generate summary report

### 3. Data Analysis Pipeline
1. **Raw Detection Data**: Individual organism detections with confidence scores
2. **Statistical Analysis**: Aggregation by taxonomy, location, time
3. **Trend Analysis**: Population changes over time
4. **Environmental Correlation**: Link organism presence to environmental factors
5. **Report Generation**: Comprehensive analysis reports for researchers

## Environmental Data Integration

The system captures and analyzes environmental parameters:
- **Water Temperature** (°C)
- **Salinity** (PSU - Practical Salinity Units)
- **pH Level** (0-14 scale)
- **Dissolved Oxygen** (mg/L)
- **Sample Depth** (meters)
- **Geographic Coordinates** (GPS)

## Machine Learning Integration

### Detection Profile System
- **Confidence Thresholds**: Customizable per organism
- **Accuracy Tracking**: False positive/negative rates
- **Model Versioning**: Track ML model updates
- **Feature Storage**: Visual characteristics for model training

### Real-time Processing
- **Frame Analysis**: Process video frames at configurable intervals
- **Batch Detection**: Bulk API endpoints for ML model results
- **Quality Metrics**: Track detection accuracy and system performance

## Security & Authentication

- **Token Authentication**: REST API security
- **User Permissions**: Role-based access control
- **Data Ownership**: Users control their detection sessions
- **Group Collaboration**: Shared research group access

## Development Setup

### Requirements
- Python 3.8+
- Django 4.2
- PostgreSQL (production) / SQLite (development)
- Redis (for WebSocket channels)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd marine_drive

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Database Migration
```bash
# Create migrations for all apps
python manage.py makemigrations organisms detection analysis streaming users

# Apply migrations
python manage.py migrate
```

## Production Deployment

### Environment Variables
- `DEBUG`: Set to `False` for production
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection for channels
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Recommended Stack
- **Web Server**: Nginx
- **WSGI Server**: Gunicorn
- **Database**: PostgreSQL
- **Cache/Channels**: Redis
- **File Storage**: AWS S3 or similar for media files

## Future Enhancements

### Phase 2 Features
1. **Advanced Analytics**: Machine learning for population prediction
2. **Mobile App**: React Native app for field researchers
3. **IoT Integration**: Environmental sensors for automated data collection
4. **Blockchain Registry**: Decentralized biodiversity data storage
5. **Global Dashboard**: Worldwide marine organism monitoring
6. **AI Recommendations**: Intelligent alerts and recommendations

### Research Collaborations
- **Open Data Initiative**: Global dataset sharing platform
- **Academic Partnerships**: Integration with research institutions
- **Citizen Science**: Community-contributed data collection
- **Environmental Agencies**: Government monitoring integration

## API Documentation

Detailed API documentation is available at `/api/docs/` when running the development server. The API uses OpenAPI 3.0 specification with interactive documentation.

## Support & Contribution

For technical support, feature requests, or contributions, please refer to the project repository documentation and issue tracker.

---

**Marine Drive** - Advancing marine science through intelligent automation and real-time organism detection.