# Marine Drive API Testing Guide

## Server Information
- **Development Server**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin
- **API Root**: http://localhost:8000/api/

## Authentication
- **Admin User**: admin / admin123
- **API Authentication**: Token-based or Session-based

## Available Endpoints

### 1. Organisms API (`/api/organisms/`)

#### List all organisms
```bash
curl -X GET http://localhost:8000/api/organisms/
```

#### Get organism details
```bash
curl -X GET http://localhost:8000/api/organisms/1/
```

#### Search organisms
```bash
curl -X POST http://localhost:8000/api/organisms/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Alexandrium", "is_harmful": true}'
```

#### Get organism statistics
```bash
curl -X GET http://localhost:8000/api/organisms/statistics/
```

#### Get taxonomy hierarchy
```bash
curl -X GET http://localhost:8000/api/organisms/taxonomy/hierarchy/
```

### 2. Detection API (`/api/detection/`)

#### Create a new detection session
```bash
curl -X POST http://localhost:8000/api/detection/sessions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "sample_location": "Pacific Ocean - Monterey Bay",
    "sample_volume": 10.0,
    "water_temperature": 18.5,
    "salinity": 34.2,
    "ph_level": 8.1,
    "sample_coordinates_lat": 36.8023,
    "sample_coordinates_lng": -121.8017,
    "microscope_magnification": "400x"
  }'
```

#### List detection sessions
```bash
curl -X GET http://localhost:8000/api/detection/sessions/ \
  -H "Authorization: Token YOUR_TOKEN"
```

#### Create detection results (from ML model)
```bash
curl -X POST http://localhost:8000/api/detection/results/bulk-create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "session_id": "SESSION_UUID",
    "detections": [
      {
        "session": 1,
        "organism": 1,
        "confidence_score": 0.92,
        "frame_number": 1500,
        "bbox_x": 0.25,
        "bbox_y": 0.35,
        "bbox_width": 0.15,
        "bbox_height": 0.20,
        "measured_size": 28.5,
        "features_json": {
          "circularity": 0.85,
          "area": 1250.5,
          "perimeter": 125.8
        }
      }
    ]
  }'
```

#### Get detection trends
```bash
curl -X GET "http://localhost:8000/api/detection/trends/?days=7" \
  -H "Authorization: Token YOUR_TOKEN"
```

### 3. Admin Interface Testing

Visit http://localhost:8000/admin and log in with:
- Username: admin
- Password: admin123

You can:
- View and manage marine organisms
- Browse detection sessions and results
- Manage user accounts and permissions
- View system statistics

## Sample Data Available

The system has been populated with sample data including:

### Taxonomy Hierarchy
- Kingdom: Protista, Plantae
- Phylum: Dinoflagellata, Bacillariophyta, Chlorophyta
- Genera: Peridinium, Alexandrium, Thalassiosira

### Sample Organisms
1. **Peridinium cinctum** (Banded Peridinium)
   - Size: 25-45 μm
   - Non-harmful primary producer
   - Freshwater dinoflagellate

2. **Alexandrium tamarense** (Alexandrium)
   - Size: 18-32 μm
   - **HARMFUL** - Causes paralytic shellfish poisoning
   - Marine dinoflagellate, red tide species

3. **Thalassiosira pseudonana** (Thalassiosira Diatom)
   - Size: 4-6 μm
   - Important carbon sequestration organism
   - Marine diatom

## Testing Workflow

### 1. Basic API Testing
```bash
# Test organisms endpoint
curl http://localhost:8000/api/organisms/

# Test taxonomy endpoint
curl http://localhost:8000/api/organisms/taxonomy/

# Test statistics
curl http://localhost:8000/api/organisms/statistics/
```

### 2. Authentication Testing
```bash
# Get authentication token
curl -X POST http://localhost:8000/api/auth/login/ \
  -d "username=admin&password=admin123"

# Use token for authenticated requests
curl -X GET http://localhost:8000/api/detection/sessions/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### 3. Complete Detection Workflow
1. Create a detection session
2. Add detection results (simulate ML model output)
3. Verify detections
4. End session and view statistics
5. Generate trends and analysis

## Error Handling

The API returns standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request (validation errors)
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include detailed information:
```json
{
  "error": "Validation failed",
  "details": {
    "confidence_score": ["This field must be between 0 and 1"]
  }
}
```

## Next Steps for Frontend Integration

### For Next.js Frontend:
1. **API Client Setup**: Create API service modules for each endpoint
2. **Authentication**: Implement token-based authentication
3. **Real-time Updates**: Use WebSocket connections for live detection feeds
4. **Data Visualization**: Charts for organism statistics and trends
5. **User Management**: Login, registration, and profile management
6. **Live Streaming**: WebRTC integration for microscope video feeds

### For Raspberry Pi ML Model:
1. **Detection Integration**: Use bulk-create endpoints for ML results
2. **Session Management**: Automatic session creation and management
3. **Real-time Alerts**: Trigger alerts for harmful organisms
4. **Image Storage**: Upload detection images and cropped organism photos
5. **Environmental Sensors**: Submit environmental data with detections

## Performance Considerations

- Use pagination for large datasets
- Implement caching for frequently accessed data
- Optimize database queries with select_related/prefetch_related
- Consider Redis for real-time features and session storage
- Use background tasks for heavy analysis operations

## Security Notes

- Always use HTTPS in production
- Implement proper CORS settings for frontend
- Use environment variables for sensitive settings
- Regularly update dependencies
- Implement rate limiting for API endpoints
- Validate and sanitize all input data

---

The Marine Drive API is now fully functional and ready for frontend integration and ML model deployment!