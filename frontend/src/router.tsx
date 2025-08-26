import { createBrowserRouter } from "react-router-dom";
import AgentsPage from "./components/AgentsPage";
import EnhancedAgentsPage from "./components/EnhancedAgentsPage";
import Layout from "./components/Layout";
import DashboardPage from "./components/DashboardPage";
import WorkflowsPage from "./components/WorkflowsPage";
import ReportsPage from "./components/ReportsPage";
import StatisticsPage from "./components/StatisticsPage";
import DemoPage from "./pages/DemoPage";
import App from "./App";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        path: "",
        element: <Layout />,
        children: [
          {
            index: true,
            element: <DashboardPage />,
          },
          {
            path: "agents",
            element: <EnhancedAgentsPage />,
          },
          {
            path: "agents-old",
            element: <AgentsPage />,
          },
          {
            path: "workflows",
            element: <WorkflowsPage />,
          },
          {
            path: "reports",
            element: <ReportsPage />,
          },
          {
            path: "statistics",
            element: <StatisticsPage />,
          },
          {
            path: "demo",
            element: <DemoPage />,
          },
        ],
      }
    ]
  },
]);

export default router;
