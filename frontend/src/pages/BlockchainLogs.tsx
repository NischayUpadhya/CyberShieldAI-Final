import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

interface BlockchainRecord {
  index: number;
  timestamp?: string;
  event?: {
    attack_type?: string;
    source_ip?: string;
    severity?: string;
    xgboost_confidence?: number;
    ppo_action?: string | null;
  };
  previous_hash?: string;
  hash?: string;
}

interface BlockchainStatus {
  status: string;
  network: string;
  consensus: string;
  integrity: boolean;
}

export default function BlockchainLogs() {
  const [records, setRecords] = useState<BlockchainRecord[]>([]);
  const [status, setStatus] = useState<BlockchainStatus | null>(null);
  const [verified, setVerified] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadBlockchainData = async () => {
    try {
      setLoading(true);
      setError("");

      const [recordsResponse, statusResponse, verifyResponse] =
        await Promise.all([
          fetch(`${API_URL}/api/blockchain/records`),
          fetch(`${API_URL}/api/blockchain/status`),
          fetch(`${API_URL}/api/blockchain/verify`),
        ]);

      if (!recordsResponse.ok) {
        throw new Error("Failed to load blockchain records");
      }

      if (!statusResponse.ok) {
        throw new Error("Failed to load blockchain status");
      }

      if (!verifyResponse.ok) {
        throw new Error("Failed to verify blockchain");
      }

      const recordsData = await recordsResponse.json();
      const statusData = await statusResponse.json();
      const verifyData = await verifyResponse.json();

      // The backend may return the records directly or inside "records".
      const blockchainRecords = Array.isArray(recordsData)
        ? recordsData
        : recordsData.records || [];

      setRecords(blockchainRecords);
      setStatus(statusData);

      setVerified(
        typeof verifyData === "boolean"
          ? verifyData
          : verifyData.valid ?? verifyData.integrity ?? false
      );
   } catch (err: unknown) {
  setError(
    err instanceof Error
      ? err.message
      : "Unable to connect to the blockchain backend"
  );
} finally {
      setLoading(false);
    }
  };

  useEffect(() => {
  // Initial data fetch synchronizes this page with the backend.
  // eslint-disable-next-line react-hooks/set-state-in-effect
  void loadBlockchainData();
}, []);
  const formatTimestamp = (timestamp?: string) => {
    if (!timestamp) return "-";

    const date = new Date(timestamp);

    if (Number.isNaN(date.getTime())) {
      return timestamp;
    }

    return date.toLocaleString();
  };

  const formatHash = (hash?: string) => {
    if (!hash) return "-";

    if (hash.length <= 18) {
      return hash;
    }

    return `${hash.slice(0, 10)}...${hash.slice(-8)}`;
  };

  const totalRecords = records.length;

  const verifiedRecords =
    verified === true ? totalRecords : 0;

  return (
    <div className="space-y-6">

      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold">
          Blockchain Logs
        </h1>

        <p className="mt-2 text-sm text-gray-400">
          Immutable security event records stored on the CyberShield private chain
        </p>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">

        {/* Total Records */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Total Records
          </p>

          <p className="mt-3 text-3xl font-bold text-black">
            {loading ? "..." : totalRecords}
          </p>

          <p className="mt-2 text-sm text-gray-500">
            Actual blockchain records
          </p>
        </div>

        {/* Verified Records */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Verified Records
          </p>

          <p className="mt-3 text-3xl font-bold text-black">
            {loading ? "..." : verifiedRecords}
          </p>

          <p className="mt-2 text-sm text-green-600">
            {verified === true
              ? "100% integrity verified"
              : "Integrity verification pending"}
          </p>
        </div>

        {/* Blockchain Status */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Blockchain Status
          </p>

          <p className="mt-3 text-2xl font-bold text-black">
            {loading ? "..." : status?.status || "Unknown"}
          </p>

          <p
            className={`mt-2 text-sm ${
              verified
                ? "text-green-600"
                : "text-red-600"
            }`}
          >
            {verified
              ? "✓ Chain integrity verified"
              : "✗ Integrity verification failed"}
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
            Live security events recorded by the CyberShield blockchain service
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
                  Source IP
                </th>

                <th className="px-4 py-3">
                  PPO Action
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

              {loading ? (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-8 text-center text-gray-500"
                  >
                    Loading blockchain records...
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-8 text-center text-gray-500"
                  >
                    No blockchain records found.
                  </td>
                </tr>
              ) : (
                [...records]
                  .reverse()
                  .map((record) => (
                    <tr
                      key={record.index}
                      className="border-b"
                    >

                      <td className="px-4 py-4 font-medium text-black">
                        #{record.index}
                      </td>

                      <td className="px-4 py-4 text-black">
                        {record.event?.attack_type || "Genesis"}
                      </td>

                      <td className="px-4 py-4 font-mono text-sm text-gray-600">
                        {record.event?.source_ip || "-"}
                      </td>

                      <td className="px-4 py-4 text-black">
                        {record.event?.ppo_action || "-"}
                      </td>

                      <td className="px-4 py-4 font-mono text-sm text-gray-600">
                        {formatHash(record.hash)}
                      </td>

                      <td className="px-4 py-4 text-gray-600">
                        {formatTimestamp(record.timestamp)}
                      </td>

                      <td className="px-4 py-4">
                        <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-600">
                          Verified
                        </span>
                      </td>

                    </tr>
                  ))
              )}

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
              {status?.network || "CyberShield Private Chain"}
            </p>
          </div>

          <div className="rounded-lg bg-gray-100 p-4">
            <p className="text-sm text-gray-500">
              Consensus
            </p>

            <p className="mt-1 font-semibold text-black">
              {status?.consensus || "Single-Node Private Chain"}
            </p>
          </div>

          <div className="rounded-lg bg-gray-100 p-4">
            <p className="text-sm text-gray-500">
              Integrity
            </p>

            <p
              className={`mt-1 font-semibold ${
                verified
                  ? "text-green-600"
                  : "text-red-600"
              }`}
            >
              {verified
                ? "✓ Verified"
                : "✗ Verification Failed"}
            </p>
          </div>

        </div>

        {/* Refresh */}
        <button
          onClick={loadBlockchainData}
          disabled={loading}
          className="mt-6 rounded-lg bg-slate-900 px-5 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Refreshing..." : "Refresh Blockchain"}
        </button>

      </div>

    </div>
  );
}