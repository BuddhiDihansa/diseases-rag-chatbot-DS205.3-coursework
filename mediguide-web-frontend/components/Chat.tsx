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
import DoctorRobot from "./DoctorRobot";


import {
  CheckIcon,
  ChevronDownIcon,
  CopyIcon,
  MenuIcon,
  MoonIcon,
  SunIcon,
  TrashIcon,
} from "./icons";

type Theme = "light" | "dark";

type Message = ChatMessage;

type RobotState =
  | "idle"
  | "listening"
  | "thinking"
  | "happy"
  | "error";

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
  const [typedMessageId, setTypedMessageId] = useState<string | null>(null);

  /*
   * Robot state
   *
   * idle      = normal floating
   * listening = user is typing
   * thinking  = API/RAG is processing
   * happy     = answer successfully received
   * error     = API failed
   */
  const [robotState, setRobotState] =
    useState<RobotState>("idle");

  const scrollRef = useRef<HTMLDivElement>(null);

  /* =========================================
     SESSION CHANGE
  ========================================= */

  useEffect(() => {
    setTypedMessageId(null);
    setInput("");
    setRobotState("idle");
  }, [session.id]);

  /* =========================================
     AUTO SCROLL
  ========================================= */

  useEffect(() => {
    const container = scrollRef.current;

    if (!container) return;

    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth",
    });
  }, [messages.length, loading, session.id]);

  /* =========================================
     THINKING STEP ANIMATION
  ========================================= */

  useEffect(() => {
    if (!loading) return;

    setStepIndex(0);

    const interval = window.setInterval(() => {
      setStepIndex((index) =>
        Math.min(
          index + 1,
          STEP_LABELS.length - 1
        )
      );
    }, 1300);

    return () => window.clearInterval(interval);
  }, [loading]);

  /* =========================================
     INPUT LISTENING STATE
  ========================================= */

  function handleInputChange(value: string) {
    setInput(value);

    /*
     * If user is typing something,
     * robot becomes attentive/listening.
     */
    if (value.trim() && !loading) {
      setRobotState("listening");
    } else if (!loading) {
      setRobotState("idle");
    }
  }

  /* =========================================
     SEND MESSAGE
  ========================================= */

  async function send(text: string) {
    const trimmed = text.trim();

    if (!trimmed || loading) return;

    /* Robot starts thinking immediately */

    setRobotState("thinking");

    const userMessage: Message = {
      role: "user",
      content: trimmed,
      id: uid(),
    };

    onMessagesChange([
      ...messages,
      userMessage,
    ]);

    setInput("");
    setLoading(true);

    try {
      /*
       * Existing MediGuide API.
       * Nothing changed here.
       */
      const result = await askMediGuide(trimmed);

      const assistantId = uid();

      onMessagesChange([
        ...messages,
        userMessage,
        {
          role: "assistant",
          content: result.answer,
          id: assistantId,
          meta: result,
        },
      ]);

      setTypedMessageId(assistantId);

      /*
       * Successful answer.
       * Robot becomes happy.
       */
      setRobotState("happy");

      /*
       * Keep happy expression for a short moment,
       * then return to normal idle state.
       */
      window.setTimeout(() => {
        setRobotState("idle");
      }, 4200);
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Something went wrong.";

      onMessagesChange([
        ...messages,
        userMessage,
        {
          role: "assistant",
          content: "",
          id: uid(),
          error: message,
        },
      ]);

      /*
       * API failed.
       */
      setRobotState("error");

      window.setTimeout(() => {
        setRobotState("idle");
      }, 3000);
    } finally {
      setLoading(false);
    }
  }

  /* =========================================
     CLEAR CHAT
  ========================================= */

  function clearChat() {
    onMessagesChange([]);
    setTypedMessageId(null);
    setRobotState("idle");
  }

  return (
    <div className="relative flex min-h-screen flex-1 flex-col">

      {/* Background glow */}

      <div className="ambient-glow" />

      {/* Existing pulse divider */}

      <PulseDivider active={loading} />

      {/* =====================================
          MEDIRAG ROBOT
      ===================================== */}

      <DoctorRobot state={robotState} />

      {/* =====================================
          MAIN CONTENT
      ===================================== */}

      <div
        className="
          relative
          z-10
          mx-auto
          flex
          min-h-0
          w-full
          max-w-3xl
          flex-1
          flex-col
          gap-4
          px-4
          pb-6
          pt-5
          sm:px-6
        "
      >

        {/* Header */}

        <Header
          onOpenSidebar={onOpenSidebar}
          sessionTitle={session.title}
          theme={theme}
          onToggleTheme={onToggleTheme}
          onClearChat={clearChat}
        />

        <div className="flex min-h-0 flex-1 flex-col overflow-hidden">

          {/* ===================================
              MESSAGES
          =================================== */}

          <div
            ref={scrollRef}
            className="
              scrollbar-thin
              flex-1
              space-y-4
              overflow-y-auto
              px-1
              py-5
              sm:px-2
            "
          >

            {messages.length === 0 && (
              <EmptyState onPick={send} />
            )}

            {messages.map((message) =>
              message.role === "user" ? (
                <UserBubble
                  key={message.id}
                  content={message.content}
                />
              ) : (
                <AssistantBubble
                  key={message.id}
                  message={message}
                  animateTypewriter={
                    !message.error &&
                    message.id === typedMessageId &&
                    !loading
                  }
                />
              )
            )}

            {/* Thinking message */}

            {loading && (
              <ThinkingBubble
                label={STEP_LABELS[stepIndex]}
              />
            )}
          </div>

          {/* ===================================
              INPUT
          =================================== */}

          <Composer
            input={input}
            setInput={handleInputChange}
            onSend={() => send(input)}
            disabled={loading}
          />
        </div>
      </div>
    </div>
  );
}

