import { useState } from "react";

const API_URL = (import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

const SELECTED_FEATURES = [
  "Destination Port", "Init_Win_bytes_backward", "Bwd Header Length", "Bwd Packets/s",
  "Flow Duration", "Fwd Packet Length Max", "Bwd Packet Length Max", "Flow IAT Std",
  "Packet Length Mean", "Total Length of Fwd Packets", "Fwd IAT Mean", "Fwd Header Length",
  "Flow Packets/s", "Flow IAT Mean", "Max Packet Length", "Flow IAT Max",
  "act_data_pkt_fwd", "Total Fwd Packets", "Packet Length Variance", "Init_Win_bytes_forward",
  "Fwd IAT Std", "Flow IAT Min", "Fwd_Byte_Percentage", "Fwd IAT Min",
  "Fwd_Bwd_Avg_Packet_Length_Ratio", "Fwd Packet Length Mean", "Fwd_Bwd_Packet_Ratio",
  "Flow Bytes/s", "Fwd_Bwd_Byte_Ratio", "Bwd IAT Total", "PSH Flag Count", "Active Min",
  "Bwd Packet Length Min", "Fwd_Packet_Percentage", "Bwd IAT Mean", "Active Mean",
  "Min Packet Length", "Bwd IAT Max", "Bwd IAT Min", "ACK Flag Count",
] as const;

interface DefenseResult {
  xgboost: { predicted_class: number; attack_name: string; confidence: number };
  ppo: { state_shape: number[]; action: number; action_name: string };
  blockchain: { block_index: number; block_hash: string; previous_hash: string };
  defense_execution?: {
    mode?: string; action?: string; successful?: boolean; message?: string;
    threat_reduction?: number; traffic_reduction?: number;
    legitimate_traffic_impact?: number; resource_cost?: number; response_effectiveness?: number;
  };
  network_context: {
    packet_rate: number; byte_rate: number; active_threats: number; threat_severity: number;
  };
}

interface TestScenario { name: string; sourceIp: string; features: number[] }

const TEST_SCENARIOS: TestScenario[] = [
  {
    name: "Synthetic high-traffic scenario",
    sourceIp: "192.0.2.20",
    features: [
      80, 0, 20, 5000, 100000, 1500, 1500, 5000, 1200, 100000,
      5000, 20, 5000, 5000, 1500, 10000, 100, 500, 500000, 64240,
      5000, 1, 90, 1, 100, 1500, 100, 500, 100, 100,
      100, 100, 500, 100, 5000, 100, 1500, 100, 100, 20,
    ],
  },
  {
    name: "Synthetic all-zero scenario",
    sourceIp: "192.0.2.45",
    features: Array(40).fill(0),
  },
  {
    name: "Synthetic moderate-traffic scenario",
    sourceIp: "198.51.100.32",
    features: [
      6, 0, 2, 120, 800, 60, 40, 120, 80, 800,
      100, 2, 90, 100, 60, 200, 10, 50, 2000, 1500,
      100, 2, 20, 2, 10, 60, 10, 40, 10, 10,
      10, 10, 40, 10, 100, 10, 60, 10, 10, 2,
    ],
  },
];

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function parseDefenseResult(value: unknown): DefenseResult {
  if (!isRecord(value) || !isRecord(value.xgboost) || !isRecord(value.ppo)
      || !isRecord(value.blockchain) || !isRecord(value.network_context)) {
    throw new Error(
      "The backend response did not contain the expected XGBoost, PPO, blockchain, and network_context fields.",
    );
  }

  if (
    typeof value.xgboost.attack_name !== "string" ||
    typeof value.xgboost.confidence !== "number" ||
    typeof value.ppo.action_name !== "string" ||
    typeof value.blockchain.block_index !== "number" ||
    typeof value.blockchain.block_hash !== "string" ||
    typeof value.network_context.active_threats !== "number" ||
    typeof value.network_context.threat_severity !== "number"
  ) {
    throw new Error("The backend returned an incomplete or invalid prediction response.");
  }

  return value as unknown as DefenseResult;
}

function formatConfidence(confidence: number): string {
  const percentage = confidence >= 0 && confidence <= 1 ? confidence * 100 : confidence;
  return `${percentage.toFixed(2)}%`;
}

function formatMetric(value: number | undefined, digits = 3): string {
  return typeof value === "number" && Number.isFinite(value) ? value.toFixed(digits) : "—";
}

export default function ThreatDetection() {
  const [features, setFeatures] = useState<number[]>([]);
  const [sourceIp, setSourceIp] = useState("192.168.1.100");
  const [resultSourceIp, setResultSourceIp] = useState("");
  const [loadedScenario, setLoadedScenario] = useState("");
  const [nextScenarioIndex, setNextScenarioIndex] = useState(0);
  const [result, setResult] = useState<DefenseResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadTestData = () => {
    const scenario = TEST_SCENARIOS[nextScenarioIndex % TEST_SCENARIOS.length];
    if (scenario.features.length !== 40 || !scenario.features.every(Number.isFinite)) {
      setError("The selected test scenario does not contain 40 valid numeric features.");
      return;
    }

    setFeatures([...scenario.features]);
    setSourceIp(scenario.sourceIp);
    setLoadedScenario(scenario.name);
    setNextScenarioIndex((index) => (index + 1) % TEST_SCENARIOS.length);
    setResult(null);
    setResultSourceIp("");
    setError("");
  };

  const predictThreat = async () => {
    if (features.length !== 40 || !features.every(Number.isFinite)) {
      setError("Load a test scenario with 40 valid numeric features before predicting.");
      return;
    }
    const submittedIp = sourceIp.trim();
    if (!submittedIp) {
      setError("Enter a source IP address before predicting.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setResultSourceIp("");

    try {
      const response = await fetch(`${API_URL}/api/defense/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ features, source_ip: submittedIp }),
      });

      const responseText = await response.text();
      let responseData: unknown = null;
      if (responseText) {
        try {
          responseData = JSON.parse(responseText) as unknown;
        } catch {
          throw new Error(
            `The backend returned a non-JSON response (HTTP ${response.status}). Check the API URL and FastAPI server.`,
          );
        }
      }

      if (!response.ok) {
        let detail = `HTTP ${response.status} ${response.statusText}`;
        if (isRecord(responseData) && responseData.detail !== undefined) {
          detail = typeof responseData.detail === "string"
            ? responseData.detail : JSON.stringify(responseData.detail);
        }
        throw new Error(`Prediction failed: ${detail}`);
      }

      setResult(parseDefenseResult(responseData));
      setResultSourceIp(submittedIp);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(
        message === "Failed to fetch" || message.includes("NetworkError")
          ? `Could not reach ${API_URL}. Confirm FastAPI is running and CORS allows the frontend origin.`
          : message,
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Threat Detection</h1>
        <p className="mt-2 text-sm text-gray-500">
          XGBoost threat classification with PPO defense output and blockchain event recording.
        </p>
      </div>

      <section className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="mb-6">
          <h2 className="text-xl font-bold text-black">XGBoost Threat Analysis</h2>
          <p className="mt-1 text-sm text-gray-500">
            Load a synthetic scenario and send its 40 features to the running backend.
            These scenarios are for testing, not live network traffic.
          </p>
        </div>

        <div className="flex flex-wrap gap-4">
          <button type="button" onClick={loadTestData} disabled={loading}
            className="rounded-lg bg-cyan-600 px-5 py-3 font-medium text-white hover:bg-cyan-700 disabled:cursor-not-allowed disabled:opacity-50">
            Load Test Data
          </button>
          <button type="button" onClick={predictThreat} disabled={loading || features.length !== 40}
            className="rounded-lg bg-slate-900 px-5 py-3 font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50">
            {loading ? "Analyzing..." : "Predict Threat"}
          </button>
        </div>

        {loadedScenario && (
          <p className="mt-4 text-sm text-gray-500">
            Loaded scenario: <span className="font-medium text-gray-800">{loadedScenario}</span>
          </p>
        )}

        <div className="mt-6 max-w-md">
          <label htmlFor="source-ip" className="block text-sm font-medium text-gray-600">Source IP</label>
          <input id="source-ip" value={sourceIp} onChange={(event) => setSourceIp(event.target.value)}
            disabled={loading} autoComplete="off" spellCheck={false}
            className="mt-2 w-full rounded-lg border px-4 py-3 text-black disabled:bg-gray-100"
            placeholder="e.g. 192.168.1.100" />
        </div>

        <div className="mt-6 rounded-lg bg-slate-100 p-4">
          <p className="text-sm font-medium text-gray-600">Model Input</p>
          <p className="mt-1 text-lg font-bold text-black">{features.length} / 40 features loaded</p>
          {features.length === 40 && (
            <p className="mt-1 text-xs text-gray-500">
              Feature count validated. Values are sent in the selected-feature order shown below.
            </p>
          )}
        </div>

        {error && (
          <div role="alert" className="mt-6 rounded-lg bg-red-100 p-4 text-sm text-red-800">
            <strong>Error:</strong> {error}
          </div>
        )}
      </section>

      {features.length === 40 && (
        <section className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-black">Selected Features</h2>
          <p className="mt-1 text-sm text-gray-500">The 40 feature names and values sent to the backend.</p>
          <div className="mt-4 max-h-80 overflow-auto">
            <table className="w-full text-left">
              <thead className="sticky top-0 bg-white">
                <tr className="border-b text-sm text-gray-500">
                  <th scope="col" className="px-4 py-3">#</th>
                  <th scope="col" className="px-4 py-3">Feature</th>
                  <th scope="col" className="px-4 py-3">Value</th>
                </tr>
              </thead>
              <tbody>
                {features.map((value, index) => (
                  <tr key={SELECTED_FEATURES[index]} className="border-b">
                    <td className="px-4 py-2 text-gray-500">{index + 1}</td>
                    <td className="px-4 py-2 text-black">{SELECTED_FEATURES[index]}</td>
                    <td className="px-4 py-2 font-medium text-black">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {result && (
        <section className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-black">CyberShield AI Defense Result</h2>
          <p className="mt-1 text-sm text-gray-500">Backend result for source IP {resultSourceIp}.</p>

          <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard label="Detected Attack" value={result.xgboost.attack_name} />
            <MetricCard label="XGBoost Confidence" value={formatConfidence(result.xgboost.confidence)} />
            <MetricCard label="PPO Defense Action" value={result.ppo.action_name} />
            <MetricCard label="Blockchain Block" value={`#${result.blockchain.block_index}`} />
          </div>

          <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
            <MetricCard label="Threat Severity" value={formatMetric(result.network_context.threat_severity)} bordered />
            <MetricCard label="Active Threats" value={String(result.network_context.active_threats)} bordered />
            <MetricCard label="Packet Rate" value={formatMetric(result.network_context.packet_rate)} bordered />
            <MetricCard label="Byte Rate" value={formatMetric(result.network_context.byte_rate)} bordered />
          </div>

          {result.defense_execution && (
            <div className="mt-6 rounded-lg border p-4">
              <h3 className="font-semibold text-black">Defense Execution</h3>
              <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                <Detail label="Mode" value={result.defense_execution.mode ?? "—"} />
                <Detail label="Action" value={result.defense_execution.action ?? "—"} />
                <Detail label="Execution status"
                  value={typeof result.defense_execution.successful === "boolean"
                    ? result.defense_execution.successful ? "Successful" : "Unsuccessful"
                    : "Not reported"} />
                <Detail label="Response effectiveness"
                  value={formatMetric(result.defense_execution.response_effectiveness)} />
              </div>
              {result.defense_execution.message && (
                <p className="mt-3 text-sm text-gray-600">{result.defense_execution.message}</p>
              )}
              <p className="mt-3 text-xs text-amber-700">
                This is the action reported by the backend. Actual network blocking requires a configured enforcement mechanism.
              </p>
            </div>
          )}

          <div className="mt-6 rounded-lg border p-4">
            <h3 className="font-semibold text-black">Blockchain Record</h3>
            <Detail label="Source IP used for this prediction" value={resultSourceIp} />
            <div className="mt-4">
              <p className="text-sm text-gray-500">Block hash / transaction hash returned by backend</p>
              <p className="mt-1 break-all font-mono text-sm text-black">{result.blockchain.block_hash}</p>
            </div>
            <div className="mt-4">
              <p className="text-sm text-gray-500">Previous hash</p>
              <p className="mt-1 break-all font-mono text-sm text-black">{result.blockchain.previous_hash}</p>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

function MetricCard({ label, value, bordered = false }: {
  label: string; value: string; bordered?: boolean;
}) {
  return (
    <div className={`rounded-lg p-5 ${bordered ? "border" : "bg-slate-100"}`}>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-2 break-words text-xl font-bold text-black">{value}</p>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-1 break-words font-medium text-black">{value}</p>
    </div>
  );
}
