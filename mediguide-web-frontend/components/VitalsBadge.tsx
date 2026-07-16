type VitalsBadgeProps = {
  faithful: string;
  needsReview: boolean;
};

const READOUT: Record<
  string,
  { label: string; tone: "verified" | "amber"; note: string }
> = {
  Yes: {
    label: "VERIFIED",
    tone: "verified",
    note: "Every claim traces back to the retrieved guideline text.",
  },
  Partially: {
    label: "PARTIAL MATCH",
    tone: "amber",
    note: "Some of this answer isn't directly grounded in the retrieved text.",
  },
  No: {
    label: "UNVERIFIED",
    tone: "amber",
    note: "This answer could not be verified against the retrieved text.",
  },
};

export default function VitalsBadge({ faithful, needsReview }: VitalsBadgeProps) {
  const readout = READOUT[faithful] ?? {
    label: faithful.toUpperCase(),
    tone: needsReview ? "amber" : "verified",
    note: "",
  };

  const isVerified = readout.tone === "verified";

  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 font-mono text-[11px] tracking-wide ${
        isVerified
          ? "border-verified/30 bg-verified-soft text-verified"
          : "border-amber/30 bg-amber-soft text-amber"
      }`}
      title={readout.note}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          isVerified ? "bg-verified" : "bg-amber animate-blink"
        }`}
      />
      FAITHFULNESS · {readout.label}
    </div>
  );
}
