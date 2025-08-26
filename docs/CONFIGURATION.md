# Configuration System

Multi-Agent Agriculture Systems uses a unified configuration system to manage environment-specific settings and regional data. This approach improves security, maintainability, and deployment flexibility.

## Environment Configuration

### Backend Configuration

The backend uses `pydantic-settings` to load configuration from environment variables or `.env` files:

1. **Setup your environment**:
   - Copy `.env.example` to `.env` in the project root
   - Modify settings as needed (database URL, API keys, etc.)

2. **Configuration priorities**:
   - Environment variables (highest priority)
   - `.env` file
   - Default values in the code (lowest priority)

3. **Access settings**:
   - Import the config service: `from src.config import config_service`
   - Access settings: `config_service.get_database_url()`

### Frontend Configuration

The frontend uses Create React App's built-in environment variable support:

1. **Environment files**:
   - `.env.development` for local development
   - `.env.production` for production builds

2. **Configuration values**:
   - `REACT_APP_API_BASE_URL`: Backend API URL

3. **Usage in code**:
   - Access in React components: `process.env.REACT_APP_API_BASE_URL`
   - The centralized API client automatically uses this configuration

## Development vs. Production

Different environments use different configuration values:

### Development
```
DATABASE_URL=sqlite:///./data/agriculture.db
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Production
```
DATABASE_URL=postgresql://user:password@host:5432/agriculture_db
DEBUG=false
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

## Adding New Configuration Values

To add new configuration values:

1. Add the setting to `.env.example` with documentation
2. Add it to the `Settings` class in `src/config/settings.py` with appropriate type
3. Add a getter method in `ConfigService` if needed
4. Use `config_service` to access the value in your code
