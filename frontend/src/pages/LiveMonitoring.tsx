
import { useEffect, useMemo, useState } from "react";

const API_BASE = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

const POLL_INTERVAL = 2500;
const firstObservedAt = new Map<string, number>();

interface LiveFlow {
  id: string;
  time: string;
  source: string;
  destination: string;
  protocol: string;
  predictedClass: string;
  confidence: number | null;
  isBenign: boolean;
  isPending: boolean;
  pendingReason: string;
}

interface MetricCardProps {
  title: string;
  value: string | number;
  description: string;
  color?: string;
}

interface LiveMonitorPayload {
  capture_mode?: string;
  defense_execution?: string;
  defense_enabled?: boolean;
  automatic_defense_enabled?: boolean;
  flows?: any[];
  [key: string]: any;
}

function getFlows(payload: unknown): any[] {
  if (Array.isArray(payload)) return payload;

  if (!payload || typeof payload !== "object") return [];

  const record = payload as Record<string, unknown>;
  for (const key of ["flows", "items", "results", "data"]) {
    if (Array.isArray(record[key])) return record[key] as any[];
  }

  return [];
}

function getValue(object: any, keys: string[], fallback: any = null): any {
  for (const key of keys) {
    const value = object?.[key];

    if (value !== undefined && value !== null && value !== "") {
      return value;
    }
  }

  return fallback;
}

function formatTime(value: unknown): string {
  if (!value) return "—";

  const date =
    typeof value === "number"
      ? new Date(value > 1e12 ? value : value * 1000)
      : new Date(String(value));

  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleTimeString();
}




function explainPendingReason(flow: any): string {
  const protocol = String(flow.protocol ?? "UNKNOWN").toUpperCase();

  const missing = Array.isArray(flow.missing_features)
    ? flow.missing_features.map(String)
    : [];

  if (protocol === "OTHER") {
    return "Insufficient flow features for prediction";
  }

  if (missing.length === 0) {
    return (
      flow.feature_extraction_reason ||
      "Prediction is not available yet."
    );
  }

  const hasWindowFeatures = missing.some((feature: string) =>
    /Init_Win_bytes_(forward|backward)/i.test(feature)
  );

  const hasActivityFeatures = missing.some((feature: string) =>
    /Active Min|Active Mean/i.test(feature)
  );

  const reasons: string[] = [];

  if (hasWindowFeatures && protocol === "UDP") {
    reasons.push("TCP window measurements are not applicable to UDP");
  } else if (hasWindowFeatures && protocol === "TCP") {
    reasons.push("Initial TCP window measurements were not captured");
  } else if (hasWindowFeatures) {
    reasons.push("Required TCP window measurements are unavailable");
  }

  if (hasActivityFeatures) {
    reasons.push("Activity measurements are unavailable");
  }

  const otherMissing = missing.filter((feature: string) =>
    !/Init_Win_bytes_(forward|backward)|Active Min|Active Mean/i.test(feature)
  );

  if (otherMissing.length > 0) {
    reasons.push(`Missing: ${otherMissing.join(", ")}`);
  }

  return (
    reasons.join("; ") ||
    flow.feature_extraction_reason ||
    "Prediction is not available yet."
  );
}

