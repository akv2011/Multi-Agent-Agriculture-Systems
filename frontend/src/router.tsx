import { createBrowserRouter } from "react-router-dom";
import React, { Suspense, lazy } from 'react';
import App from "./App";
import ErrorBoundary from "./components/ErrorBoundary";

// Replace direct imports with lazy for code-splitting
const AgentsPage = lazy(() => import('./components/AgentsPage'));
const EnhancedAgentsPage = lazy(() => import('./components/EnhancedAgentsPage'));
const Layout = lazy(() => import('./components/Layout'));
const DashboardPage = lazy(() => import('./components/DashboardPage'));
const WorkflowsPage = lazy(() => import('./components/WorkflowsPage'));
const ReportsPage = lazy(() => import('./components/ReportsPage'));
const StatisticsPage = lazy(() => import('./components/StatisticsPage'));
const MarketplacePage = lazy(() => import('./components/MarketplacePage'));
const BusinessIntelligencePage = lazy(() => import('./components/BusinessIntelligencePage'));
const AddProductPage = lazy(() => import('./components/AddProductPage'));
const FarmerProfilePage = lazy(() => import('./components/FarmerProfilePage'));
const DemoPage = lazy(() => import('./pages/DemoPage'));

// Helper wrapper to avoid repeating Suspense fallback
const withFallback = (element: React.ReactNode) => (
  <ErrorBoundary>
    <Suspense fallback={
      <div className="route-fallback">
        <div className="loading-spinner"></div>
        <p>Loading page...</p>
      </div>
    }>
      {element}
    </Suspense>
  </ErrorBoundary>
);

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        path: "",
        element: withFallback(<Layout />),
        children: [
          { index: true, element: withFallback(<DashboardPage />) },
          { path: "agents", element: withFallback(<EnhancedAgentsPage />) },
          { path: "agents-old", element: withFallback(<AgentsPage />) },
          { path: "workflows", element: withFallback(<WorkflowsPage />) },
          { path: "reports", element: withFallback(<ReportsPage />) },
          { path: "statistics", element: withFallback(<StatisticsPage />) },
          { path: "marketplace", element: withFallback(<MarketplacePage />) },
          { path: "marketplace/add-product", element: withFallback(<AddProductPage />) },
          { path: "farmer-profiles", element: withFallback(<FarmerProfilePage />) },
          { path: "business-intelligence", element: withFallback(<BusinessIntelligencePage />) },
          { path: "demo", element: withFallback(<DemoPage />) },
        ],
      }
    ]
  },
]);

export default router;