/* ===========================================
   HEADER
=========================================== */

function Header({
  onOpenSidebar,
  sessionTitle,
  theme,
  onToggleTheme,
  onClearChat,
}: {
  onOpenSidebar: () => void;
  sessionTitle: string;
  theme: Theme;
  onToggleTheme: () => void;
  onClearChat: () => void;
}) {
  return (
    <header className="flex items-center justify-between gap-3">

      <div className="flex min-w-0 items-center gap-3">

        <button
          onClick={onOpenSidebar}
          aria-label="Open chat history"
          className="
            shrink-0
            rounded-lg
            border
            border-hairline
            p-2
            text-ink-soft
            transition
            hover:border-primary/40
            dark:border-navy-border
            dark:text-white/60
            lg:hidden
          "
        >
          <MenuIcon className="h-4 w-4" />
        </button>

        <div className="min-w-0">

          <p
            className="
              font-mono
              text-[11px]
              uppercase
              tracking-[0.3em]
              text-primary
            "
          >
            MediGuide LK
          </p>

          <h1
            className="
              truncate
              font-display
              text-lg
              font-bold
              text-ink
              dark:text-white
              sm:text-xl
            "
          >
            {sessionTitle}
          </h1>

        </div>
      </div>

      <div className="flex shrink-0 items-center gap-1.5">

        <button
          onClick={onClearChat}
          aria-label="Clear this chat"
          title="Clear this chat"
          className="
            grid
            h-9
            w-9
            place-items-center
            rounded-full
            border
            border-hairline
            text-ink-soft
            transition
            hover:border-rose/40
            hover:text-rose
            dark:border-navy-border
            dark:text-white/60
          "
        >
          <TrashIcon className="h-4 w-4" />
        </button>

        <button
          onClick={onToggleTheme}
          aria-label="Toggle dark mode"
          title="Toggle dark mode"
          className="
            grid
            h-9
            w-9
            place-items-center
            rounded-full
            border
            border-hairline
            text-ink-soft
            transition
            hover:border-primary/40
            dark:border-navy-border
            dark:text-white/60
          "
        >
          {theme === "dark" ? (
            <SunIcon className="h-4 w-4 text-accent-dark dark:text-accent" />
          ) : (
            <MoonIcon className="h-4 w-4 text-primary" />
          )}
        </button>

      </div>
    </header>
  );
}

/* ===========================================
   EMPTY STATE
=========================================== */

function EmptyState({
  onPick,
}: {
  onPick: (q: string) => void;
}) {
  return (
    <div
      className="
        flex
        min-h-[320px]
        animate-rise
        flex-col
        items-center
        justify-center
        gap-6
        rounded-xl
        border
        border-dashed
        border-hairline
        px-5
        py-10
        text-center
        dark:border-navy-border
      "
    >

      <div className="max-w-md space-y-2">

        <p
          className="
            font-display
            text-xl
            font-semibold
            text-ink
            dark:text-white
          "
        >
          Describe how you feel, or ask about a condition
        </p>

        <p
          className="
            text-sm
            leading-6
            text-ink-soft
            dark:text-white/50
          "
        >
          I answer only from verified guideline documents,
          and show you exactly which passages I used.
        </p>

      </div>

      <div className="flex w-full max-w-md flex-col gap-2">

        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onPick(suggestion)}
            className="
              rounded-xl
              border
              border-hairline
              bg-paper
              px-3.5
              py-3
              text-left
              text-[13px]
              leading-snug
              text-ink-soft
              transition
              hover:border-primary/40
              hover:text-ink
              dark:border-navy-border
              dark:bg-white/[0.02]
              dark:text-white/60
              dark:hover:border-primary/40
              dark:hover:text-white
            "
          >
            {suggestion}
          </button>
        ))}

      </div>
    </div>
  );
}

