import { Outlet, useLocation, useNavigate } from "react-router";
import { Home as HomeIcon, UserCircle, History } from "lucide-react";

export function Root() {
  const location = useLocation();
  const navigate = useNavigate();

  const tabs = [
    { path: "/", icon: HomeIcon, label: "首页" },
    { path: "/profile", icon: UserCircle, label: "生成" },
    { path: "/history", icon: History, label: "历史" },
  ];

  return (
    <div className="h-screen overflow-hidden bg-transparent">
      <div className="mx-auto flex h-full w-full max-w-md flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto pb-28">
          <Outlet />
        </div>

        <div className="pointer-events-none fixed inset-x-0 bottom-0 z-20 flex justify-center px-4 pb-4">
          <div className="pointer-events-auto w-full max-w-md rounded-[28px] border border-white/70 bg-white/88 px-3 py-3 shadow-[0_-8px_30px_rgba(15,23,42,0.12)] backdrop-blur-xl">
            <div className="flex items-center justify-around gap-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = location.pathname === tab.path;

                return (
                  <button
                    key={tab.path}
                    onClick={() => navigate(tab.path)}
                    className={`flex min-w-[88px] flex-1 flex-col items-center gap-1 rounded-2xl px-3 py-2.5 transition-all ${
                      isActive
                        ? "bg-amber-50 text-amber-700 shadow-[inset_0_0_0_1px_rgba(217,119,6,0.08)]"
                        : "text-slate-500 hover:bg-stone-50 hover:text-amber-700"
                    }`}
                  >
                    <Icon className={`h-5 w-5 ${isActive ? "scale-110" : ""}`} />
                    <span className="text-[11px] font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
