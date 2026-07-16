import Chat from "@/components/Chat";

export default function Home() {
  return (
    <main className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-64 bg-gradient-to-b from-teal/10 via-transparent to-transparent dark:from-teal/20" />
      <Chat />
    </main>
  );
}
