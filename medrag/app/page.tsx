import ChatInterface from "@/components/ChatInterface";
import Header from "@/components/Header";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F172A]">
      <Header />
      <ChatInterface />
    </div>
  );
}
