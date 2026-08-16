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
    <div className="relative flex min-h-screen flex-1 flex-col">
      <div className="ambient-glow" />
      <PulseDivider active={loading} />

      <div className="relative z-10 flex min-h-0 flex-1 flex-col gap-5 px-4 pb-6 pt-5 sm:px-6 lg:px-8">
        <Header onOpenSidebar={onOpenSidebar} sessionTitle={session.title} />

        <section className="grid min-h-0 flex-1 grid-cols-1 gap-5 xl:grid-cols-[1.6fr_1fr]">
          <div className="glass-card flex min-h-0 flex-col overflow-hidden rounded-2xl">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-hairline px-5 py-3.5 dark:border-navy-border">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-primary" />
                <p className="text-[13px] font-medium text-ink-soft dark:text-white/60">
                  Answers are checked against retrieved guideline text
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={onToggleTheme}
                  className="rounded-lg border border-hairline px-3 py-1.5 text-[12px] font-medium text-ink-soft transition hover:border-primary/40 hover:text-ink dark:border-navy-border dark:text-white/60 dark:hover:border-primary/40 dark:hover:text-white"
                >
                  {theme === "dark" ? "Light mode" : "Dark mode"}
                </button>
                <button
                  onClick={clearChat}
                  className="rounded-lg border border-hairline px-3 py-1.5 text-[12px] font-medium text-ink-soft transition hover:border-rose/40 hover:text-rose dark:border-navy-border dark:text-white/60"
                >
                  Clear
                </button>
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
              disabled={loading}
            />
          </div>

          <aside className="glass-card flex min-h-0 flex-col overflow-hidden rounded-2xl">
            <div className="border-b border-hairline px-5 py-3.5 dark:border-navy-border">
              <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-accent">
                Retrieval trace
              </p>
              <p className="mt-1 truncate text-[13px] text-ink-soft dark:text-white/50">
                {messages.length} message{messages.length === 1 ? "" : "s"} in this chat
              </p>
            </div>
            <div className="scrollbar-thin flex-1 overflow-y-auto px-5 py-4">
              <TracePanel trace={activeTrace} />
            </div>
          </aside>
        </section>
      </div>
    </div>
  );
}

function Header({
  onOpenSidebar,
  sessionTitle,
}: {
  onOpenSidebar: () => void;
  sessionTitle: string;
}) {
  return (
    <header className="flex items-center gap-3">
      <button
        onClick={onOpenSidebar}
        aria-label="Open chat history"
        className="shrink-0 rounded-lg border border-hairline p-2 text-ink-soft transition hover:border-primary/40 dark:border-navy-border dark:text-white/60 lg:hidden"
      >
        <MenuIcon className="h-4 w-4" />
      </button>
      <div className="min-w-0">
        <p className="font-mono text-[11px] uppercase tracking-[0.3em] text-primary">
          MediGuide LK
        </p>
        <h1 className="truncate font-display text-xl font-bold text-ink dark:text-white sm:text-2xl">
          {sessionTitle}
        </h1>
      </div>
    </header>
  );
}

