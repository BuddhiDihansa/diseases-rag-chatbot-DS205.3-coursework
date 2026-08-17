"use client";

export default function DoctorRobot() {
  return (
    <div
      className="
        pointer-events-none
        fixed
        bottom-20
        right-3
        z-[60]
        sm:bottom-6
        sm:right-6
      "
      aria-hidden="true"
    >
      <div className="relative h-[125px] w-[105px] sm:h-[155px] sm:w-[130px] animate-robot-idle">

        {/* Ground glow */}
        <div
          className="
            absolute
            bottom-0
            left-1/2
            h-5
            w-16
            -translate-x-1/2
            rounded-full
            bg-primary/20
            blur-md
          "
        />

        <svg
          viewBox="0 0 180 220"
          className="
            relative
            h-full
            w-full
            overflow-visible
            drop-shadow-[0_14px_22px_rgba(15,23,42,0.20)]
          "
        >

          {/* ========================= */}
          {/* ANTENNA */}
          {/* ========================= */}

          <path
            d="M90 35 C90 25 90 19 90 12"
            stroke="#16A34A"
            strokeWidth="5"
            strokeLinecap="round"
            fill="none"
          />

          <circle
            cx="90"
            cy="10"
            r="7"
            fill="#EAB308"
            className="animate-robot-blink"
          />

          {/* ========================= */}
          {/* EARS */}
          {/* ========================= */}

          <circle
            cx="27"
            cy="80"
            r="14"
            fill="#16A34A"
          />

          <circle
            cx="153"
            cy="80"
            r="14"
            fill="#16A34A"
          />

          {/* ========================= */}
          {/* HEAD */}
          {/* ========================= */}

          <rect
            x="28"
            y="34"
            width="124"
            height="92"
            rx="34"
            fill="white"
            stroke="#16A34A"
            strokeWidth="5"
          />

          {/* Face screen */}

          <rect
            x="45"
            y="51"
            width="90"
            height="58"
            rx="23"
            fill="#0F172A"
          />

          {/* ========================= */}
          {/* EYES */}
          {/* ========================= */}

          <circle
            cx="68"
            cy="76"
            r="6"
            fill="white"
            className="animate-robot-eye"
          />

          <circle
            cx="112"
            cy="76"
            r="6"
            fill="white"
            className="animate-robot-eye"
          />

          {/* ========================= */}
          {/* SMILE */}
          {/* ========================= */}

          <path
            d="M75 92 Q90 104 105 92"
            stroke="#EAB308"
            strokeWidth="5"
            fill="none"
            strokeLinecap="round"
          />

          {/* ========================= */}
          {/* CHEEKS */}
          {/* ========================= */}

          <circle
            cx="55"
            cy="94"
            r="4"
            fill="#F472B6"
            opacity="0.6"
          />

          <circle
            cx="125"
            cy="94"
            r="4"
            fill="#F472B6"
            opacity="0.6"
          />

          {/* ========================= */}
          {/* NECK */}
          {/* ========================= */}

          <rect
            x="76"
            y="123"
            width="28"
            height="12"
            rx="6"
            fill="#16A34A"
          />

          {/* ========================= */}
          {/* BODY */}
          {/* ========================= */}

          <rect
            x="39"
            y="132"
            width="102"
            height="67"
            rx="30"
            fill="white"
            stroke="#16A34A"
            strokeWidth="5"
          />

          {/* Chest */}

          <rect
            x="63"
            y="147"
            width="54"
            height="35"
            rx="12"
            fill="#EFF6FF"
          />

          {/* Medical cross */}

          <rect
            x="86"
            y="153"
            width="8"
            height="23"
            rx="2"
            fill="#16A34A"
          />

          <rect
            x="78"
            y="161"
            width="24"
            height="8"
            rx="2"
            fill="#16A34A"
          />

          {/* ========================= */}
          {/* LEFT ARM */}
          {/* ========================= */}

          <rect
            x="22"
            y="139"
            width="21"
            height="47"
            rx="10"
            fill="white"
            stroke="#16A34A"
            strokeWidth="5"
          />

          {/* ========================= */}
          {/* RIGHT ARM */}
          {/* ========================= */}

          <g className="animate-robot-wave">
            <rect
              x="137"
              y="139"
              width="21"
              height="47"
              rx="10"
              fill="white"
              stroke="#16A34A"
              strokeWidth="5"
            />

            <circle
              cx="147"
              cy="190"
              r="11"
              fill="white"
              stroke="#16A34A"
              strokeWidth="4"
            />
          </g>

          {/* Small chest light */}

          <circle
            cx="128"
            cy="149"
            r="4"
            fill="#EAB308"
            className="animate-robot-blink"
          />
        </svg>
      </div>
    </div>
  );
}