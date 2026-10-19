import { useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { Check, ChevronRight, Sparkles, Wand2 } from "lucide-react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Card } from "./ui/card";
import { Input } from "./ui/input";
import { generateContent, type GenerateResponse } from "../api";

const styleTags = ["理性专业", "活力明快", "高级简洁", "创意表达", "温和治愈", "年轻潮流"];
const scenarioTags = ["社媒图文", "活动宣传", "品牌介绍", "产品推荐", "校园项目", "个人表达"];

export function ProfileInput() {
  const navigate = useNavigate();
  const [selectedStyles, setSelectedStyles] = useState<string[]>([]);
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([]);
  const [interestsText, setInterestsText] = useState("");
  const [targetUser, setTargetUser] = useState("");
  const [inputText, setInputText] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const parsedInterests = useMemo(
    () =>
      interestsText
        .split(/[，、\s]+/)
        .map((item) => item.trim())
        .filter(Boolean),
    [interestsText],
  );

  const toggleTag = (tag: string, type: "style" | "scenario") => {
    if (type === "style") {
      setSelectedStyles((prev) =>
        prev.includes(tag) ? prev.filter((item) => item !== tag) : [...prev, tag],
      );
      return;
    }

    setSelectedScenarios((prev) =>
      prev.includes(tag) ? prev.filter((item) => item !== tag) : [...prev, tag],
    );
  };

  const handleGenerate = async () => {
    if (
      parsedInterests.length === 0 ||
      selectedStyles.length === 0 ||
      selectedScenarios.length === 0 ||
      !targetUser.trim() ||
      !inputText.trim()
    ) {
      setErrorMessage("请先补全兴趣、目标用户、风格、场景和补充说明。");
      return;
    }

    setIsGenerating(true);
    setErrorMessage("");

    try {
      const result: GenerateResponse = await generateContent({
        interests: parsedInterests,
        style: selectedStyles[0],
        scenario: selectedScenarios[0],
        target_user: targetUser.trim(),
        input_text: inputText.trim(),
      });

      navigate("/result", {
        search: `?id=${result.id}`,
        state: {
          result,
          input: inputText.trim(),
          styles: selectedStyles,
          scenarios: selectedScenarios,
          targetUser: targetUser.trim(),
          interests: parsedInterests,
        },
      });
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "生成失败，请稍后再试。");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-full px-5 pb-[calc(96px+env(safe-area-inset-bottom))] pt-8">
      <div className="mb-5 flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.22em] text-amber-700/75">
            Step by Step
          </p>
          <h1 className="mt-1 text-[28px] font-semibold tracking-tight text-slate-900">
            配置内容需求
          </h1>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            告诉系统你想写给谁、发在哪里、想表达什么。
          </p>
        </div>
        <div className="rounded-[22px] bg-white/80 p-3 shadow-[0_10px_30px_rgba(15,23,42,0.08)]">
          <Wand2 className="h-6 w-6 text-amber-600" />
        </div>
      </div>

      <Card className="mb-4 p-4">
        <div className="mb-4 grid grid-cols-3 gap-2">
          {["配置", "生成", "完成"].map((step, index) => (
            <div
              key={step}
              className={`rounded-2xl px-3 py-3 text-center ${
                index === 0 ? "bg-amber-100 text-amber-800" : "bg-stone-100 text-slate-500"
              }`}
            >
              <p className="text-[11px] uppercase tracking-[0.2em]">0{index + 1}</p>
              <p className="mt-1 text-sm font-medium">{step}</p>
            </div>
          ))}
        </div>

        <div className="rounded-2xl bg-stone-50/90 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-500">填写进度</p>
              <h3 className="mt-1 text-base font-semibold text-slate-900">
                已填写 {parsedInterests.length} 个兴趣 / {selectedStyles.length} 个风格 /{" "}
                {selectedScenarios.length} 个场景
              </h3>
            </div>
            <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-amber-700">
              准备中
            </span>
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-600">完成必要信息后即可生成内容。</p>
        </div>
      </Card>

      <Card className="mb-4 p-4">
        <div className="mb-4 flex items-center gap-2">
          <div className="h-5 w-1 rounded-full bg-gradient-to-b from-amber-500 to-orange-500" />
          <h3 className="font-medium text-slate-900">兴趣关键词</h3>
        </div>
        <Input
          value={interestsText}
          onChange={(event) => setInterestsText(event.target.value)}
          placeholder="例如：健身、睡眠、营养"
        />
        <p className="mt-2 text-xs text-slate-500">支持逗号、顿号或空格分隔。</p>
      </Card>

      <Card className="mb-4 p-4">
        <div className="mb-4 flex items-center gap-2">
          <div className="h-5 w-1 rounded-full bg-gradient-to-b from-rose-500 to-orange-500" />
          <h3 className="font-medium text-slate-900">目标用户</h3>
        </div>
        <Input
          value={targetUser}
          onChange={(event) => setTargetUser(event.target.value)}
          placeholder="例如：年轻女性、大学生、职场新人"
        />
      </Card>

      <Card className="mb-4 p-4">
        <div className="mb-4 flex items-center gap-2">
          <div className="h-5 w-1 rounded-full bg-gradient-to-b from-amber-500 to-orange-500" />
          <h3 className="font-medium text-slate-900">内容风格</h3>
        </div>
        <div className="flex flex-wrap gap-2.5">
          {styleTags.map((tag) => (
            <button
              key={tag}
              onClick={() => toggleTag(tag, "style")}
              className={`rounded-2xl px-4 py-2.5 text-sm font-medium transition-all ${
                selectedStyles.includes(tag)
                  ? "bg-stone-900 text-white shadow-[0_12px_24px_rgba(15,23,42,0.18)]"
                  : "bg-stone-100 text-slate-700 hover:bg-stone-200"
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
      </Card>

      <Card className="mb-4 p-4">
        <div className="mb-4 flex items-center gap-2">
          <div className="h-5 w-1 rounded-full bg-gradient-to-b from-rose-500 to-orange-500" />
          <h3 className="font-medium text-slate-900">发布场景</h3>
        </div>
        <div className="flex flex-wrap gap-2.5">
          {scenarioTags.map((tag) => (
            <button
              key={tag}
              onClick={() => toggleTag(tag, "scenario")}
              className={`rounded-2xl px-4 py-2.5 text-sm font-medium transition-all ${
                selectedScenarios.includes(tag)
                  ? "bg-gradient-to-r from-orange-500 to-rose-500 text-white shadow-[0_12px_24px_rgba(249,115,22,0.28)]"
                  : "bg-stone-100 text-slate-700 hover:bg-stone-200"
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
      </Card>

      <Card className="mb-4 p-4">
        <div className="mb-4 flex items-center gap-2">
          <div className="h-5 w-1 rounded-full bg-gradient-to-b from-amber-500 to-rose-500" />
          <h3 className="font-medium text-slate-900">补充说明</h3>
        </div>
        <Textarea
          placeholder="例如：希望内容更轻松自然，适合作为社交平台图文封面，突出重点信息和整体氛围。"
          value={inputText}
          onChange={(event) => setInputText(event.target.value)}
          className="min-h-36 resize-none"
        />
        <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
          <span>补充越具体，生成结果通常会更贴近预期。</span>
          <span>{inputText.length} / 500</span>
        </div>
      </Card>

      <Card className="mb-5 p-4">
        <h3 className="text-base font-semibold text-slate-900">生成准备</h3>
        <div className="mt-3 space-y-2">
          {[
            ["已填写兴趣关键词", parsedInterests.length > 0],
            ["已填写目标用户", targetUser.trim().length > 0],
            ["已选择至少 1 个风格", selectedStyles.length > 0],
            ["已选择至少 1 个场景", selectedScenarios.length > 0],
            ["已填写补充说明", inputText.trim().length > 0],
          ].map(([label, done]) => (
            <div key={label} className="flex items-center gap-3 rounded-2xl bg-stone-50 px-3 py-3">
              <div
                className={`flex h-6 w-6 items-center justify-center rounded-full ${
                  done ? "bg-emerald-100 text-emerald-600" : "bg-stone-200 text-stone-500"
                }`}
              >
                <Check className="h-3.5 w-3.5" />
              </div>
              <span className="text-sm text-slate-700">{label}</span>
            </div>
          ))}
        </div>
      </Card>

      <div className="rounded-[28px] border border-white/70 bg-white/88 p-4 shadow-[0_18px_45px_rgba(15,23,42,0.08)] backdrop-blur-sm">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-amber-700/75">
          Ready to Generate
        </p>
        <div className="mb-4 mt-1">
          <h3 className="text-lg font-semibold text-slate-900">准备生成</h3>
          <p className="mt-1 text-sm leading-6 text-slate-600">
            确认信息无误后，系统将生成标题、正文、标签和配图。
          </p>
        </div>

        {errorMessage ? (
          <div className="mb-4 rounded-2xl bg-rose-50 px-3 py-3 text-sm text-rose-600">
            {errorMessage}
          </div>
        ) : null}

        <Button
          onClick={handleGenerate}
          disabled={
            parsedInterests.length === 0 ||
            selectedStyles.length === 0 ||
            selectedScenarios.length === 0 ||
            !targetUser.trim() ||
            !inputText.trim() ||
            isGenerating
          }
          className="w-full bg-gradient-to-r from-amber-500 to-orange-500 text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isGenerating ? (
            <>
              <div className="mr-2 h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
              正在生成...
            </>
          ) : (
            <>
              <Sparkles className="h-5 w-5" />
              开始生成
              <ChevronRight className="h-5 w-5" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
