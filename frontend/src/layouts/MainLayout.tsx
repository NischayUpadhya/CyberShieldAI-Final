import { Outlet } from "react-router-dom";

import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";

export default function MainLayout() {
  return (
    <div className="flex min-h-screen bg-slate-950 text-white">

      <Sidebar />

      <div className="flex flex-col flex-1">

        <Navbar />

        <main className="p-6 flex-1">
          <Outlet />
        </main>

      </div>

    </div>
  );
}