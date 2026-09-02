import type { StatCardData } from "../../types/dashboard";

type StatCardProps = {
  data: StatCardData;
};

export default function StatCard({ data }: StatCardProps) {
  const {
    title,
    value,
    change,
    trend,
    icon: Icon,
  } = data;

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm transition-all duration-300 hover:shadow-md">
      <div className="mb-4 flex items-center justify-between">
        <div className="rounded-lg bg-gray-200 p-3">
          <Icon className="h-6 w-6 text-black" />
        </div>

        <span
          className={`text-sm font-medium ${
            trend === "up"
              ? "text-green-500"
              : "text-red-500"
          }`}
        >
          {change}
        </span>
      </div>

      <div className="space-y-1">
        <h3 className="text-sm font-medium text-gray-600">
          {title}
        </h3>

        <p className="text-3xl font-bold tracking-tight text-black">
          {value}
        </p>
      </div>
    </div>
  );
}