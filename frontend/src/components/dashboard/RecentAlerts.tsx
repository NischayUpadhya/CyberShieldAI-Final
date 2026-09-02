import { recentAlerts } from "../../data/dashboardData";

export default function RecentAlerts() {
  return (
    <div className="w-full rounded-xl border bg-white p-6 shadow-sm">
      <h2 className="mb-6 text-xl font-bold text-black">
        Recent Alerts
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b text-sm text-gray-500">
              <th className="px-4 py-3">Threat</th>
              <th className="px-4 py-3">Severity</th>
              <th className="px-4 py-3">Source</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Time</th>
            </tr>
          </thead>

          <tbody>
            {recentAlerts.map((alert) => (
              <tr
                key={alert.id}
                className="border-b last:border-b-0"
              >
                <td className="px-4 py-4 font-medium text-black">
                  {alert.threat}
                </td>

                <td className="px-4 py-4">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-medium ${
                      alert.severity === "Critical"
                        ? "bg-red-100 text-red-600"
                        : alert.severity === "High"
                        ? "bg-orange-100 text-orange-600"
                        : alert.severity === "Medium"
                        ? "bg-yellow-100 text-yellow-600"
                        : "bg-green-100 text-green-600"
                    }`}
                  >
                    {alert.severity}
                  </span>
                </td>

                <td className="px-4 py-4 text-gray-600">
                  {alert.source}
                </td>

                <td className="px-4 py-4 text-gray-600">
                  {alert.status}
                </td>

                <td className="px-4 py-4 text-gray-500">
                  {alert.timestamp}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}