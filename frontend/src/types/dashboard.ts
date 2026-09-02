import type { LucideIcon } from "lucide-react";

export interface StatCardData {
  id: number;
  title: string;
  value: string;
  change: string;
  trend: "up" | "down";
  icon: LucideIcon;
}

export interface AttackTrendData {
  day: string;
  attacks: number;
}

export interface ThreatDistributionData {
  name: string;
  value: number;
}

export interface RecentAlert {
  id: number;
  threat: string;
  severity: "Low" | "Medium" | "High" | "Critical";
  source: string;
  status: "Blocked" | "Investigating" | "Mitigated";
  timestamp: string;
}