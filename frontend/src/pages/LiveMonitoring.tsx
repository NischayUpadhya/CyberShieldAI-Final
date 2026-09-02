export default function LiveMonitoring() {
  return (
    <div className="space-y-6">

      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold">
          Live Monitoring
        </h1>

        <p className="mt-2 text-sm text-gray-400">
          Real-time monitoring of network activity and security events
        </p>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">

        {/* System Status */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-gray-500">
              System Status
            </p>

            <span className="h-3 w-3 rounded-full bg-green-500" />
          </div>

          <p className="mt-3 text-2xl font-bold text-black">
            Operational
          </p>

          <p className="mt-2 text-sm text-green-600">
            All systems running normally
          </p>
        </div>

        {/* Active Connections */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Active Connections
          </p>

          <p className="mt-3 text-2xl font-bold text-black">
            1,842
          </p>

          <p className="mt-2 text-sm text-green-600">
            +6.2% from last hour
          </p>
        </div>

        {/* Events Per Minute */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Events / Minute
          </p>

          <p className="mt-3 text-2xl font-bold text-black">
            247
          </p>

          <p className="mt-2 text-sm text-gray-500">
            Currently processing
          </p>
        </div>
      </div>

      {/* Live Activity */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-black">
              Live Activity
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Real-time security events
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-green-500" />

            <span className="text-sm font-medium text-green-600">
              Live
            </span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">

            <thead>
              <tr className="border-b text-sm text-gray-500">
                <th className="px-4 py-3">
                  Time
                </th>

                <th className="px-4 py-3">
                  Event
                </th>

                <th className="px-4 py-3">
                  Source
                </th>

                <th className="px-4 py-3">
                  Severity
                </th>

                <th className="px-4 py-3">
                  Status
                </th>
              </tr>
            </thead>

            <tbody>

              <tr className="border-b">
                <td className="px-4 py-4 text-gray-500">
                  22:58:42
                </td>

                <td className="px-4 py-4 font-medium text-black">
                  Suspicious Login Attempt
                </td>

                <td className="px-4 py-4 text-gray-600">
                  192.168.1.25
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-medium text-red-600">
                    High
                  </span>
                </td>

                <td className="px-4 py-4 text-green-600">
                  Blocked
                </td>
              </tr>

              <tr className="border-b">
                <td className="px-4 py-4 text-gray-500">
                  22:57:31
                </td>

                <td className="px-4 py-4 font-medium text-black">
                  Port Scan Detected
                </td>

                <td className="px-4 py-4 text-gray-600">
                  10.0.0.45
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-yellow-100 px-3 py-1 text-xs font-medium text-yellow-600">
                    Medium
                  </span>
                </td>

                <td className="px-4 py-4 text-orange-600">
                  Investigating
                </td>
              </tr>

              <tr className="border-b">
                <td className="px-4 py-4 text-gray-500">
                  22:56:18
                </td>

                <td className="px-4 py-4 font-medium text-black">
                  Malware Signature Detected
                </td>

                <td className="px-4 py-4 text-gray-600">
                  172.16.10.12
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-medium text-red-600">
                    Critical
                  </span>
                </td>

                <td className="px-4 py-4 text-green-600">
                  Blocked
                </td>
              </tr>

              <tr className="border-b">
                <td className="px-4 py-4 text-gray-500">
                  22:55:04
                </td>

                <td className="px-4 py-4 font-medium text-black">
                  Unusual Network Traffic
                </td>

                <td className="px-4 py-4 text-gray-600">
                  203.0.113.21
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-yellow-100 px-3 py-1 text-xs font-medium text-yellow-600">
                    Medium
                  </span>
                </td>

                <td className="px-4 py-4 text-green-600">
                  Monitored
                </td>
              </tr>

              <tr>
                <td className="px-4 py-4 text-gray-500">
                  22:54:37
                </td>

                <td className="px-4 py-4 font-medium text-black">
                  DDoS Pattern Detected
                </td>

                <td className="px-4 py-4 text-gray-600">
                  10.10.20.15
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-medium text-red-600">
                    Critical
                  </span>
                </td>

                <td className="px-4 py-4 text-green-600">
                  Mitigated
                </td>
              </tr>

            </tbody>
          </table>
        </div>
      </div>

      {/* Monitoring Information */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <h2 className="text-xl font-bold text-black">
          Monitoring Services
        </h2>

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">

          <div className="rounded-lg bg-gray-100 p-4">
            <p className="font-medium text-black">
              Network Monitoring
            </p>

            <p className="mt-1 text-sm text-green-600">
              ● Active
            </p>
          </div>

          <div className="rounded-lg bg-gray-100 p-4">
            <p className="font-medium text-black">
              AI Threat Analysis
            </p>

            <p className="mt-1 text-sm text-green-600">
              ● Active
            </p>
          </div>

          <div className="rounded-lg bg-gray-100 p-4">
            <p className="font-medium text-black">
              Automated Response
            </p>

            <p className="mt-1 text-sm text-green-600">
              ● Active
            </p>
          </div>

        </div>
      </div>

    </div>
  );
}