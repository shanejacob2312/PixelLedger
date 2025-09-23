#!/usr/bin/env node

/**
 * PixelLedger Unified Start Script
 * 
 * This script starts both frontend and backend servers.
 * Works on Windows, macOS, and Linux.
 * 
 * Usage:
 *   node start.js
 *   npm start
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkDependencies() {
  log('🔍 Checking dependencies...', 'cyan');
  
  // Check if backend directory exists
  if (!fs.existsSync('backend')) {
    log('❌ Backend directory not found', 'red');
    process.exit(1);
  }
  
  // Check if frontend directory exists
  if (!fs.existsSync('frontend')) {
    log('❌ Frontend directory not found', 'red');
    process.exit(1);
  }
  
  // Check if backend requirements.txt exists
  if (!fs.existsSync('backend/requirements.txt')) {
    log('❌ Backend requirements.txt not found', 'red');
    process.exit(1);
  }
  
  // Check if frontend package.json exists
  if (!fs.existsSync('frontend/package.json')) {
    log('❌ Frontend package.json not found', 'red');
    process.exit(1);
  }
  
  log('✅ All required files found', 'green');
}

function startBackend() {
  log('🔧 Starting backend server...', 'blue');
  
  const isWindows = process.platform === 'win32';
  const backendDir = path.join(process.cwd(), 'backend');
  
  let command, args;
  
  if (isWindows) {
    // Windows: activate virtual environment and run server
    command = 'cmd';
    args = ['/c', 'venv\\Scripts\\activate.bat', '&&', 'python', 'run_server.py'];
  } else {
    // Unix/Linux/macOS: activate virtual environment and run server
    command = 'bash';
    args = ['-c', 'source venv/bin/activate && python run_server.py'];
  }
  
  const backendProcess = spawn(command, args, {
    cwd: backendDir,
    stdio: 'inherit',
    shell: true
  });
  
  backendProcess.on('error', (error) => {
    log(`❌ Backend error: ${error.message}`, 'red');
  });
  
  return backendProcess;
}

function startFrontend() {
  log('🎨 Starting frontend server...', 'magenta');
  
  const frontendDir = path.join(process.cwd(), 'frontend');
  
  const frontendProcess = spawn('npm', ['start'], {
    cwd: frontendDir,
    stdio: 'inherit',
    shell: true
  });
  
  frontendProcess.on('error', (error) => {
    log(`❌ Frontend error: ${error.message}`, 'red');
  });
  
  return frontendProcess;
}

function cleanup(backendProcess, frontendProcess) {
  log('\n🛑 Stopping servers...', 'yellow');
  
  if (backendProcess) {
    backendProcess.kill('SIGTERM');
  }
  
  if (frontendProcess) {
    frontendProcess.kill('SIGTERM');
  }
  
  log('✅ Servers stopped', 'green');
  process.exit(0);
}

function main() {
  log('🚀 Starting PixelLedger Development Environment...', 'bright');
  log('==================================================', 'cyan');
  
  checkDependencies();
  
  // Start backend first
  const backendProcess = startBackend();
  
  // Wait a moment for backend to initialize
  setTimeout(() => {
    const frontendProcess = startFrontend();
    
    log('\n🎉 Development servers started!', 'green');
    log('==================================================', 'cyan');
    log('📱 Frontend: http://localhost:3000', 'blue');
    log('🔧 Backend API: http://localhost:8000', 'blue');
    log('📚 API Docs: http://localhost:8000/docs', 'blue');
    log('🔍 Health Check: http://localhost:8000/api/health', 'blue');
    log('\nPress Ctrl+C to stop both servers', 'yellow');
    
    // Handle cleanup on exit
    process.on('SIGINT', () => cleanup(backendProcess, frontendProcess));
    process.on('SIGTERM', () => cleanup(backendProcess, frontendProcess));
    
    // Keep the process alive
    process.on('exit', () => cleanup(backendProcess, frontendProcess));
  }, 3000);
}

if (require.main === module) {
  main();
}

module.exports = { main };
