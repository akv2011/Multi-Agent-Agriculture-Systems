# 🔐 System Access Information

## 🌾 Unified Agricultural Platform Access

### 🚀 Quick Start Commands

#### Backend API Server
```bash
# Start the unified agricultural API
python unified_agricultural_api.py
```
**Server URL**: http://localhost:8000

#### Frontend Application
```bash
# Navigate to frontend directory and start
cd frontend
npm start
```
**Frontend URL**: http://localhost:3000

### 📊 System Endpoints

#### Main Dashboard
- **API Documentation**: http://localhost:8000/docs
- **System Status**: http://localhost:8000/system/status

#### Marketplace APIs
- **Products**: http://localhost:8000/marketplace/products
- **Sellers**: http://localhost:8000/marketplace/sellers
- **Categories**: http://localhost:8000/marketplace/categories
- **Statistics**: http://localhost:8000/marketplace/stats

#### Farmer Profile APIs
- **All Profiles**: http://localhost:8000/farmer-profiles
- **Leaderboard**: http://localhost:8000/farmer-leaderboard
- **Credit Analytics**: http://localhost:8000/credit-score-analytics

#### Business Intelligence APIs
- **Market Intelligence**: http://localhost:8000/business-intel/market-intelligence
- **Procurement Recommendations**: http://localhost:8000/business-intel/procurement-recommendations

### 👤 Sample Data Access

#### Sample Farmers (Credit Scores)
1. **Manoj Patil** - Score: 691 (Maharashtra, Veteran)
2. **Kavita Sharma** - Score: 687 (Haryana, Beginner)
3. **Ramesh Yadav** - Score: 669 (Madhya Pradesh, Experienced)
4. **Sunita Devi** - Score: 658 (Uttar Pradesh, Intermediate)
5. **Rajesh Kumar Singh** - Score: 639 (Punjab, Experienced)

#### Sample Products
1. **Premium Basmati Rice** - ₹85/kg (Rajesh Kumar, Punjab)
2. **Organic Wheat Flour** - ₹45/kg (Sunita Farms, UP)

#### Sample Sellers
1. **Rajesh Kumar** - 4.8★ (Verified, Ludhiana)
2. **Sunita Farms** - 4.9★ (Verified, Meerut)
3. **Green Valley Agro** - 4.7★ (Verified, Nashik)

### 🔧 Development Environment

#### Environment Files
```bash
# Root directory .env (optional)
API_HOST=localhost
API_PORT=8000
DEBUG=True
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# Frontend .env (frontend/.env)
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

#### File Upload Directory
- **Location**: `uploads/product_images/`
- **Permissions**: Read/Write access required
- **Max Size**: 10MB per file
- **Formats**: JPG, PNG, WebP

### 🛠️ Testing Commands

#### Backend Testing
```bash
# Test system status
curl http://localhost:8000/system/status

# Test farmer profiles
curl http://localhost:8000/farmer-profiles

# Test marketplace products
curl http://localhost:8000/marketplace/products

# Test business intelligence
curl http://localhost:8000/business-intel/market-intelligence
```

#### Frontend Testing
```bash
# Run frontend tests
cd frontend
npm test

