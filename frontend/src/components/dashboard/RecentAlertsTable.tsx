import { recentAlerts } from "../../data/dashboardData";

export default function RecentAlertsTable() {
  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <h2 className="mb-6 text-xl font-bold">Recent Alerts</h2>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b text-left">
              <th className="p-3">Threat</th>
              <th className="p-3">Severity</th>
              <th className="p-3">Source</th>
              <th className="p-3">Status</th>
              <th className="p-3">Time</th>
            </tr>
          </thead>

          <tbody>
            {recentAlerts.map((alert) => (
              <tr key={alert.id} className="border-b hover:bg-gray-50">
                <td className="p-3">{alert.threat}</td>
                <td className="p-3">{alert.severity}</td>
                <td className="p-3">{alert.source}</td>
                <td className="p-3">{alert.status}</td>
                <td className="p-3">{alert.timestamp}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}