/* ===========================================
   USER MESSAGE
=========================================== */

function UserBubble({
  content,
}: {
  content: string;
}) {
  return (
    <div className="flex justify-end animate-rise">

      <div
        className="
          max-w-[80%]
          rounded-2xl
          rounded-tr-sm
          bg-primary
          px-4
          py-2.5
          text-[14px]
          leading-relaxed
          text-white
        "
      >
        {content}
      </div>

    </div>
  );
}

/* ===========================================
   ASSISTANT MESSAGE
=========================================== */

function AssistantBubble({
  message,
  animateTypewriter,
}: {
  message: Extract<
    Message,
    { role: "assistant" }
  >;

  animateTypewriter: boolean;
}) {
  const [
    visibleText,
    setVisibleText,
  ] = useState(
    animateTypewriter
      ? ""
      : message.content
  );

  const [copied, setCopied] =
    useState(false);

  const [sourcesOpen, setSourcesOpen] =
    useState(false);

  useEffect(() => {
    if (!animateTypewriter) {
      setVisibleText(message.content);
      return;
    }

    setVisibleText("");

    let index = 0;

    const timer =
      window.setInterval(() => {
        index += Math.max(
          1,
          Math.ceil(
            message.content.length / 50
          )
        );

        if (
          index >=
          message.content.length
        ) {
          setVisibleText(
            message.content
          );

          window.clearInterval(timer);

          return;
        }

        setVisibleText(
          message.content.slice(
            0,
            index
          )
        );
      }, TYPE_SPEED);

    return () =>
      window.clearInterval(timer);
  }, [
    animateTypewriter,
    message.content,
  ]);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(
        message.content
      );

      setCopied(true);

      window.setTimeout(
        () => setCopied(false),
        1600
      );
    } catch {
      // Clipboard permissions unavailable.
    }
  }

  if (message.error) {
    return (
      <div className="flex justify-start animate-rise">

        <div
          className="
            max-w-[85%]
            rounded-2xl
            rounded-tl-sm
            border
            border-rose/25
            bg-rose-soft
            px-4
            py-2.5
            text-[14px]
            leading-relaxed
            text-rose
            dark:bg-rose/10
          "
        >
          {message.error}
        </div>

      </div>
    );
  }

  const sourceCount =
    message.meta?.citations.length ?? 0;

  return (
    <div className="flex justify-start animate-rise">

      <div
        className="
          max-w-[85%]
          rounded-2xl
          rounded-tl-sm
          border
          border-hairline
          bg-paper
          px-4
          py-3
          dark:border-navy-border
          dark:bg-white/[0.02]
        "
      >

        <div className="prose-chat text-ink dark:text-white/85">

          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
          >
            {visibleText}
          </ReactMarkdown>

        </div>

        {message.meta && (
          <div className="mt-3 flex flex-wrap items-center gap-2">

            <VitalsBadge
              faithful={
                message.meta.faithful
              }
              needsReview={
                message.meta.needs_review
              }
            />

            <button
              onClick={handleCopy}
              className="
                inline-flex
                items-center
                gap-1.5
                rounded-full
                border
                border-hairline
                px-2.5
                py-1
                font-mono
                text-[11px]
                text-ink-soft
                transition
                hover:border-primary/40
                hover:text-ink
                dark:border-navy-border
                dark:text-white/55
                dark:hover:text-white
              "
            >
              {copied ? (
                <CheckIcon className="h-3 w-3 text-primary" />
              ) : (
                <CopyIcon className="h-3 w-3" />
              )}

              {copied
                ? "Copied"
                : "Copy"}
            </button>

            {sourceCount > 0 && (
              <button
                onClick={() =>
                  setSourcesOpen(
                    (open) => !open
                  )
                }
                className="
                  inline-flex
                  items-center
                  gap-1.5
                  rounded-full
                  border
                  border-hairline
                  px-2.5
                  py-1
                  font-mono
                  text-[11px]
                  text-accent-dark
                  transition
                  hover:border-accent/50
                  dark:border-navy-border
                  dark:text-accent
                "
              >
                {sourceCount} source
                {sourceCount > 1
                  ? "s"
                  : ""}

                <ChevronDownIcon
                  className={`
                    h-3
                    w-3
                    transition-transform
                    duration-200
                    ${
                      sourcesOpen
                        ? "rotate-180"
                        : ""
                    }
                  `}
                />
              </button>
            )}

          </div>
        )}

        {message.meta &&
          sourcesOpen && (
            <div
              className="
                mt-3
                space-y-3
                border-t
                border-hairline
                pt-3
                dark:border-navy-border
              "
            >

              {message.meta
                .unsupported_claims
                .length > 0 && (
                <div
                  className="
                    rounded-lg
                    border
                    border-rose/25
                    bg-rose-soft
                    p-3
                    dark:bg-rose/10
                  "
                >
                  <p
                    className="
                      font-mono
                      text-[10px]
                      uppercase
                      tracking-wider
                      text-rose
                    "
                  >
                    Flagged claims
                  </p>

                  <ul
                    className="
                      mt-1
                      list-disc
                      space-y-1
                      pl-4
                      text-[13px]
                      leading-6
                      text-rose/90
                      dark:text-rose/85
                    "
                  >
                    {message.meta
                      .unsupported_claims
                      .map(
                        (
                          claim,
                          index
                        ) => (
                          <li
                            key={`${claim}-${index}`}
                          >
                            {claim}
                          </li>
                        )
                      )}
                  </ul>
                </div>
              )}

              <div className="space-y-2">

                {message.meta.citations.map(
                  (
                    citation,
                    index
                  ) => (
                    <CitationCard
                      key={`${citation.source}-${index}`}
                      citation={citation}
                      index={
                        index + 1
                      }
                    />
                  )
                )}

              </div>

              <p
                className="
                  font-mono
                  text-[10px]
                  uppercase
                  tracking-wider
                  text-ink-soft/45
                  dark:text-white/30
                "
              >
                {
                  message.meta
                    .response_time_seconds
                }
                s response time
              </p>

            </div>
          )}

      </div>
    </div>
  );
}

