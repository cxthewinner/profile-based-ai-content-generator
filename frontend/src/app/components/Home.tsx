import { useNavigate } from "react-router";
import {
  ChevronRight,
  FileText,
  History,
  ImageIcon,
  Sparkles,
  UserCircle,
  Wand2,
} from "lucide-react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { ImageWithFallback } from "./shared/ImageWithFallback";

export function Home() {
  const navigate = useNavigate();
  const quickHighlights = [
    { label: "画像理解", value: "理解兴趣、受众与内容目标", icon: UserCircle },
    { label: "内容生成", value: "生成标题、正文与标签", icon: FileText },
    { label: "视觉配图", value: "生成适合封面的主视觉", icon: ImageIcon },
  ];

  return (
    <div className="min-h-full px-5 pb-[calc(96px+env(safe-area-inset-bottom))] pt-8">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="mb-1 text-xs font-medium uppercase tracking-[0.24em] text-amber-700/80">
            Persona Studio
          </p>
          <h1 className="text-[28px] font-semibold tracking-tight text-slate-900">
            智能图文生成
          </h1>
          <p className="mt-1 text-sm leading-6 text-slate-600">
            输入兴趣、受众和发布场景，快速生成适合社交平台使用的标题、正文、标签与配图。
          </p>
        </div>
        <div className="rounded-[22px] bg-white/80 p-3 shadow-[0_10px_30px_rgba(15,23,42,0.08)]">
          <div className="rounded-2xl bg-gradient-to-br from-amber-400 via-orange-400 to-rose-400 p-3 text-white">
            <Sparkles className="h-6 w-6" />
          </div>
        </div>
      </div>

      <Card className="mb-5 overflow-hidden bg-[linear-gradient(135deg,#2f241d_0%,#5a3f31_52%,#bb5b38_100%)] text-white">
        <div className="relative overflow-hidden px-5 pb-5 pt-5">
          <div className="absolute right-[-32px] top-[-32px] h-32 w-32 rounded-full bg-white/10 blur-2xl" />
          <div className="absolute bottom-[-40px] left-[-16px] h-28 w-28 rounded-full bg-amber-200/10 blur-2xl" />

          <div className="relative z-10 mb-4 inline-flex items-center gap-2 rounded-full bg-white/14 px-3 py-1 text-xs font-medium">
            <Wand2 className="h-3.5 w-3.5" />
            内容创作助手
          </div>

          <div className="relative z-10 mb-4">
            <h2 className="text-2xl font-semibold leading-8">
              从一个想法开始，生成完整图文内容
            </h2>
            <p className="mt-2 text-sm leading-6 text-white/78">
              把零散需求整理成可发布的图文方案。
            </p>
          </div>

          <div className="relative z-10 mb-5 grid grid-cols-3 gap-2">
            {quickHighlights.map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.label}
                  className="rounded-2xl border border-white/10 bg-white/10 px-3 py-3"
                >
                  <Icon className="mb-2 h-4 w-4 text-amber-100" />
                  <p className="text-[11px] text-white/65">{item.label}</p>
                  <p className="mt-1 text-sm font-medium">{item.value}</p>
                </div>
              );
            })}
          </div>

          <div className="relative z-10 flex gap-3">
            <Button
              onClick={() => navigate("/profile")}
              className="flex-1 bg-white text-stone-900 shadow-none hover:bg-stone-100"
            >
              开始生成
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate("/history")}
              className="border-white/20 bg-white/10 text-white hover:bg-white/15 hover:text-white"
            >
              <History className="h-4 w-4" />
              查看历史
            </Button>
          </div>
        </div>
      </Card>

      <Card className="mb-5 p-4">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-amber-700">使用流程</p>
            <h3 className="mt-1 text-lg font-semibold text-slate-900">先配置需求，再生成内容</h3>
          </div>
          <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700">
            移动端友好
          </span>
        </div>

        <div className="space-y-3">
          {[
            ["01", "画像理解", "理解兴趣、受众与内容目标"],
            ["02", "内容生成", "生成标题、正文与标签"],
            ["03", "视觉配图", "生成适合封面的主视觉"],
          ].map(([step, title, desc]) => (
            <div
              key={step}
              className="flex items-start gap-3 rounded-2xl bg-stone-50/90 px-3 py-3"
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-amber-100 text-sm font-semibold text-amber-700">
                {step}
              </div>
              <div>
                <h4 className="text-sm font-medium text-slate-900">{title}</h4>
                <p className="mt-1 text-sm leading-6 text-slate-600">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="overflow-hidden">
        <div className="relative h-44 overflow-hidden rounded-t-[24px]">
          <ImageWithFallback
            src="https://images.unsplash.com/photo-1523726491678-bf852e717f6a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1200"
            alt="Creative workflow"
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-stone-950/40 via-stone-950/10 to-transparent" />
          <div className="absolute bottom-4 left-4 right-4 rounded-2xl bg-white/88 p-3 backdrop-blur-sm">
            <p className="text-xs font-medium text-slate-500">灵感方向</p>
            <p className="mt-1 text-sm font-semibold text-slate-900">
              生活方式分享 / 经验总结 / 轻科普内容
            </p>
          </div>
        </div>

        <div className="p-4">
          <h3 className="text-lg font-semibold text-slate-900">用更清晰的方式开始创作</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            从兴趣、人群和场景出发，把灵感整理成更完整的图文内容方案。
          </p>
        </div>
      </Card>
    </div>
  );
}
