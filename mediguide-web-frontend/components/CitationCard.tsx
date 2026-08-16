import type { Citation } from "@/lib/api";

export default function CitationCard({
  citation,
  index,
}: {
  citation: Citation;
  index: number;
}) {
  return (
    <div className="animate-rise rounded-lg border border-hairline bg-paper/60 p-3 dark:border-navy-border dark:bg-white/5">
      <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-ink-soft dark:text-white/50">
        <span className="flex h-4 w-4 items-center justify-center rounded-sm bg-primary-soft text-primary-dark dark:bg-primary/15 dark:text-primary">
          {index}
        </span>
        <span className="truncate">{citation.source}</span>
      </div>
      <p className="mt-2 text-[13px] leading-relaxed text-ink-soft dark:text-white/65">
        {citation.snippet}
      </p>
    </div>
  );
}