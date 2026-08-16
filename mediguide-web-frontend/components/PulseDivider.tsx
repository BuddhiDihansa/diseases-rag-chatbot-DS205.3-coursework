"use client";

/**
 * The app's signature motion element: a sticky, full-width vitals-monitor
 * trace bar pinned to the very top of the content area. It is always
 * mounted and always animating (slow trace at idle), so the page feels
 * "alive" continuously - not just during a request. While a request is
 * in flight it switches to a faster, brighter trace, doubling as the
 * loading indicator instead of a generic spinner.
 */
export default function PulseDivider({ active = false }: { active?: boolean }) {
  return (
    <div className="signal-bar">
      <svg
        viewBox="0 0 960 34"
        preserveAspectRatio="none"
        className={`h-full w-full ${active ? "text-primary" : "text-primary/50"}`}
      >
        <path
          d="M0 17 H360 L378 4 L396 30 L414 17 H460 L478 8 L496 26 L514 17 H960"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray="240"
          className={active ? "animate-pulseline" : "animate-pulseline-idle"}
        />
      </svg>
    </div>
  );
}