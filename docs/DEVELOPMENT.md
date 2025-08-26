# 🛠️ Development Guide

## Getting Started

This guide provides comprehensive instructions for setting up, developing, and contributing to the Unified Agricultural Platform.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Ubuntu 18.04+
- **RAM**: Minimum 8GB, Recommended 16GB
- **Storage**: At least 10GB free space
- **Internet**: Stable internet connection for API integrations

### Software Dependencies
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **npm**: 8.0 or higher (comes with Node.js)
- **Git**: Latest version
- **Code Editor**: VS Code (recommended) or any preferred editor

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/akv2011/Multi-Agent-Agriculture-Systems.git
cd Multi-Agent-Agriculture-Systems
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file in the root directory:
```env
# API Configuration
API_HOST=localhost
API_PORT=8000
DEBUG=True

# Upload Configuration
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB

# Database Configuration (if using external DB)
DATABASE_URL=sqlite:///./agricultural_platform.db

# External API Keys (optional)
WEATHER_API_KEY=your_weather_api_key
SATELLITE_API_KEY=your_satellite_api_key
```

### 3. Frontend Setup

#### Navigate to Frontend Directory
```bash
cd frontend
```

#### Install Node.js Dependencies
```bash
npm install
```

#### Environment Configuration
Create a `.env` file in the frontend directory:
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## Development Workflow

### Starting the Development Environment

#### Start Backend Server
```bash
# From project root directory
python unified_agricultural_api.py
```
The API will be available at: http://localhost:8000

#### Start Frontend Development Server
```bash
# From frontend directory
npm start
```
The frontend will be available at: http://localhost:3000

### Development Commands

#### Backend Commands
```bash
# Run the unified API
python unified_agricultural_api.py

# Run individual components (for testing)
python farmer_profile_api.py        # Port 8003
python marketplace_api_standalone.py # Port 8001

# Run tests
python test_unified_system.py

# Check system health
curl http://localhost:8000/system/status
```

#### Frontend Commands
```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

## Project Structure

```
Multi-Agent-Agriculture-Systems/
├── README.md                          # Main project documentation
├── requirements.txt                   # Python dependencies
├── unified_agricultural_api.py        # Main API server
├── farmer_profile_api.py             # Farmer profile service
├── marketplace_api_standalone.py     # Marketplace service
├── test_unified_system.py            # System tests
├── create_placeholder_images.py      # Image generation utility
│
├── docs/                              # Documentation
│   ├── API.md                        # API documentation
│   ├── FARMER_CREDIT_SCORING.md      # Credit scoring guide
│   ├── MARKETPLACE.md                # Marketplace guide
│   ├── BUSINESS_INTELLIGENCE.md      # BI module guide
│   └── DEVELOPMENT.md                # This file
│
├── frontend/                          # React frontend
│   ├── package.json                  # Node.js dependencies
│   ├── src/                          # Source code
│   │   ├── components/               # React components
│   │   │   ├── AddProductPage.tsx    # Product addition form
│   │   │   ├── FarmerProfilePage.tsx # Farmer profiles
│   │   │   └── Layout.tsx            # App layout
│   │   ├── pages/                    # Page components
│   │   ├── utils/                    # Utility functions
│   │   └── App.tsx                   # Main app component
│   └── public/                       # Static assets
│
├── uploads/                           # File uploads directory
│   └── product_images/               # Product images
│
├── data/                             # Data storage
├── logs/                             # Application logs
├── scripts/                          # Utility scripts
└── tests/                            # Test files
```

## Architecture Overview

### Backend Architecture

#### FastAPI Application Structure
```python
# unified_agricultural_api.py structure
app = FastAPI(
    title="Unified Agricultural Platform API",
    description="Comprehensive agricultural platform",
    version="2.0.0"
)

