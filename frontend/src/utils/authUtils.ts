// Auth utilities for secure credential handling
interface DemoCredentials {
  [key: string]: string;
}

interface UserRole {
  role: string;
}

const USER_ROLES: { [key: string]: UserRole } = {
  admin: { role: 'Administrator' },
  user: { role: 'User' },
  farmer: { role: 'Farmer' },
  agrisens: { role: 'AgriSens Expert' }
};

/**
 * Decode base64 credential hash
 * @param hash - Base64 encoded username:password string
 * @returns Object with username and password
 */
const decodeCredentialHash = (hash: string): { username: string; password: string } | null => {
  try {
    const decoded = atob(hash);
    const [username, password] = decoded.split(':');
    return username && password ? { username, password } : null;
  } catch {
    return null;
  }
};

/**
 * Get demo credentials from environment variables
 * Only used in development/demo mode
 */
export const getDemoCredentials = (): DemoCredentials => {
  const credentials: DemoCredentials = {};
  
  // Only load demo credentials if in demo mode
  if (import.meta.env.VITE_DEMO_MODE !== 'true') {
    return credentials;
  }

  // Load credentials from environment variables
  const envHashes = {
    admin: import.meta.env.VITE_DEMO_ADMIN_HASH,
    user: import.meta.env.VITE_DEMO_USER_HASH,
    farmer: import.meta.env.VITE_DEMO_FARMER_HASH,
    agrisens: import.meta.env.VITE_DEMO_AGRISENS_HASH
  };

  Object.entries(envHashes).forEach(([username, hash]) => {
    if (hash) {
      const decoded = decodeCredentialHash(hash);
      if (decoded && decoded.username === username) {
        credentials[username] = decoded.password;
      }
    }
  });

  return credentials;
};

/**
 * Validate demo credentials
 * @param username - Username to validate
 * @param password - Password to validate
 * @returns User role if valid, null if invalid
 */
export const validateDemoCredentials = (username: string, password: string): string | null => {
  const credentials = getDemoCredentials();
  
  if (credentials[username] === password && USER_ROLES[username]) {
    return USER_ROLES[username].role;
  }
  
  return null;
};

/**
 * Check if demo mode is enabled
 */
export const isDemoMode = (): boolean => {
  return import.meta.env.VITE_DEMO_MODE === 'true';
};
