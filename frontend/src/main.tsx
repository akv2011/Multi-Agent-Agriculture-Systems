import React from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { RouterProvider } from 'react-router-dom'
import router from './router'

// Add console log to verify main.tsx is executing
console.log("Main.tsx is initializing the application");

// Check if root element exists
const rootElement = document.getElementById('root');
if (!rootElement) {
  console.error("Root element not found! Check your HTML file.");
} else {
  console.log("Root element found, rendering application...");
  createRoot(rootElement).render(
    // Temporarily disable StrictMode to fix WebSocket connection issues in development
    // <React.StrictMode>
      <RouterProvider router={router} />
    // </React.StrictMode>
  );
}