# Core modules
- Marketplace API endpoints
- Farmer Profile API endpoints  
- Business Intelligence API endpoints
- File upload handling
- Data models and validation
- In-memory data storage
```

#### API Endpoint Organization
```
/system/status                        # System health
/marketplace/*                        # Marketplace operations
/farmer-profiles                      # Farmer management
/farmer-profile/{id}                  # Individual farmer data
/farmer-leaderboard                   # Credit score rankings
/business-intel/*                     # BI and analytics
```

### Frontend Architecture

#### React Component Structure
```tsx
App.tsx
├── Layout.tsx                        # Main layout wrapper
│   ├── Header                        # Navigation header
│   ├── Sidebar                       # Navigation sidebar
│   └── Main Content                  # Page content area
│
├── AddProductPage.tsx                # Product addition form
│   ├── ImageUpload                   # Multi-image upload
│   ├── ProductForm                   # Product details form
│   └── CategorySelector              # Category selection
│
└── FarmerProfilePage.tsx             # Farmer profiles dashboard
    ├── ProfileCards                  # Individual farmer cards
    ├── CreditScoreChart              # Score visualization
    ├── Leaderboard                   # Rankings table
    └── Analytics                     # Performance metrics
```

#### State Management
- **React Hooks**: useState, useEffect for local state
- **Context API**: Global state management (planned)
- **Local Storage**: Temporary data persistence
- **API Integration**: Fetch-based HTTP client

## Data Models

### Core Data Structures

#### Farmer Profile Model
```python
class FarmerProfile(BaseModel):
    farmer_id: str
    name: str
    phone: str
    location: Dict[str, str]
    farm_size_hectares: float
    primary_crops: List[str]
    farming_experience: FarmingExperience
    verification_status: VerificationStatus
    agriculture_credit_score: int
    score_category: CreditScoreCategory
    satellite_metrics: SatelliteMetrics
    crop_performance_history: List[CropPerformanceHistory]
    financial_history: FinancialHistory
    market_activity: MarketActivity
    technology_adoption: TechnologyAdoption
```

#### Product Model
```python
class Product(BaseModel):
    product_id: str
    name: str
    description: str
    category: str
    price: float
    unit: str
    stock: int
    seller: Seller
    images: List[str]
    is_organic: bool
    harvest_date: Optional[date]
    marketplace_type: str
    specifications: Dict[str, Any]
    created_at: datetime
```

#### Seller Model
```python
class Seller(BaseModel):
    seller_id: str
    name: str
    location: str
    contact: str
    rating: float
    verified: bool
    total_sales: int
    specialties: List[str]
    joined_date: date
```

## API Development

### Adding New Endpoints

#### 1. Define Data Models
```python
# Add to unified_agricultural_api.py
class NewDataModel(BaseModel):
    id: str
    name: str
    # ... other fields
```

#### 2. Create Endpoint
```python
@app.get("/new-endpoint")
async def get_new_data():
    """
    Get new data with proper documentation
    """
    try:
        # Implementation logic
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

#### 3. Add Error Handling
```python
from fastapi import HTTPException

@app.post("/new-endpoint")
async def create_new_data(data: NewDataModel):
    try:
        # Validation
        if not data.name:
            raise HTTPException(status_code=400, detail="Name is required")
        
        # Implementation
        result = process_data(data)
        return {"status": "success", "data": result}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Testing API Endpoints

#### Manual Testing
```bash
# Test with curl
curl -X GET http://localhost:8000/system/status
curl -X POST http://localhost:8000/marketplace/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Product", "price": 100}'
```

#### Automated Testing
```python
# test_new_endpoint.py
import requests

def test_new_endpoint():
    response = requests.get("http://localhost:8000/new-endpoint")
    assert response.status_code == 200
    assert "status" in response.json()
```

## Frontend Development

### Adding New Components

#### 1. Create Component File
```tsx
// src/components/NewComponent.tsx
import React, { useState, useEffect } from 'react';

interface NewComponentProps {
  data: any[];
  onUpdate: (item: any) => void;
}

const NewComponent: React.FC<NewComponentProps> = ({ data, onUpdate }) => {
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Component initialization
  }, []);

  return (
    <div className="new-component">
      {/* Component JSX */}
    </div>
  );
};

export default NewComponent;
```

#### 2. Add Styling
```css
/* src/styles/NewComponent.css */
.new-component {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
}
```

#### 3. Integration
```tsx
// src/App.tsx or parent component
import NewComponent from './components/NewComponent';

function App() {
  return (
    <div>
      <NewComponent data={data} onUpdate={handleUpdate} />
    </div>
  );
}
```

### API Integration

#### Fetch Wrapper Utility
```typescript
// src/utils/api.ts
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const apiClient = {
  async get(endpoint: string) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  },

  async post(endpoint: string, data: any) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  },

  async postFormData(endpoint: string, formData: FormData) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
};
```

## Testing

### Backend Testing

#### Unit Tests
```python
# test_farmer_profiles.py
import pytest
from unified_agricultural_api import calculate_agriculture_credit_score

def test_credit_score_calculation():
    # Create test farmer profile
    farmer = create_test_farmer()
    
    # Calculate credit score
    score = calculate_agriculture_credit_score(farmer)
    
    # Assertions
    assert 300 <= score <= 900
    assert isinstance(score, int)
```

#### Integration Tests
```python
# test_api_integration.py
import requests

def test_farmer_profile_api():
    # Test farmer profiles endpoint
    response = requests.get("http://localhost:8000/farmer-profiles")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