function EmptyState({ onPick }: { onPick: (q: string) => void }) {
  return (
    <div className="flex min-h-[340px] animate-rise flex-col items-center justify-center gap-6 rounded-xl border border-dashed border-hairline px-5 py-10 text-center dark:border-navy-border">
      <div className="max-w-lg space-y-2">
        <p className="font-display text-xl font-semibold text-ink dark:text-white">
          Describe how you feel, or ask about a condition
        </p>
        <p className="text-sm leading-6 text-ink-soft dark:text-white/50">
          I answer only from verified guideline documents, and show you exactly which passages I used.
        </p>
      </div>
      <div className="grid w-full max-w-xl gap-2.5 sm:grid-cols-3">
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onPick(suggestion)}
            className="rounded-xl border border-hairline bg-paper px-3.5 py-3 text-left text-[13px] leading-snug text-ink-soft transition hover:border-primary/40 hover:text-ink dark:border-navy-border dark:bg-white/[0.02] dark:text-white/60 dark:hover:border-primary/40 dark:hover:text-white"
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
      <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-primary px-4 py-2.5 text-[14px] leading-relaxed text-white">
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
        <div className="max-w-[85%] rounded-2xl rounded-tl-sm border border-rose/25 bg-rose-soft px-4 py-2.5 text-[14px] leading-relaxed text-rose dark:bg-rose/10">
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
            ? "border-primary/30 bg-primary-soft/40 dark:bg-primary/10"
            : "border-hairline bg-paper hover:border-primary/25 dark:border-navy-border dark:bg-white/[0.02]"
        }`}
      >
        <div className="prose-chat text-ink dark:text-white/85">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{visibleText}</ReactMarkdown>
        </div>
        {message.meta && (
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <VitalsBadge faithful={message.meta.faithful} needsReview={message.meta.needs_review} />
            {message.meta.citations.length > 0 && (
              <span className="font-mono text-[11px] text-accent">
                {message.meta.citations.length} source{message.meta.citations.length > 1 ? "s" : ""} · view trace →
              </span>
            )}
          </div>
        )}
        {message.meta && (
          <div className="mt-3 border-t border-hairline pt-3 dark:border-navy-border xl:hidden">
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
      <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm border border-hairline bg-paper px-4 py-2.5 text-[13px] text-ink-soft dark:border-navy-border dark:bg-white/[0.02] dark:text-white/55">
        <span className="flex gap-1">
          <span className="h-1.5 w-1.5 animate-blink rounded-full bg-primary [animation-delay:-0.2s]" />
          <span className="h-1.5 w-1.5 animate-blink rounded-full bg-primary [animation-delay:-0.1s]" />
          <span className="h-1.5 w-1.5 animate-blink rounded-full bg-primary" />
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
  setInput: (value: string) => void;
  onSend: () => void;
  disabled: boolean;
}) {
  return (
    <div className="border-t border-hairline p-4 dark:border-navy-border">
      <div className="rounded-xl border border-hairline bg-paper p-2.5 focus-within:border-primary/50 dark:border-navy-border dark:bg-white/[0.02]">
        <div className="flex items-end gap-2.5">
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
            placeholder="Describe symptoms, ask for a condition summary…"
            className="max-h-36 flex-1 resize-none bg-transparent px-2 py-1.5 text-[14px] leading-6 text-ink placeholder:text-ink-soft/50 focus:outline-none dark:text-white dark:placeholder:text-white/30"
          />
          <button
            onClick={onSend}
            disabled={disabled || !input.trim()}
            className="shrink-0 rounded-lg bg-primary px-4 py-2 text-[13px] font-semibold text-white transition hover:bg-primary-dark active:scale-95 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Send
          </button>
        </div>
      </div>
      <p className="mt-2 px-1 text-[11px] text-ink-soft/60 dark:text-white/35">
        Enter to send, Shift+Enter for a newline. Informational only — not a substitute for professional medical advice.
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
      <div className="flex h-full flex-col items-center justify-center gap-2 py-8 text-center">
        <p className="max-w-[220px] text-[13px] leading-6 text-ink-soft/70 dark:text-white/40">
          Ask a question — the guideline passages behind the answer will show up here.
        </p>
      </div>
    );
  }

  const { meta } = trace;

  return (
    <div className={compact ? "space-y-3" : "space-y-4"}>
      <div>
        <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft/60 dark:text-white/35">
          {meta.is_informational ? "Question" : "Extracted symptoms"}
        </p>
        <p className="mt-1 text-[13px] leading-6 text-ink dark:text-white/85">{meta.structured_symptoms}</p>
      </div>

      {meta.unsupported_claims.length > 0 && (
        <div className="rounded-lg border border-rose/25 bg-rose-soft p-3 dark:bg-rose/10">
          <p className="font-mono text-[10px] uppercase tracking-wider text-rose">Flagged claims</p>
          <ul className="mt-1 list-disc space-y-1 pl-4 text-[13px] leading-6 text-rose/90 dark:text-rose/85">
            {meta.unsupported_claims.map((claim, index) => (
              <li key={`${claim}-${index}`}>{claim}</li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <p className="font-mono text-[10px] uppercase tracking-wider text-accent">
          Sources ({meta.citations.length})
        </p>
        <div className="mt-2 space-y-2">
          {meta.citations.length === 0 ? (
            <p className="text-[13px] leading-6 text-ink-soft/60 dark:text-white/40">
              No supporting passages were retrieved.
            </p>
          ) : (
            meta.citations.map((citation, index) => (
              <CitationCard key={`${citation.source}-${index}`} citation={citation} index={index + 1} />
            ))
          )}
        </div>
      </div>

      <p className="font-mono text-[10px] uppercase tracking-wider text-ink-soft/45 dark:text-white/30">
        {meta.response_time_seconds}s response time
      </p>
    </div>
  );
}