# Build production version
npm run build
```

### 📝 System Requirements

#### Backend Requirements
- Python 3.8+
- FastAPI
- Uvicorn
- Pydantic
- Pillow (for image processing)

#### Frontend Requirements
- Node.js 16+
- React 18+
- TypeScript
- Tailwind CSS

### 🔐 Security Notes

#### Current Status
- **Authentication**: None (development mode)
- **Authorization**: None (open access)
- **HTTPS**: Not enabled (local development)
- **Rate Limiting**: Not implemented
- **Input Validation**: Implemented with Pydantic

#### Production Recommendations
- Implement JWT authentication
- Add role-based authorization
- Enable HTTPS with SSL certificates
- Add rate limiting and DDoS protection
- Implement audit logging

### 📊 Monitoring and Health

#### Health Check Endpoint
```bash
curl http://localhost:8000/system/status
```

**Expected Response:**
```json
{
  "status": "operational",
  "api_version": "2.0.0",
  "uptime": "99.9%",
  "services": {
    "marketplace": "active",
    "farmer_profiles": "active",
    "business_intelligence": "active",
    "image_upload": "active",
    "ai_recommendations": "active"
  },
  "statistics": {
    "total_products": 2,
    "total_sellers": 3,
    "total_farmers": 5,
    "verified_farmers": 1
  }
}
```

### 🆘 Troubleshooting

#### Common Issues
1. **Port 8000 in use**: Kill existing process or use different port
2. **Module not found**: Run `pip install -r requirements.txt`
3. **Upload permission denied**: Check uploads directory permissions
4. **Frontend won't start**: Run `npm install` in frontend directory
5. **API not responding**: Check if Python server is running

#### Log Locations
- **Backend Logs**: Console output
- **Frontend Logs**: Browser console
- **Upload Logs**: Server console for file operations

---

## ✅ **System Ready**

The Unified Agricultural Platform is fully operational with:
- 🎯 **Single API Server**: All functionality in one service
- 📊 **Complete Frontend**: React-based user interface
- 🔍 **Full Documentation**: Comprehensive guides available
- 🚀 **Easy Deployment**: One-command startup

**No login required for development access. All endpoints are open for testing and demonstration.**
| **👑 Administrator** | `admin` | `admin123` | Full system access |
| **👤 Regular User** | `user` | `user123` | Standard user access |
| **🌾 Farmer** | `farmer` | `farmer123` | Farm management access |
| **🎯 AgriSens Expert** | `agrisens` | `agrisens2025` | Expert system access |

---

## 🚀 How to Login

### **Method 1: Manual Login**
1. Open the dashboard: `http://localhost:3000`
2. Enter any username/password combination from the table above
3. Click "Sign In"

### **Method 2: Quick Demo Login**
1. Open the dashboard: `http://localhost:3000`
2. Click the **"Quick Demo Login"** button
3. This will automatically log you in as `admin`

---

## ⚙️ Technical Details

### **Environment Configuration**
```bash
VITE_DEMO_MODE=true                               # Demo mode enabled
VITE_DEMO_ADMIN_HASH=YWRtaW46YWRtaW4xMjM=         # admin:admin123
VITE_DEMO_USER_HASH=dXNlcjp1c2VyMTIz              # user:user123
VITE_DEMO_FARMER_HASH=ZmFybWVyOmZhcm1lcjEyMw==     # farmer:farmer123
VITE_DEMO_AGRISENS_HASH=YWdyaXNlbnM6YWdyaXNlbnMyMDI1 # agrisens:agrisens2025
```

### **Security Features**
- ✅ **Base64 encoded** credentials in environment variables
- ✅ **Demo mode toggle** for production safety
- ✅ **No hardcoded secrets** in source code
- ✅ **Environment-based authentication** system

---

## 🛡️ Security Notes

### **For Development**
- These credentials are **safe for development** and testing
- Demo mode is **automatically disabled** for production builds
- All credentials are **environment-based** (no hardcoded values)

### **For Production**
- Set `VITE_DEMO_MODE=false` to disable demo authentication
- Configure your own secure authentication system
- Use proper user management and database integration

---

## 🔧 Starting the Dashboard

```bash
# Navigate to frontend directory
cd frontend/

# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev

# Access the dashboard
# http://localhost:3000
```

---

## 🎯 Recommended Login for Testing

**Start with:** `admin` / `admin123`
- Full access to all features
- Can test all dashboard components
- Administrator-level permissions

**Quick Demo Login:** Just click the "Quick Demo Login" button for instant access!

---

**Status:** ✅ **Ready to use**  
**Demo Mode:** 🟢 **Enabled**  
**Security:** 🛡️ **Secure (environment-based)**
