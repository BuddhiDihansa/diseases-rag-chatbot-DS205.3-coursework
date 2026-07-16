"use client";

import { useEffect, useRef, useState } from "react";
import { askMediGuide, ApiError, type ChatResponse } from "@/lib/api";
import PulseDivider from "./PulseDivider";
import VitalsBadge from "./VitalsBadge";
import CitationCard from "./CitationCard";

type Message =
  | { role: "user"; content: string; id: string }
  | {
      role: "assistant";
      content: string;
      id: string;
      meta?: ChatResponse;
      error?: string;
    };

const STEP_LABELS = [
  "Reading your message…",
  "Searching clinical guidelines…",
  "Drafting a grounded answer…",
  "Checking the answer against sources…",
];

const SUGGESTIONS = [
  "What are the symptoms of Dengue fever?",
  "What precautions should a diabetic patient take with their diet?",
  "What are the warning signs of a heart attack?",
];

function uid() {
  return Math.random().toString(36).slice(2, 10);
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [activeTraceId, setActiveTraceId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, loading]);

  useEffect(() => {
    if (!loading) return;
    setStepIndex(0);
    const interval = setInterval(() => {
      setStepIndex((i) => Math.min(i + 1, STEP_LABELS.length - 1));
    }, 1400);
    return () => clearInterval(interval);
  }, [loading]);

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    const userMsg: Message = { role: "user", content: trimmed, id: uid() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const result = await askMediGuide(trimmed);
      const assistantId = uid();
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: result.answer,
          id: assistantId,
          meta: result,
        },
      ]);
      setActiveTraceId(assistantId);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Something went wrong.";
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "", id: uid(), error: message },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const activeTrace = messages.find(
    (m): m is Extract<Message, { role: "assistant" }> =>
      m.role === "assistant" && m.id === activeTraceId
  );

  return (
    <div className="mx-auto flex h-screen max-w-6xl flex-col px-4 pb-4 pt-6 sm:px-6">
      <Header />
      <PulseDivider active={loading} className="mb-4" />

      <div className="grid min-h-0 flex-1 grid-cols-1 gap-5 lg:grid-cols-[1fr_340px]">
        {/* Conversation */}
        <div className="flex min-h-0 flex-col rounded-2xl border border-hairline bg-white/50 shadow-card">
          <div
            ref={scrollRef}
            className="scrollbar-thin flex-1 space-y-4 overflow-y-auto p-5"
          >
            {messages.length === 0 && (
              <EmptyState onPick={(q) => send(q)} />
            )}

            {messages.map((m) =>
              m.role === "user" ? (
                <UserBubble key={m.id} content={m.content} />
              ) : (
                <AssistantBubble
                  key={m.id}
                  message={m}
                  isActiveTrace={m.id === activeTraceId}
                  onSelectTrace={() => setActiveTraceId(m.id)}
                />
              )
            )}

            {loading && <ThinkingBubble label={STEP_LABELS[stepIndex]} />}
          </div>

          <Composer
            input={input}
            setInput={setInput}
            onSend={() => send(input)}
            disabled={loading}
          />
        </div>

        {/* Retrieval trace panel - desktop only, mobile gets it inline */}
        <aside className="hidden min-h-0 flex-col rounded-2xl border border-hairline bg-panel/60 p-5 shadow-card lg:flex">
          <TracePanel trace={activeTrace} />
        </aside>
      </div>
    </div>
  );
}

function Header() {
  return (
    <header className="mb-1 flex items-baseline justify-between">
      <div>
        <h1 className="font-display text-2xl font-medium tracking-tight text-ink">
          MediGuide <span className="italic text-teal">LK</span>
        </h1>
        <p className="mt-0.5 text-[13px] text-ink-soft">
          Grounded answers from verified clinical guideline documents.
        </p>
      </div>
      <span className="hidden font-mono text-[11px] uppercase tracking-widest text-ink-soft/70 sm:block">
        Retrieval-Augmented · Multi-Agent
      </span>
    </header>
  );
}

function EmptyState({ onPick }: { onPick: (q: string) => void }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-5 py-10 text-center">
      <div className="max-w-sm">
        <p className="font-display text-lg italic text-ink-soft">
          "Describe how you feel, or ask about a condition -
          I'll answer only from verified guideline documents."
        </p>
      </div>
      <div className="flex flex-col gap-2 w-full max-w-md">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => onPick(s)}
            className="rounded-xl border border-hairline bg-white/70 px-4 py-2.5 text-left text-sm text-ink-soft transition hover:border-teal/40 hover:text-ink"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}

function UserBubble({ content }: { content: string }) {
  return (
    <div className="flex justify-end animate-rise">
      <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-teal px-4 py-2.5 text-[14px] leading-relaxed text-paper">
        {content}
      </div>
    </div>
  );
}

