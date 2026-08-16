type VitalsBadgeProps = {
  faithful: string;
  needsReview: boolean;
};

type Tone = "primary" | "amber" | "rose";

const READOUT: Record<string, { label: string; tone: Tone; note: string }> = {
  Yes: {
    label: "VERIFIED",
    tone: "primary",
    note: "Every claim traces back to the retrieved guideline text.",
  },
  Partially: {
    label: "PARTIAL MATCH",
    tone: "amber",
    note: "Some of this answer isn't directly grounded in the retrieved text.",
  },
  No: {
    label: "UNVERIFIED",
    tone: "rose",
    note: "This answer could not be verified against the retrieved text.",
  },
};

const TONE_STYLES: Record<Tone, string> = {
  primary:
    "border-primary/25 bg-primary-soft text-primary-dark dark:border-primary/30 dark:bg-primary/15 dark:text-primary",
  amber:
    "border-amber/25 bg-amber-soft text-amber dark:border-amber/30 dark:bg-amber/15 dark:text-amber",
  rose: "border-rose/25 bg-rose-soft text-rose dark:border-rose/30 dark:bg-rose/15 dark:text-rose",
};

const DOT_STYLES: Record<Tone, string> = {
  primary: "bg-primary",
  amber: "bg-amber animate-blink",
  rose: "bg-rose animate-blink",
};

export default function VitalsBadge({ faithful, needsReview }: VitalsBadgeProps) {
  const readout = READOUT[faithful] ?? {
    label: faithful.toUpperCase(),
    tone: (needsReview ? "amber" : "primary") as Tone,
    note: "",
  };

  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 font-mono text-[11px] tracking-wide ${TONE_STYLES[readout.tone]}`}
      title={readout.note}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${DOT_STYLES[readout.tone]}`} />
      FAITHFULNESS · {readout.label}
    </div>
  );
}