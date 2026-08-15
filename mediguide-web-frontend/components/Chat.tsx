"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { askMediGuide, ApiError } from "@/lib/api";
import type { ChatMessage, ChatSession } from "@/lib/chatStore";
import { uid } from "@/lib/chatStore";
import CitationCard from "./CitationCard";
import PulseDivider from "./PulseDivider";
import VitalsBadge from "./VitalsBadge";
import { MenuIcon } from "./icons";

type Theme = "light" | "dark";
type Message = ChatMessage;

const TYPE_SPEED = 18;

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

export default function Chat({
  session,
  onMessagesChange,
  theme,
  onToggleTheme,
  onOpenSidebar,
}: {
  session: ChatSession;
  onMessagesChange: (messages: Message[]) => void;
  theme: Theme;
  onToggleTheme: () => void;
  onOpenSidebar: () => void;
}) {
  const messages = session.messages;
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [activeTraceId, setActiveTraceId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const lastAssistant = [...session.messages].reverse().find((m) => m.role === "assistant");
    setActiveTraceId(lastAssistant ? lastAssistant.id : null);
    setInput("");
  }, [session.id]);

  useEffect(() => {
    const container = scrollRef.current;
    if (!container) return;
    container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
  }, [messages.length, loading, session.id]);

  useEffect(() => {
    if (!loading) return;
    setStepIndex(0);
    const interval = window.setInterval(() => {
      setStepIndex((index) => Math.min(index + 1, STEP_LABELS.length - 1));
    }, 1300);
    return () => window.clearInterval(interval);
  }, [loading]);

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    const userMessage: Message = { role: "user", content: trimmed, id: uid() };
    onMessagesChange([...messages, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const result = await askMediGuide(trimmed);
      const assistantId = uid();
      onMessagesChange([
        ...messages,
        userMessage,
        { role: "assistant", content: result.answer, id: assistantId, meta: result },
      ]);
      setActiveTraceId(assistantId);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Something went wrong.";
      onMessagesChange([
        ...messages,
        userMessage,
        { role: "assistant", content: "", id: uid(), error: message },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function clearChat() {
    onMessagesChange([]);
    setActiveTraceId(null);
  }

  const activeTrace = [...messages].reverse().find(
    (message): message is Extract<Message, { role: "assistant" }> =>
      message.role === "assistant" && message.id === activeTraceId
  );

  return (
    <div className="relative flex min-h-screen flex-1 flex-col px-4 pb-6 pt-5 sm:px-6 lg:px-8">
      <DecorativeBackground />

      <div className="relative flex min-h-0 flex-1 flex-col gap-5">
        <Header
          theme={theme}
          onToggleTheme={onToggleTheme}
          onClearChat={clearChat}
          onOpenSidebar={onOpenSidebar}
        />
        <PulseDivider active={loading} className="-mt-1" />

        <section className="grid min-h-0 flex-1 grid-cols-1 gap-5 xl:grid-cols-[1.45fr_0.95fr]">
          <div
            key={session.id}
            className="aurora-band glass-card glow-accent flex min-h-0 flex-col overflow-hidden rounded-[28px] border border-white/40 shadow-[0_24px_80px_rgba(22,38,43,0.12)] backdrop-blur-xl dark:border-white/10 dark:shadow-[0_24px_80px_rgba(0,0,0,0.35)]"
          >
            <div className="border-b border-white/30 px-5 py-4 dark:border-white/10">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-mono text-[11px] uppercase tracking-[0.35em] text-violet dark:text-violet/70">
                    Grounded medical copilot
                  </p>
                  <p className="mt-1 text-sm text-ink-soft dark:text-white/70">
                    Answers are verified against retrieved guideline text before display.
                  </p>
                </div>
                <div className="flex items-center gap-2 text-[11px] font-mono uppercase tracking-[0.28em] text-ink-soft/70 dark:text-white/50">
                  <span className="h-2 w-2 rounded-full bg-coral shadow-[0_0_0_4px_rgba(227,93,79,0.18)]" />
                  Persistent session active
                </div>
              </div>
            </div>

            <div ref={scrollRef} className="scrollbar-thin flex-1 space-y-4 overflow-y-auto px-4 py-5 sm:px-5">
              {messages.length === 0 && <EmptyState onPick={send} />}

              {messages.map((message) =>
                message.role === "user" ? (
                  <UserBubble key={message.id} content={message.content} />
                ) : (
                  <AssistantBubble
                    key={message.id}
                    message={message}
                    isActiveTrace={message.id === activeTraceId}
                    animateTypewriter={!message.error && message.id === activeTraceId && !loading}
                    onSelectTrace={() => setActiveTraceId(message.id)}
                  />
                )
              )}

              {loading && <ThinkingBubble label={STEP_LABELS[stepIndex]} />}
            </div>

            <Composer
              input={input}
              setInput={setInput}
              onSend={() => send(input)}
              onClear={clearChat}
              disabled={loading}
            />
          </div>

          <aside className="flex min-h-0 flex-col gap-5">
            <div className="aurora-band glass-card overflow-hidden rounded-[28px] border border-white/35 p-5 shadow-[0_18px_60px_rgba(22,38,43,0.1)] backdrop-blur-xl dark:border-white/10 dark:shadow-[0_18px_60px_rgba(0,0,0,0.28)]">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="font-mono text-[11px] uppercase tracking-[0.35em] text-sky dark:text-sky/70">
                    This conversation
                  </p>
                  <h2 className="mt-1 truncate text-lg font-semibold text-ink dark:text-white">
                    {session.title}
                  </h2>
                </div>
                <span className="shrink-0 rounded-full border border-violet/20 bg-violet-soft px-3 py-1 text-[11px] font-mono uppercase tracking-[0.22em] text-violet dark:border-violet/30 dark:bg-violet/15 dark:text-violet/90">
                  saved
                </span>
              </div>

              <div className="mt-4 grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                <InfoChip label="Theme" value={theme === "dark" ? "Dark" : "Light"} />
                <InfoChip label="Messages" value={`${messages.length}`} />
                <InfoChip label="Trace" value={activeTrace ? "Selected" : "Idle"} />
              </div>
            </div>

            <div className="glass-card flex min-h-0 flex-1 flex-col overflow-hidden rounded-[28px] border border-white/35 p-5 shadow-[0_18px_60px_rgba(22,38,43,0.1)] backdrop-blur-xl dark:border-white/10 dark:shadow-[0_18px_60px_rgba(0,0,0,0.28)]">
              <TracePanel trace={activeTrace} />
            </div>
          </aside>
        </section>
      </div>
    </div>
  );
}

function DecorativeBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="floating-orb absolute left-[-6rem] top-[-4rem] h-56 w-56 rounded-full bg-coral/18 blur-3xl" />
      <div className="floating-orb absolute right-[-4rem] top-16 h-72 w-72 rounded-full bg-violet/18 blur-3xl [animation-delay:-3s]" />
      <div className="floating-orb absolute left-[18%] bottom-[8%] h-56 w-56 rounded-full bg-sky/12 blur-3xl [animation-delay:-5s]" />
      <div className="absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-paper/90 via-paper/40 to-transparent dark:from-[#071114]/90 dark:via-[#071114]/45" />
    </div>
  );
}

function Header({
  theme,
  onToggleTheme,
  onClearChat,
  onOpenSidebar,
}: {
  theme: Theme;
  onToggleTheme: () => void;
  onClearChat: () => void;
  onOpenSidebar: () => void;
}) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-3">
      <div className="flex max-w-2xl items-start gap-3">
        <button
          onClick={onOpenSidebar}
          aria-label="Open chat history"
          className="mt-1 shrink-0 rounded-xl border border-white/40 bg-white/70 p-2 text-ink-soft transition hover:bg-white/90 dark:border-white/10 dark:bg-white/5 dark:text-white/70 dark:hover:bg-white/10 lg:hidden"
        >
          <MenuIcon className="h-4 w-4" />
        </button>
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.35em] text-violet dark:text-violet/70">
            MediGuide LK
          </p>
          <h1 className="mt-2 font-display text-4xl font-semibold tracking-tight text-ink dark:text-white sm:text-5xl">
            A colorful medical chat interface with grounded answers.
          </h1>
          <p className="mt-3 max-w-xl text-sm leading-6 text-ink-soft dark:text-white/70 sm:text-[15px]">
            Type naturally, review the retrieved evidence, and keep every conversation saved to its own thread.
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <button
          onClick={onToggleTheme}
          className="rounded-full border border-white/40 bg-gradient-to-r from-teal-soft via-violet-soft to-sky-soft px-4 py-2 text-sm font-medium text-ink transition hover:-translate-y-0.5 hover:shadow-[0_10px_24px_rgba(120,87,229,0.18)] dark:border-white/10 dark:bg-white/5 dark:text-white dark:hover:bg-white/10"
        >
          {theme === "dark" ? "Light mode" : "Dark mode"}
        </button>
        <button
          onClick={onClearChat}
          className="rounded-full border border-white/40 bg-gradient-to-r from-coral-soft to-gold-soft px-4 py-2 text-sm font-medium text-ink transition hover:-translate-y-0.5 hover:shadow-[0_10px_24px_rgba(227,93,79,0.18)] dark:border-white/10 dark:bg-white/5 dark:text-white dark:hover:bg-white/10"
        >
          Clear this chat
        </button>
      </div>
    </header>
  );
}

