import type { Citation } from "@/lib/api";

export default function CitationCard({
  citation,
  index,
}: {
  citation: Citation;
  index: number;
}) {
  return (
    <div className="rounded-lg border border-hairline bg-paper/60 p-3 animate-rise">
      <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-ink-soft">
        <span className="flex h-4 w-4 items-center justify-center rounded-sm bg-teal-soft text-teal">
          {index}
        </span>
        <span className="truncate">{citation.source}</span>
      </div>
      <p className="mt-2 text-[13px] leading-relaxed text-ink-soft">
        {citation.snippet}
      </p>
    </div>
  );
}
