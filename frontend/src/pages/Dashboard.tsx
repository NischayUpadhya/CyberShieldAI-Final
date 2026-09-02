import StatCard from "../components/dashboard/StatCard";
import AttackTrendChart from "../components/dashboard/AttackTrendchart";
import ThreatDistributionChart from "../components/dashboard/TrheatDistributionChart";
import RecentAlerts from "../components/dashboard/RecentAlerts";

import { stats } from "../data/dashboardData";

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Dashboard heading */}
      <h1 className="text-3xl font-bold">
        Dashboard
      </h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <StatCard
            key={stat.id}
            data={stat}
          />
        ))}
      </div>

      {/* Attack Trend */}
      <AttackTrendChart />

      {/* Threat Distribution */}
      <ThreatDistributionChart />
      <RecentAlerts />
    </div>
  );
}