function EmptyState({ onPick }: { onPick: (q: string) => void }) {
  return (
    <div className="flex min-h-[360px] animate-rise flex-col items-center justify-center gap-6 rounded-[24px] border border-white/40 bg-gradient-to-br from-coral-soft/80 via-violet-soft/70 to-sky-soft/70 px-5 py-10 text-center shadow-[0_20px_50px_rgba(120,87,229,0.12)] dark:border-white/10 dark:from-coral/10 dark:via-violet/10 dark:to-sky/10">
      <div className="max-w-2xl space-y-3">
        <p className="font-display text-2xl italic text-ink dark:text-white sm:text-3xl">
          Describe how you feel, or ask about a condition. I’ll answer only from verified guideline documents.
        </p>
        <p className="text-sm leading-6 text-ink-soft dark:text-white/65">
          Each conversation is saved as its own thread in the sidebar, so you can pick up where you left off.
        </p>
      </div>
      <div className="grid w-full max-w-2xl gap-3 sm:grid-cols-3">
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onPick(suggestion)}
            className="rounded-2xl border border-white/50 bg-white/80 px-4 py-3 text-left text-sm text-ink-soft transition hover:-translate-y-0.5 hover:shadow-[0_12px_24px_rgba(47,143,232,0.12)] dark:border-white/10 dark:bg-white/5 dark:text-white/70 dark:hover:bg-white/10"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}

