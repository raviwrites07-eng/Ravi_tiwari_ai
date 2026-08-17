import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    if (!question.trim() || loading) {
      return;
    }

    const currentQuestion = question.trim();

    // Show user's question
    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: currentQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      // Send question to FastAPI backend
      const response = await fetch(
        `http://127.0.0.1:8000/ask?question=${encodeURIComponent(
          currentQuestion
        )}`
      );

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();

      // Show AI answer
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
        },
      ]);
    } catch (error) {
      console.error("frontend error:", error);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
             `Error: ${error.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  return (
    <div className="app">

      {/* Header */}
      <header className="header">
        <div className="brand">
          <div className="brand-icon">✦</div>

          <div>
            <h1>Ravi Tiwari AI</h1>
            <p>AI Resume Assistant</p>
          </div>
        </div>

        <div className="online-status">
          <span className="status-dot"></span>
          Online
        </div>
      </header>

      {/* Chat area */}
      <main className="chat-container">

        {messages.length === 0 ? (

          <section className="welcome">

            <div className="welcome-icon">
              ✦
            </div>

            <h2>Ask about my resume</h2>

            <p>
              Ask anything about my skills, experience,
              education, or projects.
            </p>

            <div className="suggestions">

              <button
                onClick={() =>
                  setQuestion("Do you have experience with Python?")
                }
              >
                Do you have Python experience?
              </button>

              <button
                onClick={() =>
                  setQuestion("What AI projects have you built?")
                }
              >
                What AI projects have you built?
              </button>

              <button
                onClick={() =>
                  setQuestion("What technologies do you know?")
                }
              >
                What technologies do you know?
              </button>

            </div>

          </section>

        ) : (

          <section className="messages">

            {messages.map((message, index) => (

              <div
                key={index}
                className={`message-row ${
                  message.role === "user"
                    ? "user-row"
                    : "assistant-row"
                }`}
              >

                {message.role === "assistant" && (
                  <div className="avatar ai-avatar">
                    ✦
                  </div>
                )}

                <div
                  className={`message ${
                    message.role === "user"
                      ? "user-message"
                      : "assistant-message"
                  }`}
                >
                  {message.content}
                </div>

                {message.role === "user" && (
                  <div className="avatar user-avatar">
                    R
                  </div>
                )}

              </div>

            ))}

            {/* Loading animation */}
            {loading && (
              <div className="message-row assistant-row">

                <div className="avatar ai-avatar">
                  ✦
                </div>

                <div className="message assistant-message loading-message">

                  <span></span>
                  <span></span>
                  <span></span>

                </div>

              </div>
            )}

          </section>

        )}

      </main>

      {/* Input area */}
      <div className="input-wrapper">

        <div className="input-box">

          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about my resume..."
            rows="1"
          />

          <button
            className="send-button"
            onClick={askQuestion}
            disabled={loading || !question.trim()}
          >
            ➤
          </button>

        </div>

        <p className="footer-text">
          Answers are grounded in the information available in my resume.
        </p>

      </div>

    </div>
  );
}

export default App;