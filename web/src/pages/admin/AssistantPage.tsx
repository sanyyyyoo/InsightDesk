import { useEffect, useRef, useState, type FormEvent } from "react";
import { friendlyMessage } from "../../api/client";
import { useChat } from "../../api/hooks";
import { Card, PageHeader } from "../../components/ui";

interface Message {
  role: "user" | "bot";
  text: string;
  error?: boolean;
}

const SUGGESTIONS = ["Which cases are spiking right now?", "Summarise case 101 and its root cause", "List all topics and their departments"];
const STORAGE_KEY = "insightdesk.chat";

function loadHistory(): Message[] {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Message[]) : [];
  } catch {
    return [];
  }
}

export function AssistantPage() {
  const chat = useChat();
  const [messages, setMessages] = useState<Message[]>(loadHistory);
  const [input, setInput] = useState("");
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-50)));
    } catch {
      /* storage unavailable: history just isn't kept */
    }
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function send(text: string) {
    const msg = text.trim();
    if (!msg || chat.isPending) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: msg }]);
    try {
      const res = await chat.mutateAsync(msg);
      setMessages((m) => [...m, { role: "bot", text: res.answer || "(empty answer)" }]);
    } catch (err) {
      setMessages((m) => [...m, { role: "bot", text: friendlyMessage(err), error: true }]);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void send(input);
  }

  return (
    <div className="stack">
      <PageHeader title="AI Assistant" subtitle="Ask about cases, topics and root causes. Answers come from InsightDesk data via the assistant's tools." />
      <Card
        actions={
          messages.length > 0 && (
            <button className="btn btn-secondary" type="button" onClick={() => setMessages([])} disabled={chat.isPending}>
              Clear chat
            </button>
          )
        }
      >
        <div className="chat">
          <div className="chat-log" ref={logRef} aria-live="polite">
            {messages.length === 0 && (
              <div className="state stack">
                <span>Try one of these:</span>
                <div className="row" style={{ justifyContent: "center" }}>
                  {SUGGESTIONS.map((s) => (
                    <button key={s} className="btn btn-secondary" type="button" onClick={() => send(s)}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`bubble ${m.role}`} style={m.error ? { borderColor: "var(--danger-soft)", color: "var(--danger)" } : undefined}>
                {m.text}
              </div>
            ))}
            {chat.isPending && (
              <div className="bubble bot row">
                <span className="spinner" aria-hidden /> Thinking…
              </div>
            )}
          </div>
          <form className="chat-input" onSubmit={onSubmit}>
            <input
              className="input"
              placeholder="Ask a question…"
              aria-label="Message"
              value={input}
              maxLength={2000}
              onChange={(e) => setInput(e.target.value)}
              disabled={chat.isPending}
            />
            <button className="btn" type="submit" disabled={chat.isPending || !input.trim()}>
              Send
            </button>
          </form>
        </div>
      </Card>
    </div>
  );
}
