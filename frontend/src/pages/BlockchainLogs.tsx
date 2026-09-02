export default function BlockchainLogs() {
  return (
    <div className="space-y-6">

      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold">
          Blockchain Logs
        </h1>

        <p className="mt-2 text-sm text-gray-400">
          Immutable security event records stored on the blockchain
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">

        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Total Records
          </p>

          <p className="mt-3 text-3xl font-bold text-black">
            8,492
          </p>

          <p className="mt-2 text-sm text-green-600">
            +124 today
          </p>
        </div>

        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Verified Records
          </p>

          <p className="mt-3 text-3xl font-bold text-black">
            8,492
          </p>

          <p className="mt-2 text-sm text-green-600">
            100% integrity verified
          </p>
        </div>

        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Blockchain Status
          </p>

          <p className="mt-3 text-2xl font-bold text-black">
            Operational
          </p>

          <p className="mt-2 text-sm text-green-600">
            ● Network healthy
          </p>
        </div>

      </div>

      {/* Blockchain Records */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <div className="mb-6">
          <h2 className="text-xl font-bold text-black">
            Blockchain Records
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Security events permanently recorded on the blockchain
          </p>
        </div>

        <div className="overflow-x-auto">

          <table className="w-full text-left">

            <thead>
              <tr className="border-b text-sm text-gray-500">

                <th className="px-4 py-3">
                  Block
                </th>

                <th className="px-4 py-3">
                  Event
                </th>

                <th className="px-4 py-3">
                  Hash
                </th>

                <th className="px-4 py-3">
                  Timestamp
                </th>

                <th className="px-4 py-3">
                  Status
                </th>

              </tr>
            </thead>

            <tbody>

              <tr className="border-b">

                <td className="px-4 py-4 font-medium text-black">
                  #8492
                </td>

                <td className="px-4 py-4 text-black">
                  Malware Detection
                </td>

                <td className="px-4 py-4 font-mono text-sm text-gray-600">
                  0x7f3a...92bd
                </td>

                <td className="px-4 py-4 text-gray-600">
                  22:58:42
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-600">
                    Verified
                  </span>
                </td>

              </tr>

              <tr className="border-b">

                <td className="px-4 py-4 font-medium text-black">
                  #8491
                </td>

                <td className="px-4 py-4 text-black">
                  Phishing Detection
                </td>

                <td className="px-4 py-4 font-mono text-sm text-gray-600">
                  0x91ab...45ef
                </td>

                <td className="px-4 py-4 text-gray-600">
                  22:57:31
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-600">
                    Verified
                  </span>
                </td>

              </tr>

              <tr className="border-b">

                <td className="px-4 py-4 font-medium text-black">
                  #8490
                </td>

                <td className="px-4 py-4 text-black">
                  DDoS Detection
                </td>

                <td className="px-4 py-4 font-mono text-sm text-gray-600">
                  0x42cd...781a
                </td>

                <td className="px-4 py-4 text-gray-600">
                  22:56:18
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-600">
                    Verified
                  </span>
                </td>

              </tr>

              <tr className="border-b">

                <td className="px-4 py-4 font-medium text-black">
                  #8489
                </td>

                <td className="px-4 py-4 text-black">
                  Ransomware Detection
                </td>

                <td className="px-4 py-4 font-mono text-sm text-gray-600">
                  0xb821...3c91
                </td>

                <td className="px-4 py-4 text-gray-600">
                  22:55:04
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-600">
                    Verified
                  </span>
                </td>

              </tr>

              <tr>

                <td className="px-4 py-4 font-medium text-black">
                  #8488
                </td>

                <td className="px-4 py-4 text-black">
                  Suspicious Login
                </td>

                <td className="px-4 py-4 font-mono text-sm text-gray-600">
                  0xe73d...a421
                </td>

                <td className="px-4 py-4 text-gray-600">
                  22:54:37
                </td>

                <td className="px-4 py-4">
                  <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-600">
                    Verified
                  </span>
                </td>

              </tr>

            </tbody>

          </table>

        </div>
      </div>

      {/* Blockchain Information */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-xl font-bold text-black">
          Blockchain Network
        </h2>

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">

          <div className="rounded-lg bg-gray-100 p-4">
            <p className="text-sm text-gray-500">
              Network
            </p>

            <p className="mt-1 font-semibold text-black">
              CyberShield Private Chain
            </p>
          </div>

          <div className="rounded-lg bg-gray-100 p-4">
            <p className="text-sm text-gray-500">
              Consensus
            </p>

            <p className="mt-1 font-semibold text-black">
              Proof of Authority
            </p>
          </div>

          <div className="rounded-lg bg-gray-100 p-4">
            <p className="text-sm text-gray-500">
              Integrity
            </p>

            <p className="mt-1 font-semibold text-green-600">
              ● Verified
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}