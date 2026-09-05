# GPS Vehicle Tracking System - Backend

## Architecture
Flutter App → FastAPI → PostgreSQL
                ↑
         MQTT Broker ← GPS Simulator

## Tech Stack
- Python FastAPI
- PostgreSQL Database
- MQTT (Mosquitto Broker)
- Docker and Docker Compose
- GPS Simulator

## Database Design
- users - User accounts with route and vehicle assignment
- bus_routes - Bus routes with waypoints
- vehicles - Vehicle details
- gps_data - Historical GPS tracking data
- latest_locations - Latest GPS location per vehicle

## Setup and Run

### Requirements
- Docker
- Docker Compose

### Steps
git clone https://github.com/toufikbeg/vehicle-tracking-backend
cd vehicle-tracking-backend
docker-compose up -d --build
docker-compose exec backend python seed_data.py

## Test Users
Username: user_a | Password: password123 | Route: City Center to Airport | Vehicle: BUS-001
Username: user_b | Password: password123 | Route: University to Tech Park | Vehicle: BUS-002
Username: admin  | Password: admin123    | Role: Admin Only

## API Endpoints
POST   /api/auth/login          - Login and get token
GET    /api/auth/me             - Get current user
GET    /api/gps/dashboard       - Get full dashboard data
GET    /api/gps/current-location - Get latest GPS location
GET    /api/gps/history         - Get GPS history
POST   /api/gps/update          - Update GPS via REST
GET    /api/routes/my-route     - Get assigned route
GET    /api/vehicles/my-vehicle - Get assigned vehicle
POST   /api/routes/assign       - Admin - Assign route to user
POST   /api/vehicles/create     - Admin - Create new vehicle
POST   /api/routes/create       - Admin - Create new route

## Authentication
- JWT Token based authentication
- Token expires in 24 hours
- Bearer token required for protected endpoints
- Each user can only access their assigned route and vehicle
- Backend enforces route and vehicle authorization

## Route and Vehicle Assignment Logic
- Admin assigns route and vehicle to each user
- User A can only see Route A and BUS-001
- User B can only see Route B and BUS-002
- Assignment is enforced by the backend not the frontend
- Unauthorized access returns 403 Forbidden

## GPS Data Flow
GPS Simulator → MQTT Broker → Backend → PostgreSQL
                                ↓
                    Latest Location Table Updated
                                ↓
                    Flutter App Polls Every 5 Seconds

## MQTT Topic Format
Topic: vehicle/{vehicle_id}/gps
Payload:
{
  latitude: 12.9716,
  longitude: 77.5946,
  speed: 45.5,
  heading: 180.0,
  altitude: 920.0,
  timestamp: 2024-01-01T10:00:00Z
}

## Docker Services
backend      - Port 8000 - FastAPI Server
postgres     - Port 5432 - PostgreSQL Database
mqtt_broker  - Port 1883 - MQTT Broker
gps_simulator - Port -   - GPS Data Simulator

## API Documentation
http://localhost:8000/docs