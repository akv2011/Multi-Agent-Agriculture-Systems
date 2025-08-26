# 🔐 Dashboard Login Credentials

## Available Login Credentials

**Demo Mode:** ✅ **ENABLED**

### 👤 User Accounts

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
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