/* ===========================================
   THINKING BUBBLE
=========================================== */

function ThinkingBubble({
  label,
}: {
  label: string;
}) {
  return (
    <div className="flex justify-start animate-rise">

      <div
        className="
          flex
          items-center
          gap-2
          rounded-2xl
          rounded-tl-sm
          border
          border-hairline
          bg-paper
          px-4
          py-2.5
          text-[13px]
          text-ink-soft
          dark:border-navy-border
          dark:bg-white/[0.02]
          dark:text-white/55
        "
      >

        <span className="flex gap-1">

          <span
            className="
              h-1.5
              w-1.5
              animate-blink
              rounded-full
              bg-primary
              [animation-delay:-0.2s]
            "
          />

          <span
            className="
              h-1.5
              w-1.5
              animate-blink
              rounded-full
              bg-primary
              [animation-delay:-0.1s]
            "
          />

          <span
            className="
              h-1.5
              w-1.5
              animate-blink
              rounded-full
              bg-primary
            "
          />

        </span>

        {label}

      </div>
    </div>
  );
}

/* ===========================================
   COMPOSER
=========================================== */

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
    <div
      className="
        border-t
        border-hairline
        p-4
        dark:border-navy-border
      "
    >

      <div
        className="
          rounded-xl
          border
          border-hairline
          bg-paper
          p-2.5
          focus-within:border-primary/50
          dark:border-navy-border
          dark:bg-white/[0.02]
        "
      >

        <div className="flex items-end gap-2.5">

          <textarea
            value={input}
            onChange={(event) =>
              setInput(
                event.target.value
              )
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey
              ) {
                event.preventDefault();
                onSend();
              }
            }}
            rows={1}
            placeholder="Describe symptoms, ask for a condition summary…"
            className="
              max-h-36
              flex-1
              resize-none
              bg-transparent
              px-2
              py-1.5
              text-[14px]
              leading-6
              text-ink
              placeholder:text-ink-soft/50
              focus:outline-none
              dark:text-white
              dark:placeholder:text-white/30
            "
          />

          <button
            onClick={onSend}
            disabled={
              disabled ||
              !input.trim()
            }
            className="
              shrink-0
              rounded-lg
              bg-primary
              px-4
              py-2
              text-[13px]
              font-semibold
              text-white
              transition
              hover:bg-primary-dark
              active:scale-95
              disabled:cursor-not-allowed
              disabled:opacity-40
            "
          >
            Send
          </button>

        </div>
      </div>

      <p
        className="
          mt-2
          px-1
          text-[11px]
          text-ink-soft/60
          dark:text-white/35
        "
      >
        Enter to send, Shift+Enter for a newline.
        Informational only — not a substitute for
        professional medical advice.
      </p>

    </div>
  );
}