function normalizeFlow(flow: any): LiveFlow {
  const prediction =
    flow?.prediction && typeof flow.prediction === "object"
      ? flow.prediction
      : {};

  const label = getValue(flow, [
    "predicted_class",
    "prediction_label",
    "label",
    "class_name",
   ], getValue(prediction, [
    "attack_name",
    "predicted_class",
    "label",
    "class_name",
    "class",
    "name",
  ], null));

    const confidenceValue =
    prediction.confidence ??
    prediction.probability ??
    flow.confidence ??
    flow.prediction_confidence ??
    null;

  let confidence =
    confidenceValue === null ? null : Number(confidenceValue);

  if (confidence !== null && Number.isFinite(confidence)) {
    if (confidence > 1 && confidence <= 100) confidence /= 100;
    if (confidence < 0 || confidence > 1) confidence = null;
  } else {
    confidence = null;
  }



  const source = getValue(flow, [
    "src_ip",
    "source_ip",
    "src",
    "source",
    "src_addr",
  ], "Unknown");

  const destination = getValue(flow, [
    "dst_ip",
    "destination_ip",
    "dst",
    "destination",
    "dst_addr",
  ], "Unknown");

  const sourcePort = getValue(flow, ["src_port", "source_port"], "");
  const destinationPort = getValue(
    flow,
    ["dst_port", "destination_port"],
    ""
  );

  const protocol = getValue(flow, ["protocol", "proto"], "Unknown");

  const predictedClass =
    label === null || label === ""
      ? "Awaiting prediction"
      : String(label);

  const isBenign = /benign|normal/i.test(predictedClass);
  const isPending = /pending|unknown|awaiting|none/i.test(predictedClass);


  return {
    id: String(
      getValue(
        flow,
        ["flow_id", "id", "key"],
        `${source}-${sourcePort}-${destination}-${destinationPort}-${protocol}`
      )
    ),
    time: (() => {
      const timestamp = getValue(flow, [
        "last_seen",
        "timestamp",
        "updated_at",
        "start_time",
        "time",
      ]);

      if (timestamp !== null) return formatTime(timestamp);

      const flowId = `${source}-${sourcePort}-${destination}-${destinationPort}-${protocol}`;

      if (!firstObservedAt.has(flowId)) {
        firstObservedAt.set(flowId, Date.now());
      }

      return formatTime(firstObservedAt.get(flowId));
    })(),
    source: `${source}${sourcePort !== "" ? `:${sourcePort}` : ""}`,
    destination: `${destination}${destinationPort !== "" ? `:${destinationPort}` : ""}`,
    protocol: String(protocol).toUpperCase(),
    predictedClass,
    confidence,
    isBenign,
    isPending,
    pendingReason: isPending ? explainPendingReason(flow) : "",
  };
}

function MetricCard({ title, value, description, color = "text-gray-500" }: MetricCardProps) {
  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <p className="text-sm font-medium text-gray-500">{title}</p>
      <p className="mt-3 text-2xl font-bold text-black">{value}</p>
      <p className={`mt-2 text-sm ${color}`}>{description}</p>
    </div>
  );
}

