"use client";

/**
 * A small, cute doctor-robot mascot that gently roams the page edges.
 * Purely decorative (pointer-events-none) so it never blocks clicks.
 * - Outer element: animates position (roam) across a safe zone that
 *   stays clear of the sidebar and the chat's readable center column.
 * - Inner element: continuous idle bob + tilt.
 * - Right arm: waves on a loop. Antenna tip: soft blinking sensor light.
 */
export default function DoctorRobot() {
  return (
    <div
      className="pointer-events-none fixed z-[60] h-20 w-20 -translate-x-1/2 -translate-y-1/2 animate-roam sm:h-24 sm:w-24"
      aria-hidden="true"
    >
      <div className="animate-bob">
        <svg viewBox="0 0 100 132" className="h-full w-full drop-shadow-[0_12px_18px_rgba(15,23,42,0.22)]">
          {/* antenna */}
          <line x1="50" y1="20" x2="50" y2="7" stroke="#16A34A" strokeWidth="3" strokeLinecap="round" />
          <circle cx="50" cy="6" r="5" fill="#EAB308" className="animate-blink" />

          {/* side ear domes */}
          <circle cx="14" cy="42" r="7" fill="#16A34A" />
          <circle cx="86" cy="42" r="7" fill="#16A34A" />

          {/* head shell */}
          <rect x="18" y="18" width="64" height="48" rx="20" fill="#FFFFFF" stroke="#16A34A" strokeWidth="3" />

          {/* screen-face visor */}
          <rect x="27" y="27" width="46" height="30" rx="13" fill="#0F172A" />
          <path d="M36 43 Q40 36 44 43" stroke="#FFFFFF" strokeWidth="3" fill="none" strokeLinecap="round" />
          <path d="M56 43 Q60 36 64 43" stroke="#FFFFFF" strokeWidth="3" fill="none" strokeLinecap="round" />
          <path d="M43 49 Q50 54 57 49" stroke="#EAB308" strokeWidth="2.5" fill="none" strokeLinecap="round" />

          {/* body */}
          <rect x="15" y="70" width="70" height="48" rx="22" fill="#FFFFFF" stroke="#16A34A" strokeWidth="3" />

          {/* stethoscope drape */}
          <path d="M30 71 Q23 82 32 90" stroke="#5B6478" strokeWidth="2.5" fill="none" strokeLinecap="round" />
          <circle cx="32" cy="90" r="3.2" fill="#5B6478" />

          {/* cross badge */}
          <rect x="50" y="84" width="8" height="20" rx="2" fill="#16A34A" />
          <rect x="42" y="92" width="24" height="8" rx="2" fill="#16A34A" />

          {/* left (static) arm */}
          <rect x="2" y="80" width="13" height="24" rx="6.5" fill="#FFFFFF" stroke="#16A34A" strokeWidth="3" />

          {/* right (waving) arm */}
          <rect
            x="85" y="74" width="13" height="24" rx="6.5"
            fill="#FFFFFF" stroke="#EAB308" strokeWidth="3"
            style={{ transformOrigin: "86px 82px" }}
            className="animate-wave"
          />

          {/* ground shadow */}
          <ellipse cx="50" cy="126" rx="26" ry="5" fill="rgba(15,23,42,0.08)" />
        </svg>
      </div>
    </div>
  );
}