function AssistantBubble({
  message,
  isActiveTrace,
  onSelectTrace,
}: {
  message: Extract<Message, { role: "assistant" }>;
  isActiveTrace: boolean;
  onSelectTrace: () => void;
}) {
  if (message.error) {
    return (
      <div className="flex justify-start animate-rise">
        <div className="max-w-[85%] rounded-2xl rounded-tl-sm border border-amber/30 bg-amber-soft px-4 py-2.5 text-[14px] leading-relaxed text-amber">
          {message.error}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start animate-rise">
      <button
        onClick={onSelectTrace}
        className={`max-w-[85%] rounded-2xl rounded-tl-sm border px-4 py-3 text-left text-[14px] leading-relaxed transition ${
          isActiveTrace
            ? "border-teal/30 bg-white"
            : "border-hairline bg-white/60 hover:border-teal/20"
        }`}
      >
        <p className="whitespace-pre-line text-ink">{message.content}</p>
        {message.meta && (
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <VitalsBadge
              faithful={message.meta.faithful}
              needsReview={message.meta.needs_review}
            />
            {message.meta.citations.length > 0 && (
              <span className="font-mono text-[11px] text-ink-soft/70">
                {message.meta.citations.length} source
                {message.meta.citations.length > 1 ? "s" : ""} · view trace →
              </span>
            )}
          </div>
        )}
        {/* Inline trace for mobile, where the side panel is hidden */}
        {message.meta && (
          <div className="mt-3 border-t border-hairline pt-3 lg:hidden">
            <TracePanel trace={message} compact />
          </div>
        )}
      </button>
    </div>
  );
}

function ThinkingBubble({ label }: { label: string }) {
  return (
    <div className="flex justify-start animate-rise">
      <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm border border-hairline bg-white/60 px-4 py-2.5 text-[13px] text-ink-soft">
        <span className="flex gap-1">
          <span className="h-1.5 w-1.5 animate-blink rounded-full bg-teal [animation-delay:-0.2s]" />
          <span className="h-1.5 w-1.5 animate-blink rounded-full bg-teal [animation-delay:-0.1s]" />
          <span className="h-1.5 w-1.5 animate-blink rounded-full bg-teal" />
        </span>
        {label}
      </div>
    </div>
  );
}

function Composer({
  input,
  setInput,
  onSend,
  disabled,
}: {
  input: string;
  setInput: (v: string) => void;
  onSend: () => void;
  disabled: boolean;
}) {
  return (
    <div className="border-t border-hairline p-3">
      <div className="flex items-end gap-2 rounded-xl border border-hairline bg-white px-3 py-2 focus-within:border-teal/50">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
          rows={1}
          placeholder="Describe your symptoms, or ask about a condition…"
          className="max-h-32 flex-1 resize-none bg-transparent py-1.5 text-[14px] text-ink placeholder:text-ink-soft/50 focus:outline-none"
        />
        <button
          onClick={onSend}
          disabled={disabled || !input.trim()}
          className="shrink-0 rounded-lg bg-teal px-3.5 py-1.5 text-[13px] font-medium text-paper transition hover:bg-teal-dark disabled:cursor-not-allowed disabled:opacity-40"
        >
          Send
        </button>
      </div>
      <p className="mt-2 px-1 text-[11px] text-ink-soft/60">
        Informational only — not a substitute for professional medical advice.
      </p>
    </div>
  );
}

function TracePanel({
  trace,
  compact = false,
}: {
  trace?: Extract<Message, { role: "assistant" }>;
  compact?: boolean;
}) {
  if (!trace || !trace.meta) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-center">
        <p className="font-mono text-[11px] uppercase tracking-widest text-ink-soft/60">
          Retrieval Trace
        </p>
        <p className="max-w-[220px] text-[13px] text-ink-soft/70">
          Ask a question - the guideline passages behind the answer will
          show up here.
        </p>
      </div>
    );
  }

  const { meta } = trace;

  return (
    <div className={compact ? "" : "flex h-full flex-col"}>
      {!compact && (
        <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-ink-soft/60">
          Retrieval Trace
        </p>
      )}

      <div className={compact ? "space-y-3" : "space-y-4 overflow-y-auto scrollbar-thin"}>
        <div>
          <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft/60">
            {meta.is_informational ? "Question" : "Extracted symptoms"}
          </p>
          <p className="mt-1 text-[13px] text-ink">{meta.structured_symptoms}</p>
        </div>

        {meta.unsupported_claims.length > 0 && (
          <div className="rounded-lg border border-amber/30 bg-amber-soft p-3">
            <p className="font-mono text-[10px] uppercase tracking-wider text-amber">
              Flagged claims
            </p>
            <ul className="mt-1 list-disc space-y-1 pl-4 text-[13px] text-amber/90">
              {meta.unsupported_claims.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </div>
        )}

        <div>
          <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft/60">
            Sources ({meta.citations.length})
          </p>
          <div className="mt-2 space-y-2">
            {meta.citations.length === 0 ? (
              <p className="text-[13px] text-ink-soft/60">
                No supporting passages were retrieved.
              </p>
            ) : (
              meta.citations.map((c, i) => (
                <CitationCard key={i} citation={c} index={i + 1} />
              ))
            )}
          </div>
        </div>

        <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft/50">
          {meta.response_time_seconds}s response time
        </p>
      </div>
    </div>
  );
}
