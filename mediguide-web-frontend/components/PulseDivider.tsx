"use client";

type PulseDividerProps = {
  active?: boolean;
  className?: string;
};

/**
 * The page's signature element: a clinical vitals-monitor trace line.
 * Idle: a calm, static waveform hairline that reads as a EKG strip
 * motif tying back to "reading vital signs from a document" - the
 * whole premise of the app.
 * Active (a request is in flight): the line animates left-to-right,
 * doubling as the loading indicator instead of a generic spinner.
 */
export default function PulseDivider({
  active = false,
  className = "",
}: PulseDividerProps) {
  return (
    <div className={`w-full overflow-hidden ${className}`} aria-hidden="true">
      <svg
        viewBox="0 0 480 32"
        preserveAspectRatio="none"
        className="h-6 w-full text-teal/70"
      >
        <path
          d="M0 16 H150 L162 4 L174 28 L186 16 H210 L222 8 L234 24 L246 16 H480"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray="240"
          className={active ? "animate-pulseline" : ""}
          style={!active ? { opacity: 0.35 } : undefined}
        />
      </svg>
    </div>
  );
}
