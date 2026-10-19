import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router";
import {
  Copy,
  ImageIcon,
  MoreHorizontal,
  RefreshCcw,
  Sparkles,
} from "lucide-react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { ImageWithFallback } from "./shared/ImageWithFallback";
import {
  buildImageUrl,
  generateContent,
  getHistoryDetail,
  type GenerateRequestPayload,
  type GenerateResponse,
  type HistoryDetail,
} from "../api";

interface ResultLocationState {
  result: GenerateResponse;
  input: string;
  styles: string[];
  scenarios: string[];
  targetUser: string;
  interests: string[];
}

export function Result() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as ResultLocationState | null;
  const searchParams = new URLSearchParams(location.search);
  const recordId = searchParams.get("id");

  const [detailResult, setDetailResult] = useState<GenerateResponse | HistoryDetail | null>(
    state?.result ?? null,
  );
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [copyMessage, setCopyMessage] = useState("");

  useEffect(() => {
    if (state?.result) {
      setDetailResult(state.result);
      return;
    }

    if (!recordId) {
      navigate("/profile");
      return;
    }

    const loadDetail = async () => {
      setLoading(true);
      setErrorMessage("");

      try {
        const detail = await getHistoryDetail(Number(recordId));
        setDetailResult(detail);
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "生成失败，请稍后重试。");
      } finally {
        setLoading(false);
      }
    };

    void loadDetail();
  }, [navigate, recordId, state]);

  useEffect(() => {
    if (!copyMessage) {
      return;
    }

    const timer = window.setTimeout(() => {
      setCopyMessage("");
    }, 2000);

    return () => window.clearTimeout(timer);
  }, [copyMessage]);

  const result = detailResult;
  const displayStyles = state?.styles ?? (result && "style" in result ? [result.style] : []);
  const displayScenarios =
    state?.scenarios ?? (result && "scenario" in result ? [result.scenario] : []);
  const displayTargetUser =
    state?.targetUser ?? (result && "target_user" in result ? result.target_user : "");
  const displayInterests =
    state?.interests ??
    (result && "interests" in result
      ? result.interests
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean)
      : []);
  const displayInput =
    state?.input ?? (result && "input_text" in result ? result.input_text ?? "" : "");

  const imageSrc = useMemo(() => {
    if (!result?.image_url) {
      return "";
    }

    return buildImageUrl(result.image_url);
  }, [result?.image_url]);

  const canRegenerate =
    displayInterests.length > 0 &&
    displayStyles.length > 0 &&
    displayScenarios.length > 0 &&
    displayTargetUser.trim().length > 0;

  const handleCopy = async () => {
    if (!result) {
      return;
    }

    try {
      await navigator.clipboard.writeText(`${result.title}\n\n${result.content}`);
      setCopyMessage("内容已复制");
    } catch {
      setCopyMessage("复制失败，请手动复制");
    }
  };

  const handleRegenerate = async () => {
    if (!canRegenerate) {
      setErrorMessage("缺少重新生成所需的信息。");
      return;
    }

    const payload: GenerateRequestPayload = {
      interests: displayInterests,
      style: displayStyles[0],
      scenario: displayScenarios[0],
      target_user: displayTargetUser.trim(),
      input_text: displayInput,
    };

    setIsRegenerating(true);
    setErrorMessage("");

    try {
      const newResult = await generateContent(payload);
      setDetailResult(newResult);
      navigate("/result", {
        replace: true,
        search: `?id=${newResult.id}`,
        state: {
          result: newResult,
          input: displayInput,
          styles: displayStyles,
          scenarios: displayScenarios,
          targetUser: displayTargetUser,
          interests: displayInterests,
        },
      });
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "生成失败，请稍后重试。");
    } finally {
      setIsRegenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-full px-5 pb-6 pt-8">
        <Card className="p-12 text-center">
          <p className="text-sm text-slate-500">正在加载结果详情...</p>
        </Card>
      </div>
    );
  }

  if (errorMessage && !result) {
    return (
      <div className="min-h-full px-5 pb-6 pt-8">
        <Card className="p-6 text-center">
          <p className="text-sm text-rose-600">{errorMessage}</p>
          <Button onClick={() => navigate("/history")} className="mt-4">
            返回历史记录
          </Button>
        </Card>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  return (
    <div className="min-h-full px-5 pb-[calc(96px+env(safe-area-inset-bottom))] pt-8">
      <div className="mb-5 flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-amber-700/75">
            Generated Result
          </p>
          <h1 className="mt-1 text-[28px] font-semibold tracking-tight text-slate-900">
            生成结果
          </h1>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            这里展示本次生成的配图、标题、正文、标签和画像摘要。
          </p>
        </div>
        <button className="rounded-2xl bg-white/80 p-3 transition-colors hover:bg-white">
          <MoreHorizontal className="h-5 w-5 text-slate-600" />
        </button>
      </div>

      {errorMessage ? (
        <Card className="mb-4 border-rose-100 bg-rose-50/80 p-4">
          <p className="text-sm text-rose-600">{errorMessage}</p>
        </Card>
      ) : null}

      {copyMessage ? (
        <Card className="mb-4 border-emerald-100 bg-emerald-50/80 p-4">
          <p className="text-sm text-emerald-700">{copyMessage}</p>
        </Card>
      ) : null}

      <Card className="mb-4 overflow-hidden bg-[linear-gradient(135deg,#31241f_0%,#6c4c3e_100%)] text-white">
        <div className="space-y-4 p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white/14">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="font-medium">生成完成</h3>
              <p className="text-xs text-white/70">已保存到历史记录</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {displayStyles.map((item) => (
              <span key={item} className="rounded-full bg-white/12 px-3 py-1.5 text-xs font-medium">
                风格：{item}
              </span>
            ))}
            {displayScenarios.map((item) => (
              <span
                key={item}
                className="rounded-full bg-white/12 px-3 py-1.5 text-xs font-medium"
              >
                场景：{item}
              </span>
            ))}
          </div>
        </div>
      </Card>

      <Card className="mb-4 overflow-hidden">
        <div className="border-b border-stone-200/80 px-4 py-3">
          <p className="text-xs font-medium text-amber-700">生成图片</p>
          <h3 className="mt-1 text-lg font-semibold text-slate-900">图片预览</h3>
        </div>

        <div className="p-4 pt-0">
          <div className="relative mt-4 overflow-hidden rounded-[24px] border border-stone-200 bg-gradient-to-br from-amber-100 via-orange-100 to-rose-100">
            {imageSrc ? (
              <div className="h-80">
                <ImageWithFallback
                  src={imageSrc}
                  alt={result.title}
                  className="h-full w-full object-cover"
                />
              </div>
            ) : (
              <div className="flex h-80 flex-col items-center justify-center px-6 text-center">
                <div className="mb-3 rounded-full bg-white/75 p-4 text-amber-700">
                  <ImageIcon className="h-8 w-8" />
                </div>
                <p className="text-base font-semibold text-slate-900">暂无图片</p>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  当前结果没有可展示的图片，请稍后重新生成。
                </p>
              </div>
            )}
          </div>
        </div>
      </Card>

      <Card className="mb-4 p-4">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-amber-700">内容详情</p>
            <h3 className="mt-1 text-xl font-semibold text-slate-900">生成文案</h3>
          </div>
          <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700">
            已保存
          </span>
        </div>

        <h2 className="text-[22px] font-semibold leading-8 text-slate-900">{result.title}</h2>
        <p className="mt-4 text-[15px] leading-8 text-slate-700">{result.content}</p>

        <div className="mt-5 flex flex-wrap gap-2">
          {result.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-stone-100 px-3 py-1.5 text-xs font-medium text-slate-600"
            >
              {tag}
            </span>
          ))}
        </div>
      </Card>

      <Card className="mb-4 p-4">
        <p className="text-xs font-medium text-amber-700">画像摘要</p>
        <div className="mt-3 space-y-4 rounded-2xl bg-stone-50 px-4 py-4 text-sm text-slate-600">
          <div>
            <p className="font-medium text-slate-900">用户画像摘要</p>
            <p className="mt-1 leading-6">{result.profile_summary}</p>
          </div>
          <div>
            <p className="font-medium text-slate-900">生成时间</p>
            <p className="mt-1">{result.created_at}</p>
          </div>
          <div>
            <p className="font-medium text-slate-900">补充说明</p>
            <p className="mt-1 leading-6">{displayInput || "未提供"}</p>
          </div>
          <div>
            <p className="font-medium text-slate-900">目标用户</p>
            <p className="mt-1">{displayTargetUser || "未提供"}</p>
          </div>
          <div>
            <p className="font-medium text-slate-900">兴趣标签</p>
            <p className="mt-1">{displayInterests.join("、") || "未提供"}</p>
          </div>
        </div>
      </Card>

      <div className="mb-5 grid grid-cols-2 gap-3">
        <Button
          variant="outline"
          onClick={() => void handleCopy()}
          className="flex h-auto items-center justify-center gap-2 py-4"
        >
          <Copy className="h-4 w-4 text-amber-700" />
          <span>复制内容</span>
        </Button>
        <Button
          onClick={() => void handleRegenerate()}
          disabled={isRegenerating}
          className="flex h-auto items-center justify-center gap-2 bg-gradient-to-r from-amber-500 to-orange-500 py-4 text-white disabled:opacity-60"
        >
          <RefreshCcw className={`h-4 w-4 ${isRegenerating ? "animate-spin" : ""}`} />
          <span>{isRegenerating ? "正在生成..." : "重新生成"}</span>
        </Button>
      </div>
    </div>
  );
}