```

### Frontend Testing

#### Component Tests
```tsx
// src/components/__tests__/FarmerProfilePage.test.tsx
import { render, screen } from '@testing-library/react';
import FarmerProfilePage from '../FarmerProfilePage';

test('renders farmer profiles', () => {
  render(<FarmerProfilePage />);
  expect(screen.getByText('Farmer Profiles')).toBeInTheDocument();
});
```

#### Integration Tests
```tsx
// src/__tests__/App.integration.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import App from '../App';

test('loads and displays farmer data', async () => {
  render(<App />);
  
  await waitFor(() => {
    expect(screen.getByText('Farmer Profiles')).toBeInTheDocument();
  });
});
```

## Deployment

### Development Deployment

#### Local Development
```bash
# Terminal 1: Backend
python unified_agricultural_api.py

# Terminal 2: Frontend
cd frontend && npm start
```

#### Docker Development (Optional)
```dockerfile
# Dockerfile.backend
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "unified_agricultural_api.py"]
```

```dockerfile
# Dockerfile.frontend
FROM node:16
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
CMD ["npm", "start"]
```

### Production Deployment

#### Backend Production
```bash
# Install production dependencies
pip install gunicorn uvicorn

# Run with Gunicorn
gunicorn unified_agricultural_api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend Production
```bash
# Build production bundle
cd frontend
npm run build

# Serve with nginx or Apache
# Copy build/ directory to web server
```

## Code Quality

### Linting and Formatting

#### Python (Backend)
```bash
# Install tools
pip install black flake8 mypy

# Format code
black unified_agricultural_api.py

# Lint code
flake8 unified_agricultural_api.py

# Type checking
mypy unified_agricultural_api.py
```

#### TypeScript (Frontend)
```bash
# Install tools
npm install --save-dev eslint prettier @typescript-eslint/parser

# Lint code
npm run lint

# Format code
npm run prettier
```

### Code Review Guidelines

#### Backend Code Review
- ✅ Proper error handling with try/catch
- ✅ Input validation using Pydantic models
- ✅ Consistent API response format
- ✅ Docstrings for all functions
- ✅ Type hints for function parameters

#### Frontend Code Review
- ✅ TypeScript interfaces for props
- ✅ Proper component lifecycle management
- ✅ Error boundary implementation
- ✅ Accessibility attributes
- ✅ Responsive design considerations

## Troubleshooting

### Common Issues

#### Backend Issues
```bash
# Port already in use
Error: [Errno 48] Address already in use
Solution: Kill process using port or use different port

# Module not found
ModuleNotFoundError: No module named 'fastapi'
Solution: Install dependencies with pip install -r requirements.txt

# Permission denied for uploads
PermissionError: [Errno 13] Permission denied: 'uploads/'
Solution: Create uploads directory with proper permissions
```

#### Frontend Issues
```bash
# Node modules issues
Error: Cannot resolve dependency
Solution: Delete node_modules and run npm install

# API connection issues
TypeError: Failed to fetch
Solution: Check if backend is running and API_BASE_URL is correct

# Build failures
Error: Module build failed
Solution: Check TypeScript errors and fix them
```

### Debug Mode

#### Enable Debug Logging
```python
# unified_agricultural_api.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
print(f"Debug: Processing request for {endpoint}")
```

#### Frontend Debug Mode
```tsx
// Enable React development mode
const debug = process.env.NODE_ENV === 'development';

if (debug) {
  console.log('Debug: Component rendered with props:', props);
}
```

## Contributing

### Git Workflow

#### Branch Naming Convention
- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/critical-fix` - Critical fixes
- `docs/documentation-update` - Documentation updates

#### Commit Message Format
```
type(scope): brief description

Detailed explanation of changes made.

- Added new farmer credit scoring algorithm
- Updated API documentation
- Fixed image upload validation
```

#### Pull Request Process
1. Create feature branch from main
2. Implement changes with tests
3. Update documentation if needed
4. Submit pull request with description
5. Address review feedback
6. Merge after approval

### Development Standards

#### Code Style
- **Python**: Follow PEP 8 guidelines
- **TypeScript**: Use ESLint and Prettier
- **Comments**: Explain complex logic
- **Naming**: Use descriptive variable names

#### Documentation Standards
- **API**: Document all endpoints with examples
- **Components**: Document props and usage
- **Functions**: Include docstrings with parameters
- **README**: Keep setup instructions current

---

**This development guide provides the foundation for contributing to the Unified Agricultural Platform. For specific questions or issues, please refer to the project documentation or create an issue in the repository.**
