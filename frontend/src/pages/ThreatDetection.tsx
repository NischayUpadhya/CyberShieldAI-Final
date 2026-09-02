import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

const SELECTED_FEATURES = [
  "Destination Port",
  "Init_Win_bytes_backward",
  "Bwd Header Length",
  "Bwd Packets/s",
  "Flow Duration",
  "Fwd Packet Length Max",
  "Bwd Packet Length Max",
  "Flow IAT Std",
  "Packet Length Mean",
  "Total Length of Fwd Packets",
  "Fwd IAT Mean",
  "Fwd Header Length",
  "Flow Packets/s",
  "Flow IAT Mean",
  "Max Packet Length",
  "Flow IAT Max",
  "act_data_pkt_fwd",
  "Total Fwd Packets",
  "Packet Length Variance",
  "Init_Win_bytes_forward",
  "Fwd IAT Std",
  "Flow IAT Min",
  "Fwd_Byte_Percentage",
  "Fwd IAT Min",
  "Fwd_Bwd_Avg_Packet_Length_Ratio",
  "Fwd Packet Length Mean",
  "Fwd_Bwd_Packet_Ratio",
  "Flow Bytes/s",
  "Fwd_Bwd_Byte_Ratio",
  "Bwd IAT Total",
  "PSH Flag Count",
  "Active Min",
  "Bwd Packet Length Min",
  "Fwd_Packet_Percentage",
  "Bwd IAT Mean",
  "Active Mean",
  "Min Packet Length",
  "Bwd IAT Max",
  "Bwd IAT Min",
  "ACK Flag Count",
];

export default function ThreatDetection() {
  const [features, setFeatures] = useState<number[]>([]);
  const [sourceIp, setSourceIp] = useState("192.168.1.100");

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Load a test packet
  const loadTestData = () => {
    const testData = new Array(40).fill(0);

    // Example benign network traffic
    testData[0] = 80;      // Destination Port
    testData[4] = 100000;  // Flow Duration
    testData[5] = 1000;    // Fwd Packet Length Max
    testData[6] = 1000;    // Bwd Packet Length Max
    testData[17] = 10;     // Total Fwd Packets
    testData[18] = 100;    // Packet Length Variance
    testData[19] = 64240;  // Init Win Forward
    testData[20] = 1000;   // Fwd IAT Std
    testData[21] = 1000;   // Flow IAT Min
    testData[29] = 10000;  // Bwd IAT Total
    testData[30] = 0;      // PSH Flag Count
    testData[38] = 1000;   // Bwd IAT Min
    testData[39] = 10;     // ACK Flag Count

    setFeatures(testData);
    setSourceIp("192.168.1.100");
    setResult(null);
    setError("");
  };

  const predictThreat = async () => {
    if (features.length !== 40) {
      setError("Please load test data first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        `${API_URL}/api/xgboost/predict`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            features: features,
            source_ip: sourceIp,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
            ? JSON.stringify(data.detail)
            : "Prediction failed"
        );
      }

      setResult(data);
    } catch (err: any) {
      setError(err.message || "Unable to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">
          Threat Detection
        </h1>

        <p className="mt-2 text-sm text-gray-400">
          AI-powered XGBoost network threat detection
        </p>
      </div>

      {/* XGBoost Detection Panel */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <div className="mb-6">
          <h2 className="text-xl font-bold text-black">
            XGBoost Threat Analysis
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Load network test data and run the trained XGBoost model.
          </p>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap gap-4">

          <button
            onClick={loadTestData}
            className="rounded-lg bg-cyan-600 px-5 py-3 font-medium text-white hover:bg-cyan-700"
          >
            Load Test Data
          </button>

          <button
            onClick={predictThreat}
            disabled={loading || features.length !== 40}
            className="rounded-lg bg-slate-900 px-5 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Analyzing..." : "Predict Threat"}
          </button>

        </div>

        {/* Source IP */}
        <div className="mt-6 max-w-md">
          <label className="block text-sm font-medium text-gray-600">
            Source IP
          </label>

          <input
            value={sourceIp}
            onChange={(e) => setSourceIp(e.target.value)}
            className="mt-2 w-full rounded-lg border px-4 py-3 text-black"
          />
        </div>

        {/* Feature Status */}
        <div className="mt-6 rounded-lg bg-slate-100 p-4">

          <p className="text-sm font-medium text-gray-600">
            Model Input
          </p>

          <p className="mt-1 text-lg font-bold text-black">
            {features.length} / 40 features loaded
          </p>

        </div>

        {/* Error */}
        {error && (
          <div className="mt-6 rounded-lg bg-red-100 p-4 text-sm text-red-700">
            <strong>Error:</strong> {error}
          </div>
        )}

      </div>

      {/* Loaded Features */}
      {features.length === 40 && (
        <div className="rounded-xl border bg-white p-6 shadow-sm">

          <h2 className="text-xl font-bold text-black">
            Selected Features
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            40 features selected by the trained XGBoost pipeline.
          </p>

          <div className="mt-4 max-h-80 overflow-y-auto">

            <table className="w-full text-left">

              <thead>
                <tr className="border-b text-sm text-gray-500">
                  <th className="px-4 py-3">
                    #
                  </th>

                  <th className="px-4 py-3">
                    Feature
                  </th>

                  <th className="px-4 py-3">
                    Value
                  </th>
                </tr>
              </thead>

              <tbody>
                {features.map((value, index) => (
                  <tr
                    key={index}
                    className="border-b"
                  >
                    <td className="px-4 py-2 text-gray-500">
                      {index + 1}
                    </td>

                    <td className="px-4 py-2 text-black">
                      {SELECTED_FEATURES[index]}
                    </td>

                    <td className="px-4 py-2 font-medium text-black">
                      {value}
                    </td>
                  </tr>
                ))}
              </tbody>

            </table>

          </div>
        </div>
      )}

      {/* Prediction Result */}
      {result && (
        <div className="rounded-xl border bg-white p-6 shadow-sm">

          <h2 className="text-xl font-bold text-black">
            XGBoost Prediction Result
          </h2>

          <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">

            {/* Attack */}
            <div className="rounded-lg bg-slate-100 p-5">
              <p className="text-sm text-gray-500">
                Detected Attack
              </p>

              <p className="mt-2 text-2xl font-bold text-black">
                {result.attack_name}
              </p>
            </div>

            {/* Confidence */}
            <div className="rounded-lg bg-slate-100 p-5">
              <p className="text-sm text-gray-500">
                Confidence
              </p>

              <p className="mt-2 text-2xl font-bold text-black">
                {(result.confidence * 100).toFixed(2)}%
              </p>
            </div>

            {/* Severity */}
            <div className="rounded-lg bg-slate-100 p-5">
              <p className="text-sm text-gray-500">
                Severity
              </p>

              <p className="mt-2 text-2xl font-bold text-black">
                {result.severity}
              </p>
            </div>

            {/* Status */}
            <div className="rounded-lg bg-slate-100 p-5">
              <p className="text-sm text-gray-500">
                Status
              </p>

              <p className="mt-2 text-2xl font-bold text-black">
                {result.status}
              </p>
            </div>

          </div>

          {/* Source */}
          <div className="mt-6 rounded-lg border p-4">

            <p className="text-sm text-gray-500">
              Source IP
            </p>

            <p className="mt-1 font-mono text-black">
              {result.source_ip}
            </p>

          </div>

        </div>
      )}

    </div>
  );
}