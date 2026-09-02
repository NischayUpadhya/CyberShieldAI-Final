import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  ShieldAlert,
  Activity,
  Link2,
  FileBarChart2,
  Settings,
} from "lucide-react";

const menuItems = [
  {
    title: "Dashboard",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    title: "Threat Detection",
    path: "/threats",
    icon: ShieldAlert,
  },
  {
    title: "Live Monitoring",
    path: "/monitoring",
    icon: Activity,
  },
  {
    title: "Blockchain Logs",
    path: "/blockchain",
    icon: Link2,
  },
  {
    title: "Reports",
    path: "/reports",
    icon: FileBarChart2,
  },
  {
    title: "Settings",
    path: "/settings",
    icon: Settings,
  },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
      <div className="p-6 border-b border-slate-800">
        <h1 className="text-2xl font-bold text-cyan-400">
          CyberShield AI
        </h1>
      </div>

      <nav className="flex-1 p-4">
        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.title}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition ${
                  isActive
                    ? "bg-cyan-500 text-white"
                    : "text-slate-300 hover:bg-slate-800"
                }`
              }
            >
              <Icon size={20} />
              {item.title}
            </NavLink>
          );
        })}
      </nav>

      <div className="p-5 border-t border-slate-800 text-sm text-slate-400">
        Logged in as <br />
        <span className="font-semibold text-white">
          Nischay
        </span>
      </div>
    </aside>
  );
}