export default function LiveMonitoring() {
  const [payload, setPayload] = useState<LiveMonitorPayload | null>(null);
  const [flows, setFlows] = useState<LiveFlow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    let mounted = true;
    let timer: number | undefined;

    async function fetchFlows() {
      try {
        const response = await fetch(
          `${API_BASE}/api/live-monitor/flows`,
          {
            headers: { Accept: "application/json" },
          }
        );

        if (!response.ok) {
          throw new Error(`Backend returned HTTP ${response.status}`);
        }

        const data = await response.json();

        if (!mounted) return;

        setPayload(data);
        setFlows(getFlows(data).map(normalizeFlow));
        setError("");
        setLastUpdated(new Date());
      } catch (err) {
        if (!mounted) return;

        setError(
          err instanceof Error
            ? err.message
            : "Unable to connect to the backend"
        );
      } finally {
        if (mounted) {
          setLoading(false);
          timer = window.setTimeout(fetchFlows, POLL_INTERVAL);
        }
      }
    }

    fetchFlows();

    return () => {
      mounted = false;
      window.clearTimeout(timer);
    };
  }, []);

  const stats = useMemo(() => {
    const predicted = flows.filter(
      (flow) => !flow.isPending
    ).length;

    const nonBenign = flows.filter(
      (flow) => !flow.isBenign && !flow.isPending
    ).length;

    return {
      total: flows.length,
      predicted,
      nonBenign,
    };
  }, [flows]);

  const captureMode = getValue(
    payload,
    ["capture_mode"],
    "Not reported"
  );

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold">Live Monitoring</h1>
        <p className="mt-2 text-sm text-gray-400">
          Real-time network monitoring and AI predictions
        </p>
      </div>

      {/* Live statistics */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-gray-500">
              Backend Status
            </p>
            <span
              className={`h-3 w-3 rounded-full ${
                error
                  ? "bg-red-500"
                  : loading
                    ? "bg-yellow-400"
                    : "bg-green-500"
              }`}
            />
          </div>

          <p className="mt-3 text-2xl font-bold text-black">
            {error ? "Disconnected" : loading ? "Connecting..." : "Connected"}
          </p>

          <p
            className={`mt-2 text-sm ${
              error ? "text-red-600" : "text-gray-500"
            }`}
          >
            {error ||
              (lastUpdated
                ? `Updated ${lastUpdated.toLocaleTimeString()}`
                : "Waiting for data")}
          </p>
        </div>

        <MetricCard
          title="Observed Flows"
          value={stats.total}
          description={`Capture mode: ${captureMode}`}
        />

        <MetricCard
          title="Flows with Predictions"
          value={stats.predicted}
          description={`${stats.nonBenign} non-benign result(s) require review`}
          color={stats.nonBenign ? "text-amber-600" : "text-green-600"}
        />
      </div>

      {/* Live flow table */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-bold text-black">
              Live Network Flows
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              Automatically refreshed every 2.5 seconds
            </p>
          </div>

          <span
            className={`text-sm font-medium ${
              error ? "text-red-600" : "text-green-600"
            }`}
          >
            ● {error ? "Offline" : "Live polling"}
          </span>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            Could not load live flows: {error}. Ensure the backend is running
            at {API_BASE}.
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b text-sm text-gray-500">
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3">Source</th>
                <th className="px-4 py-3">Destination</th>
                <th className="px-4 py-3">Protocol</th>
                <th className="px-4 py-3">XGBoost Prediction</th>
                <th className="px-4 py-3">Confidence</th>
                <th className="px-4 py-3">Classification</th>
                <th className="px-4 py-3">Prediction Status</th>
              </tr>
            </thead>

            <tbody>
              {loading && flows.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                    Connecting to live monitor...
                  </td>
                </tr>
              )}

              {!loading && !error && flows.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                    No flows were returned by the API yet.
                  </td>
                </tr>
              )}

              {flows.map((flow) => (
                <tr key={flow.id} className="border-b last:border-0">
                  <td className="whitespace-nowrap px-4 py-4 text-gray-500">
                    {flow.time}
                  </td>

                  <td className="whitespace-nowrap px-4 py-4 text-gray-700">
                    {flow.source}
                  </td>

                  <td className="whitespace-nowrap px-4 py-4 text-gray-700">
                    {flow.destination}
                  </td>

                  <td className="px-4 py-4 text-gray-600">
                    {flow.protocol}
                  </td>

                  <td className="px-4 py-4 font-medium text-black">
                    {flow.predictedClass}
                  </td>

                  <td className="px-4 py-4 text-gray-600">
                    {flow.confidence === null
                      ? "—"
                      : `${(flow.confidence * 100).toFixed(1)}%`}
                  </td>

                  <td className="px-4 py-4">
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-medium ${
                        flow.isPending
                          ? "bg-gray-100 text-gray-600"
                          : flow.isBenign
                            ? "bg-green-100 text-green-700"
                            : "bg-amber-100 text-amber-700"
                      }`}
                    >
                      {flow.isPending
                        ? "Awaiting prediction"
                        : flow.isBenign
                          ? "Benign"
                          : "Review"}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-600">
                    {flow.isPending
                    ?flow.pendingReason
                     :"Prediction available"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="mt-4 text-xs text-gray-500">
          A non-benign model output is a classification to investigate, not
          proof that malicious activity occurred. No traffic is blocked by
          this page.
        </p>
      </div>

      {/* Service status */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <h2 className="text-xl font-bold text-black">
          Monitoring Services
        </h2>

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-lg bg-gray-100 p-4">
            <p className="font-medium text-black">Network Monitoring</p>
            <p className="mt-1 text-sm text-green-600">
              ● Passive capture
            </p>
          </div>

          <div className="rounded-lg bg-gray-100 p-4">
            <p className="font-medium text-black">AI Threat Analysis</p>
            <p className="mt-1 text-sm text-green-600">
              ● Prediction pipeline configured
            </p>
          </div>

          <div className="rounded-lg bg-gray-100 p-4">
            <p className="font-medium text-black">Automated Response</p>
            <p className="mt-1 text-sm text-amber-600">
              ● Disabled for safe passive monitoring
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
