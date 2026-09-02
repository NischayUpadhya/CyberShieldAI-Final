import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

import { attackTrendData } from "../../data/dashboardData";

export default function AttackTrendChart() {
  return (
    <div className="w-full rounded-xl border bg-white p-6 shadow-sm">
      <h2 className="mb-6 text-xl font-bold text-black">
        Attack Trend
      </h2>

      <div
        className="w-full"
        style={{ height: "320px" }}
      >
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <LineChart
            data={attackTrendData}
            margin={{
              top: 10,
              right: 20,
              left: 10,
              bottom: 10,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="day" />

            <YAxis />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="attacks"
              stroke="#06b6d4"
              strokeWidth={3}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}