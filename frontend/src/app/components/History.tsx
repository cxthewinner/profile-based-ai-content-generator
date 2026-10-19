import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { Clock, RefreshCcw, Sparkles, Trash2 } from "lucide-react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { ImageWithFallback } from "./shared/ImageWithFallback";
import {
  buildImageUrl,
  deleteHistoryRecord,
  getHistoryList,
  type HistoryListItem,
} from "../api";

function buildHistoryPreview(item: HistoryListItem) {
  if (item.title.trim()) {
    return "点击查看完整标题、正文、标签与配图内容。";
  }
  return "已生成一条图文内容，可继续查看详情或删除。";
}

export function History() {
  const navigate = useNavigate();
  const [historyItems, setHistoryItems] = useState<HistoryListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    setErrorMessage("");

    try {
      const data = await getHistoryList();
      setHistoryItems(data);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "历史记录加载失败。");
    } finally {
      setLoading(false);
    }
  };

  const deleteItem = async (id: number) => {
    setDeletingId(id);
    setErrorMessage("");

    try {
      await deleteHistoryRecord(id);
      setHistoryItems((prev) => prev.filter((item) => item.id !== id));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "删除失败，请稍后再试。");
    } finally {
      setDeletingId(null);
    }
  };

  useEffect(() => {
    void fetchHistory();
  }, []);

  return (
    <div className="min-h-full px-5 pb-[calc(96px+env(safe-area-inset-bottom))] pt-8">
      <div className="mb-5 flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-amber-700/75">
            Archive
          </p>
          <h1 className="mt-1 text-[28px] font-semibold tracking-tight text-slate-900">
            历史记录
          </h1>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            查看之前生成过的图文内容，方便继续编辑、复用或删除。
          </p>
        </div>
        <Button variant="outline" size="icon" onClick={() => void fetchHistory()} disabled={loading}>
          <RefreshCcw className={`h-4 w-4 text-amber-700 ${loading ? "animate-spin" : ""}`} />
        </Button>
      </div>

      {errorMessage ? (
        <Card className="mb-4 p-4">
          <p className="text-sm text-rose-600">{errorMessage}</p>
        </Card>
      ) : null}

      <Card className="mb-4 p-4">
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="rounded-2xl bg-amber-50 px-3 py-3">
            <p className="text-xs text-slate-500">总记录</p>
            <p className="mt-1 text-lg font-semibold text-slate-900">{historyItems.length}</p>
          </div>
          <div className="rounded-2xl bg-stone-100 px-3 py-3">
            <p className="text-xs text-slate-500">内容类型</p>
            <p className="mt-1 text-sm font-semibold text-slate-900">图文方案</p>
          </div>
          <div className="rounded-2xl bg-stone-100 px-3 py-3">
            <p className="text-xs text-slate-500">保存状态</p>
            <p className="mt-1 text-sm font-semibold text-slate-900">本地保存</p>
          </div>
        </div>
      </Card>

      {loading ? (
        <Card className="p-12 text-center">
          <p className="text-sm text-slate-500">正在加载历史记录...</p>
        </Card>
      ) : historyItems.length === 0 ? (
        <Card className="p-12 text-center">
          <Clock className="mx-auto mb-4 h-12 w-12 text-slate-400" />
          <h3 className="mb-2 font-medium text-slate-900">还没有生成记录</h3>
          <p className="mb-6 text-sm text-slate-600">
            先去生成一条内容，这里就会显示保存下来的图文方案。
          </p>
          <Button
            onClick={() => navigate("/profile")}
            className="bg-gradient-to-r from-amber-500 to-orange-500 text-white"
          >
            去生成
          </Button>
        </Card>
      ) : (
        <div className="space-y-4">
          {historyItems.map((item) => (
            <Card
              key={item.id}
              className="overflow-hidden p-4 transition-shadow hover:shadow-[0_14px_32px_rgba(15,23,42,0.08)]"
            >
              <div className="flex gap-3">
                <div className="relative h-[92px] w-[92px] shrink-0 overflow-hidden rounded-[20px] bg-gradient-to-br from-amber-100 to-orange-100">
                  <ImageWithFallback
                    src={buildImageUrl(item.image_url)}
                    alt={item.title}
                    className="h-full w-full object-cover"
                  />
                  <div className="absolute left-2 top-2 rounded-full bg-black/40 px-2 py-1 text-[10px] text-white">
                    #{item.id}
                  </div>
                </div>

                <div className="min-w-0 flex-1">
                  <div className="mb-2 flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <button
                        onClick={() => navigate(`/result?id=${item.id}`)}
                        className="block max-w-full text-left"
                      >
                        <h3 className="truncate text-base font-semibold text-slate-900">
                          {item.title}
                        </h3>
                        <p className="mt-1 line-clamp-2 text-sm leading-6 text-slate-600">
                          {buildHistoryPreview(item)}
                        </p>
                      </button>
                    </div>
                    <button
                      onClick={(event) => {
                        event.stopPropagation();
                        void deleteItem(item.id);
                      }}
                      disabled={deletingId === item.id}
                      className="rounded-xl p-2 transition-colors hover:bg-stone-100 disabled:cursor-not-allowed disabled:opacity-50"
                      aria-label="删除记录"
                    >
                      <Trash2 className="h-4 w-4 text-slate-400 hover:text-red-500" />
                    </button>
                  </div>

                  <div className="flex items-center justify-between border-t border-stone-200/80 pt-3">
                    <div className="text-xs text-slate-500">
                      {deletingId === item.id ? "正在删除..." : "点击卡片查看详情"}
                    </div>
                    <div className="flex items-center gap-1 text-xs text-slate-400">
                      <Clock className="h-3.5 w-3.5" />
                      <span>{item.created_at}</span>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <div className="mt-5 rounded-[28px] bg-[linear-gradient(135deg,#3b2f25_0%,#6d4c41_100%)] p-4 text-white shadow-[0_18px_45px_rgba(15,23,42,0.12)]">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-white/12 p-3">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <p className="text-sm font-medium">内容持续积累中</p>
            <p className="mt-1 text-xs text-white/75">
              你可以从这里快速回看、复用或删除之前保存的图文内容。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
