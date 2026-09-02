import {
  Activity,
  ShieldAlert,
  ShieldCheck,
  Brain,
} from "lucide-react";

import type {
  StatCardData,
  AttackTrendData,
  ThreatDistributionData,
  RecentAlert,
} from "../types/dashboard";

export const stats: StatCardData[] = [
  {
    id: 1,
    title: "Total Attacks",
    value: "12,480",
    change: "+12%",
    trend: "up",
    icon: Activity,
  },
  {
    id: 2,
    title: "Active Threats",
    value: "28",
    change: "-5%",
    trend: "down",
    icon: ShieldAlert,
  },
  {
    id: 3,
    title: "Blocked IPs",
    value: "1,942",
    change: "+18%",
    trend: "up",
    icon: ShieldCheck,
  },
  {
    id: 4,
    title: "AI Accuracy",
    value: "98.6%",
    change: "+0.8%",
    trend: "up",
    icon: Brain,
  },
];

export const attackTrendData: AttackTrendData[] = [
  { day: "Mon", attacks: 120 },
  { day: "Tue", attacks: 180 },
  { day: "Wed", attacks: 160 },
  { day: "Thu", attacks: 240 },
  { day: "Fri", attacks: 210 },
  { day: "Sat", attacks: 310 },
  { day: "Sun", attacks: 280 },
];

export const threatDistributionData: ThreatDistributionData[] = [
  { name: "Malware", value: 35 },
  { name: "Phishing", value: 25 },
  { name: "DDoS", value: 20 },
  { name: "Ransomware", value: 12 },
  { name: "Insider Threat", value: 8 },
];

export const recentAlerts: RecentAlert[] = [
  {
    id: 1,
    threat: "Malware",
    severity: "High",
    source: "192.168.1.25",
    status: "Blocked",
    timestamp: "2 min ago",
  },
  {
    id: 2,
    threat: "Phishing",
    severity: "Medium",
    source: "172.16.10.12",
    status: "Investigating",
    timestamp: "8 min ago",
  },
  {
    id: 3,
    threat: "DDoS",
    severity: "Critical",
    source: "10.0.0.45",
    status: "Mitigated",
    timestamp: "15 min ago",
  },
  {
    id: 4,
    threat: "Ransomware",
    severity: "Critical",
    source: "203.0.113.21",
    status: "Blocked",
    timestamp: "30 min ago",
  },
];