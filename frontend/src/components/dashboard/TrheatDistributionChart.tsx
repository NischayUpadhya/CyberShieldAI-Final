import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from "recharts";

import { threatDistributionData } from "../../data/dashboardData";

const COLORS = [
  "#06b6d4",
  "#3b82f6",
  "#8b5cf6",
  "#f59e0b",
  "#ef4444",
];

export default function ThreatDistributionChart() {
  return (
    <div className="w-full rounded-xl border bg-white p-6 shadow-sm">
      <h2 className="mb-6 text-xl font-bold text-black">
        Threat Distribution
      </h2>

      <div
        className="w-full"
        style={{ height: "320px" }}
      >
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <PieChart>
            <Pie
              data={threatDistributionData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={105}
              label
            >
              {threatDistributionData.map(
                (entry, index) => (
                  <Cell
                    key={`cell-${entry.name}`}
                    fill={
                      COLORS[
                        index % COLORS.length
                      ]
                    }
                  />
                )
              )}
            </Pie>

            <Tooltip />

            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}