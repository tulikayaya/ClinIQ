import { useState } from "react";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";
import { sendMessage } from "../api/client";

export default function ChatWindow() {
  const [messages, setMessages]           = useState([
    {
      role: "assistant",
      content: "Hello! I'm ClinIQ. Describe your patient — demographics, diagnosis, molecular markers, treatment — and I'll find the most similar historical cases. You can also attach a NIfTI image and mask for imaging-based retrieval.",
    },
  ]);
  const [radiomic_vector, setRadiomicVec] = useState(null);
  const [loading, setLoading]             = useState(false);

  async function handleSend(text, vector) {
    const userMsg = { role: "user", content: text };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setLoading(true);

    const activeVector = vector ?? radiomic_vector;
    if (vector) setRadiomicVec(vector);

    try {
      const data = await sendMessage(nextMessages, activeVector);
      setMessages((prev) => [...prev, { role: "assistant", content: data.reply, cases: data.cases ?? [] }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-window">
      <div className="message-list">
        {messages.map((msg, i) => (
          <MessageBubble key={i} role={msg.role} content={msg.content} cases={msg.cases ?? []} />
        ))}
        {loading && (
          <div className="bubble assistant loading">
            <span className="dots">···</span>
          </div>
        )}
      </div>
      <ChatInput onSend={handleSend} disabled={loading} />
    </div>
  );
}