function UserBubble({ content }: { content: string }) {
  return (
    <div className="flex justify-end animate-rise">
      <div className="max-w-[82%] rounded-3xl rounded-tr-sm bg-gradient-to-br from-violet via-teal to-sky px-4 py-3 text-[14px] leading-relaxed text-paper shadow-[0_12px_30px_rgba(120,87,229,0.24)]">
        {content}
      </div>
    </div>
  );
}

function AssistantBubble({
  message,
  isActiveTrace,
  animateTypewriter,
  onSelectTrace,
}: {
  message: Extract<Message, { role: "assistant" }>;
  isActiveTrace: boolean;
  animateTypewriter: boolean;
  onSelectTrace: () => void;
}) {
  const [visibleText, setVisibleText] = useState(animateTypewriter ? "" : message.content);

  useEffect(() => {
    if (!animateTypewriter) {
      setVisibleText(message.content);
      return;
    }

    setVisibleText("");
    let index = 0;
    const timer = window.setInterval(() => {
      index += Math.max(1, Math.ceil(message.content.length / 50));
      if (index >= message.content.length) {
        setVisibleText(message.content);
        window.clearInterval(timer);
        return;
      }
      setVisibleText(message.content.slice(0, index));
    }, TYPE_SPEED);

    return () => window.clearInterval(timer);
  }, [animateTypewriter, message.content]);

  if (message.error) {
    return (
      <div className="flex justify-start animate-rise">
        <div className="max-w-[85%] rounded-3xl rounded-tl-sm border border-amber/30 bg-amber-soft px-4 py-3 text-[14px] leading-relaxed text-amber dark:bg-amber/10 dark:text-amber/90">
          {message.error}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start animate-rise">
      <button
        onClick={onSelectTrace}
        className={`max-w-[85%] rounded-3xl rounded-tl-sm border px-4 py-3 text-left text-[14px] leading-relaxed transition ${
          isActiveTrace
            ? "border-teal/30 bg-white/90 dark:border-teal/30 dark:bg-white/10"
            : "border-black/8 bg-white/70 hover:border-teal/20 dark:border-white/10 dark:bg-white/5"
        }`}
      >
        <div className="prose-chat text-ink dark:text-white/85">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{visibleText}</ReactMarkdown>
        </div>
        {message.meta && (
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <VitalsBadge faithful={message.meta.faithful} needsReview={message.meta.needs_review} />
            {message.meta.citations.length > 0 && (
              <span className="font-mono text-[11px] text-violet dark:text-violet/70">
                {message.meta.citations.length} source{message.meta.citations.length > 1 ? "s" : ""} · view trace →
              </span>
            )}
          </div>
        )}
        {message.meta && (
          <div className="mt-3 border-t border-black/5 pt-3 dark:border-white/10 lg:hidden">
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
      <div className="flex items-center gap-2 rounded-3xl rounded-tl-sm border border-white/50 bg-white/80 px-4 py-2.5 text-[13px] text-ink-soft shadow-[0_12px_28px_rgba(120,87,229,0.08)] backdrop-blur dark:border-white/10 dark:bg-white/5 dark:text-white/65 dark:shadow-none">
        <span className="flex gap-1">
          <span className="h-1.5 w-1.5 animate-blink rounded-full bg-coral [animation-delay:-0.2s]" />
          <span className="h-1.5 w-1.5 animate-blink rounded-full bg-violet [animation-delay:-0.1s]" />
          <span className="h-1.5 w-1.5 animate-blink rounded-full bg-sky" />
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
  onClear,
  disabled,
}: {
  input: string;
  setInput: (value: string) => void;
  onSend: () => void;
  onClear: () => void;
  disabled: boolean;
}) {
  return (
    <div className="border-t border-white/40 p-4 dark:border-white/10">
      <div className="rounded-[24px] border border-white/50 bg-gradient-to-r from-white/85 via-white/75 to-white/85 p-3 shadow-[0_14px_40px_rgba(120,87,229,0.08)] backdrop-blur focus-within:border-violet/40 dark:border-white/10 dark:bg-white/5 dark:shadow-none">
        <div className="flex items-end gap-3">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                onSend();
              }
            }}
            rows={1}
            placeholder="Describe symptoms, ask for a condition summary, or paste markdown notes…"
            className="max-h-36 flex-1 resize-none bg-transparent px-2 py-2 text-[14px] leading-6 text-ink placeholder:text-ink-soft/45 focus:outline-none dark:text-white dark:placeholder:text-white/35"
          />
          <button
            onClick={onSend}
            disabled={disabled || !input.trim()}
            className="shrink-0 rounded-2xl bg-gradient-to-br from-coral via-violet to-sky px-4 py-2.5 text-[13px] font-semibold text-paper shadow-[0_12px_28px_rgba(120,87,229,0.25)] transition hover:-translate-y-0.5 active:scale-95 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Send
          </button>
        </div>
        <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-white/40 px-2 pt-3 text-[11px] text-ink-soft/60 dark:border-white/10 dark:text-white/45">
          <span>Enter to send, Shift+Enter for a newline.</span>
          <button onClick={onClear} className="font-medium text-violet hover:underline dark:text-violet/80">
            Reset conversation
          </button>
        </div>
      </div>
      <p className="mt-2 px-1 text-[11px] text-ink-soft/60 dark:text-white/45">
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
      <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
        <p className="font-mono text-[11px] uppercase tracking-[0.35em] text-violet dark:text-violet/70">
          Retrieval Trace
        </p>
        <p className="max-w-[240px] text-[13px] leading-6 text-ink-soft/70 dark:text-white/60">
          Ask a question - the guideline passages behind the answer will show up here.
        </p>
      </div>
    );
  }

  const { meta } = trace;

  return (
    <div className={compact ? "" : "flex h-full flex-col"}>
      {!compact && (
        <p className="mb-3 font-mono text-[11px] uppercase tracking-[0.35em] text-violet dark:text-violet/70">
          Retrieval Trace
        </p>
      )}

      <div className={compact ? "space-y-3" : "space-y-4 overflow-y-auto scrollbar-thin"}>
        <div>
          <p className="font-mono text-[10px] uppercase tracking-wider text-sky dark:text-sky/70">
            {meta.is_informational ? "Question" : "Extracted symptoms"}
          </p>
          <p className="mt-1 text-[13px] leading-6 text-ink dark:text-white/85">{meta.structured_symptoms}</p>
        </div>

        {meta.unsupported_claims.length > 0 && (
          <div className="rounded-2xl border border-coral/20 bg-coral-soft p-3 dark:bg-coral/10">
            <p className="font-mono text-[10px] uppercase tracking-wider text-coral">
              Flagged claims
            </p>
            <ul className="mt-1 list-disc space-y-1 pl-4 text-[13px] leading-6 text-coral/90 dark:text-coral/85">
              {meta.unsupported_claims.map((claim, index) => (
                <li key={`${claim}-${index}`}>{claim}</li>
              ))}
            </ul>
          </div>
        )}

        <div>
          <p className="font-mono text-[10px] uppercase tracking-wider text-violet dark:text-violet/70">
            Sources ({meta.citations.length})
          </p>
          <div className="mt-2 space-y-2">
            {meta.citations.length === 0 ? (
              <p className="text-[13px] leading-6 text-ink-soft/60 dark:text-white/45">
                No supporting passages were retrieved.
              </p>
            ) : (
              meta.citations.map((citation, index) => (
                <CitationCard key={`${citation.source}-${index}`} citation={citation} index={index + 1} />
              ))
            )}
          </div>
        </div>

        <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft/50 dark:text-white/40">
          {meta.response_time_seconds}s response time
        </p>
      </div>
    </div>
  );
}

function InfoChip({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/40 bg-white/78 px-4 py-3 shadow-[0_10px_22px_rgba(120,87,229,0.06)] dark:border-white/10 dark:bg-white/5">
      <p className="font-mono text-[10px] uppercase tracking-[0.3em] text-violet dark:text-violet/60">
        {label}
      </p>
      <p className="mt-2 text-sm font-semibold text-ink dark:text-white">{value}</p>
    </div>
  );
}