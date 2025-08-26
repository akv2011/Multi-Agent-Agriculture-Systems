# Environment Configuration

This project uses environment-based configuration for both the backend and frontend.

## Backend Configuration

Backend configuration is managed through a centralized settings system using `pydantic-settings`. The settings are defined in `src/config/settings.py` and exposed through a `ConfigService` in `src/config/service.py`.

### Setting up the Backend Environment

1. Copy `.env.example` to `.env` in the project root directory
2. Update the values in `.env` as needed for your environment

### Available Settings

- `API_HOST`: Host for the API server
- `API_PORT`: Port for the API server
- `API_PREFIX`: URL prefix for API endpoints
- `DEBUG`: Enable debug mode (true/false)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)
- `DATABASE_URL`: SQLite database URL
- `REDIS_HOST`: Redis host
- `REDIS_PORT`: Redis port
- `REDIS_DB`: Redis database number
- `WEBSOCKET_HOST`: WebSocket host
- `WEBSOCKET_PORT`: WebSocket port

## Frontend Configuration

Frontend configuration is managed through environment variables and a centralized config object in `frontend/src/config/index.ts`.

### Setting up the Frontend Environment

1. For development, copy `frontend/.env.example` to `frontend/.env.development`
2. For production, copy `frontend/.env.example` to `frontend/.env.production`
3. For staging, copy `frontend/.env.example` to `frontend/.env.staging`
4. Update the values in each file based on the specific environment

### Environment-Specific Builds

- Development: Run `npm run dev` (uses `.env.development`)
- Staging: Run `npm run build:staging` (uses `.env.staging`)
- Production: Run `npm run build:production` (uses `.env.production`)

### Available Settings

- `REACT_APP_API_BASE_URL`: Base URL for API requests
- `REACT_APP_WEBSOCKET_URL`: WebSocket URL for real-time communication
- `REACT_APP_ENABLE_SATELLITE_VISUALIZATION`: Enable satellite visualization features
- `REACT_APP_ENABLE_MULTILINGUAL_SUPPORT`: Enable multilingual support
- `REACT_APP_ANALYTICS_KEY`: Analytics key (optional)

## Environment Files

- `.env`: Main environment file for the backend
- `.env.example`: Example backend environment file with default values
- `frontend/.env`: Main environment file for the frontend
- `frontend/.env.development`: Development-specific frontend environment settings
- `frontend/.env.production`: Production-specific frontend environment settings (when built)

## Usage in Code

### Backend

```python
from src.config import settings

# Access settings
api_host = settings.api_host
api_port = settings.api_port
```

### Frontend

```typescript
import config from '../config';

// Access API URL
const apiUrl = config.api.baseUrl;

// Access WebSocket URL
const wsUrl = config.websocket.url;

// Check feature flags
const satelliteEnabled = config.features.enableSatelliteVisualization;
```
