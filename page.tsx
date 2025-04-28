import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  docUrl?: string; // Optional URL for the generated document
}

export default function HomePage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  };

  const handleSendMessage = async () => {
    const text = inputValue.trim();
    if (!text) return;

    const newUserMessage: Message = {
      id: Date.now(),
      text: text,
      sender: 'user',
    };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);
    setInputValue('');
    setIsLoading(true);

    // --- Backend API Call Placeholder ---
    // In a real application, you would call your backend API here
    // The backend would handle the DDQ workflow, OpenAI call, doc generation, etc.
    // For now, we simulate a response.
    try {
      // Replace with actual API call
      // const response = await fetch('/api/chat', { 
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ prompt: text, history: messages })
      // });
      // const data = await response.json();

      // Simulate API response delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Simulated AI response
      const aiResponseText = `This is a simulated response to: "${text}". The full answer document is being generated.`;
      const simulatedDocUrl = `https://example.blob.core.windows.net/documents/generated_doc_${Date.now()}.docx`; // Placeholder URL

      const newAiMessage: Message = {
        id: Date.now() + 1,
        text: aiResponseText,
        sender: 'ai',
        docUrl: simulatedDocUrl, // Include the document URL
      };
      setMessages((prevMessages) => [...prevMessages, newAiMessage]);

    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        id: Date.now() + 1,
        text: "Sorry, I encountered an error. Please try again.",
        sender: 'ai',
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
    // --- End Placeholder ---
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && !isLoading) {
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header (Optional) */}
      <header className="bg-white shadow-md p-4 text-center">
        <h1 className="text-xl font-semibold text-gray-800">DDQ Assistant</h1>
      </header>

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-lg p-3 rounded-lg shadow ${message.sender === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-800'}`}
            >
              <p>{message.text}</p>
              {message.sender === 'ai' && message.docUrl && (
                <a 
                  href={message.docUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-blue-700 hover:underline mt-2 block"
                >
                  View Full Document
                </a>
              )}
            </div>
          </div>
        ))}
        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white p-4 border-t border-gray-200 flex items-center">
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder={isLoading ? "Processing..." : "Type your message..."}
          className="flex-1 border border-gray-300 rounded-lg p-2 mr-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        />
        <button
          onClick={handleSendMessage}
          className={`bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed`}
          disabled={isLoading}
        >
          {isLoading ? (
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            'Send'
          )}
        </button>
      </div>
    </div>
  );
}

