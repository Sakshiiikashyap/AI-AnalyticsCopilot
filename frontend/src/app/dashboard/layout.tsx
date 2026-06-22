"use client";

import { usePathname, useRouter } from "next/navigation";
import { logout } from "@/lib/auth";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/login");
  }

  function isActive(path: string) {
    return pathname === path || pathname.startsWith(path + "/");
  }

  return (
    <div className="flex min-h-screen bg-zinc-950 text-white">
      <aside className="w-60 border-r border-zinc-900 flex flex-col px-4 py-6">
        <div className="font-semibold text-lg mb-8 px-2">AI Analytics Copilot</div>

        <nav className="flex flex-col gap-1 flex-1">
          <button
            onClick={() => router.push("/dashboard")}
            className={
              pathname === "/dashboard"
                ? "text-left px-3 py-2 rounded-md bg-zinc-900 text-white text-sm"
                : "text-left px-3 py-2 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-900 text-sm transition-colors duration-150"
            }
          >
            Dashboard
          </button>
          <button
            onClick={() => router.push("/dashboard/datasets")}
            className={
              isActive("/dashboard/datasets")
                ? "text-left px-3 py-2 rounded-md bg-zinc-900 text-white text-sm"
                : "text-left px-3 py-2 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-900 text-sm transition-colors duration-150"
            }
          >
            Datasets
          </button>
        </nav>

        <button
          onClick={handleLogout}
          className="text-left px-3 py-2 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-900 text-sm"
        >
          Log out
        </button>
      </aside>

      <div className="flex-1">{children}</div>
    </div>
  );
}