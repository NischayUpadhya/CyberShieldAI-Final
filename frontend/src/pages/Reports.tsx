export default function Reports() {
  return (
    <div className="space-y-6">

      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold">
          Security Reports
        </h1>

        <p className="mt-2 text-sm text-gray-400">
          Security analysis reports and threat intelligence summaries
        </p>
      </div>

      {/* Report Statistics */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">

        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">
            Reports Generated
          </p>

          <p className="mt-3 text-3xl font-bold text-black">
            248
          </p>

          <p className="mt-2 text-sm text-green-600">
            +18 this month
          </p>
        </div>

        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">
            Threats Analyzed
          </p>

          <p className="mt-3 text-3xl font-bold text-black">
            1,284
          </p>

          <p className="mt-2 text-sm text-blue-600">
            AI analysis completed
          </p>
        </div>

        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">
            Critical Incidents
          </p>

          <p className="mt-3 text-3xl font-bold text-black">
            42
          </p>

          <p className="mt-2 text-sm text-red-600">
            Requires attention
          </p>
        </div>

      </div>

      {/* Reports List */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <div className="mb-6">
          <h2 className="text-xl font-bold text-black">
            Recent Reports
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Recently generated cybersecurity reports
          </p>
        </div>

        <div className="overflow-x-auto">

          <table className="w-full text-left">

            <thead>
              <tr className="border-b text-sm text-gray-500">

                <th className="px-4 py-3">
                  Report
                </th>

                <th className="px-4 py-3">
                  Type
                </th>

                <th className="px-4 py-3">
                  Threats
                </th>

                <th className="px-4 py-3">
                  Generated
                </th>

                <th className="px-4 py-3">
                  Status
                </th>

              </tr>
            </thead>

            <tbody>

              <tr className="border-b">

                <td className="px-4 py-4 font-medium text-black">
                  Weekly Security Report
                </td>

                <td className="px-4 py-4 text-gray-600">
                  Weekly
                </td>

                <td className="px-4 py-4 text-gray-600">
                  284
                </td>

                <td className="px-4 py-4 text-gray-600">
                  Today, 10:30 PM
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-600">
                    Completed
                  </span>
                </td>

              </tr>

              <tr className="border-b">

                <td className="px-4 py-4 font-medium text-black">
                  Threat Analysis Report
                </td>

                <td className="px-4 py-4 text-gray-600">
                  Threat Analysis
                </td>

                <td className="px-4 py-4 text-gray-600">
                  127
                </td>

                <td className="px-4 py-4 text-gray-600">
                  Today, 8:45 PM
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-600">
                    Completed
                  </span>
                </td>

              </tr>

              <tr className="border-b">

                <td className="px-4 py-4 font-medium text-black">
                  AI Detection Performance
                </td>

                <td className="px-4 py-4 text-gray-600">
                  AI Analysis
                </td>

                <td className="px-4 py-4 text-gray-600">
                  96
                </td>

                <td className="px-4 py-4 text-gray-600">
                  Yesterday, 6:20 PM
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-600">
                    Completed
                  </span>
                </td>

              </tr>

              <tr className="border-b">

                <td className="px-4 py-4 font-medium text-black">
                  Incident Response Report
                </td>

                <td className="px-4 py-4 text-gray-600">
                  Incident
                </td>

                <td className="px-4 py-4 text-gray-600">
                  42
                </td>

                <td className="px-4 py-4 text-gray-600">
                  Yesterday, 2:15 PM
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-600">
                    Completed
                  </span>
                </td>

              </tr>

            </tbody>

          </table>

        </div>

      </div>

      {/* Security Summary */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-xl font-bold text-black">
          Security Summary
        </h2>

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">

          <div className="rounded-lg bg-gray-100 p-5">
            <p className="text-sm text-gray-500">
              Overall Security Status
            </p>

            <p className="mt-2 text-2xl font-bold text-green-600">
              Healthy
            </p>

            <p className="mt-1 text-sm text-gray-600">
              Systems are operating normally
            </p>
          </div>

          <div className="rounded-lg bg-gray-100 p-5">
            <p className="text-sm text-gray-500">
              AI Detection Accuracy
            </p>

            <p className="mt-2 text-2xl font-bold text-black">
              98.6%
            </p>

            <p className="mt-1 text-sm text-gray-600">
              +0.8% improvement this period
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}