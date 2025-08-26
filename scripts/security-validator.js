#!/usr/bin/env node

/**
 * Security Validator for Environment Variables
 * Checks for potential hardcoded secrets and insecure configurations
 */

const fs = require('fs');
const path = require('path');

// Patterns that indicate potential secrets (case-insensitive)
const SECRET_PATTERNS = [
  /password\s*[:=]\s*['"][^'"]+['"]/i,
  /api_?key\s*[:=]\s*['"][^'"]+['"]/i,
  /secret\s*[:=]\s*['"][^'"]+['"]/i,
  /token\s*[:=]\s*['"][^'"]+['"]/i,
  /private_?key\s*[:=]\s*['"][^'"]+['"]/i,
  /auth\s*[:=]\s*['"][^'"]+['"]/i,
  /credential\s*[:=]\s*['"][^'"]+['"]/i,
];

// Files to check for security issues
const FILES_TO_CHECK = [
  '.env',
  '.env.local',
  '.env.development',
  '.env.production', 
  'frontend/.env',
  'frontend/.env.local',
  'frontend/.env.development',
  'frontend/.env.production',
  'src/**/*.ts',
  'src/**/*.tsx',
  'frontend/src/**/*.ts',
  'frontend/src/**/*.tsx'
];

// Safe placeholder patterns (these are OK)
const SAFE_PATTERNS = [
  /your_.*_here/i,
  /replace_with_/i,
  /example_/i,
  /placeholder/i,
  /\$\{.*\}/,  // Environment variable substitution
  /process\.env\./,  // Environment variable access
  /import\.meta\.env\./,  // Vite environment variables
];

function checkFile(filePath) {
  if (!fs.existsSync(filePath)) {
    return { safe: true, issues: [] };
  }

  const content = fs.readFileSync(filePath, 'utf8');
  const issues = [];

  // Check each line for potential secrets
  const lines = content.split('\n');
  lines.forEach((line, index) => {
    SECRET_PATTERNS.forEach(pattern => {
      if (pattern.test(line)) {
        // Check if it's a safe placeholder
        const isSafe = SAFE_PATTERNS.some(safePattern => safePattern.test(line));
        
        if (!isSafe) {
          issues.push({
            line: index + 1,
            content: line.trim(),
            pattern: pattern.toString(),
            severity: 'HIGH'
          });
        }
      }
    });
  });

  return {
    safe: issues.length === 0,
    issues
  };
}

function validateProject() {
  console.log('🔍 AgriMitr Security Validator');
  console.log('=============================');
  console.log('Checking for potential hardcoded secrets...\n');

  let totalIssues = 0;
  const results = {};

  // Check specific files
  const specificFiles = [
    '.env',
    'frontend/.env',
    'frontend/src/contexts/AuthContext.tsx',
    'frontend/src/components/LoginPage.tsx',
    'frontend/src/utils/authUtils.ts'
  ];

  specificFiles.forEach(file => {
    const result = checkFile(file);
    results[file] = result;
    
    if (result.issues.length > 0) {
      console.log(`❌ ${file}:`);
      result.issues.forEach(issue => {
        console.log(`   Line ${issue.line}: ${issue.content}`);
        console.log(`   Pattern: ${issue.pattern}`);
        console.log(`   Severity: ${issue.severity}\n`);
        totalIssues++;
      });
    } else {
      console.log(`✅ ${file}: Clean`);
    }
  });

  console.log('\n=============================');
  console.log(`📊 Security Scan Results:`);
  console.log(`Files checked: ${specificFiles.length}`);
  console.log(`Issues found: ${totalIssues}`);
  
  if (totalIssues === 0) {
    console.log('🛡️  Security Status: SECURE');
    console.log('✅ No hardcoded secrets detected');
  } else {
    console.log('🚨 Security Status: ISSUES DETECTED');
    console.log('❌ Please review and fix the issues above');
  }

  return totalIssues === 0;
}

// Run validation
if (require.main === module) {
  const isSecure = validateProject();
  process.exit(isSecure ? 0 : 1);
}

module.exports = { validateProject, checkFile };
