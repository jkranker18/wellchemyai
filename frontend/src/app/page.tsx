'use client';

import React, { useState } from 'react';
import { api } from '@/services/api';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
}

// Placeholder components for the chat UI
const Header = () => (
  <header className="bg-green-800 text-white p-4 text-center">
    <h1 className="text-2xl font-bold">Wellchemy</h1>
  </header>
);

const LeftRail = () => (
  <div className="bg-green-100 p-4 h-full">
    <h2 className="text-lg font-semibold mb-2">Chat History</h2>
    <ul className="space-y-2">
      <li className="p-2 bg-green-200 rounded">Chat 1</li>
      <li className="p-2 bg-green-200 rounded">Chat 2</li>
      <li className="p-2 bg-green-200 rounded">Chat 3</li>
    </ul>
  </div>
);

const ChatArea = ({ messages, onSendMessage }: { messages: Message[], onSendMessage: (text: string) => void }) => {
  const [inputText, setInputText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      onSendMessage(inputText);
      setInputText('');
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 p-4 overflow-y-auto bg-green-50">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`mb-4 p-3 rounded-lg ${
              message.isUser ? 'bg-green-300 ml-auto' : 'bg-green-200'
            } max-w-[80%]`}
          >
            {message.text}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="p-4 border-t border-green-300">
        <div className="flex">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-2 border border-green-300 rounded-l"
          />
          <button type="submit" className="bg-green-800 text-white p-2 rounded-r">
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

const Footer = () => (
  <footer className="bg-green-800 text-white p-4 text-center">
    <p>© 2024 Wellchemy. All rights reserved.</p>
  </footer>
);

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your Wellchemy AI assistant. How can I help you today?",
      isUser: false,
    },
  ]);

  const handleSendMessage = async (text: string) => {
    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text,
      isUser: true,
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      // Send message to backend
      const response = await api.chat(text);
      
      // Add AI response
      if (response.success) {
        const aiMessage: Message = {
          id: messages.length + 2,
          text: response.data.response,
          isUser: false,
        };
        setMessages((prev) => [...prev, aiMessage]);
      } else {
        // Handle error
        const errorMessage: Message = {
          id: messages.length + 2,
          text: "Sorry, I encountered an error. Please try again.",
          isUser: false,
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: messages.length + 2,
        text: "Sorry, I encountered an error. Please try again.",
        isUser: false,
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="flex flex-1">
        <div className="w-1/4">
          <LeftRail />
        </div>
        <div className="w-3/4">
          <ChatArea messages={messages} onSendMessage={handleSendMessage} />
        </div>
      </div>
      <Footer />
    </div>
  );
}
