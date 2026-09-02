import { BrowserRouter, Routes, Route } from "react-router-dom";

import MainLayout from "@/layouts/MainLayout";

import Dashboard from "@/pages/Dashboard";
import ThreatDetection from "@/pages/ThreatDetection";
import LiveMonitoring from "@/pages/LiveMonitoring";
import BlockchainLogs from "@/pages/BlockchainLogs";
import Reports from "@/pages/Reports";
import Settings from "@/pages/Settings";
import NotFound from "@/pages/NotFound";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/threats" element={<ThreatDetection />} />
          <Route path="/monitoring" element={<LiveMonitoring />} />
          <Route path="/blockchain" element={<BlockchainLogs />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}