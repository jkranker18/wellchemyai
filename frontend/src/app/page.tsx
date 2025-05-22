'use client';

import React, { useState, useRef, useEffect } from 'react';
import { api } from '@/services/api';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
}

const Header = () => (
  <header className="bg-gradient-to-r from-green-700 to-green-800 text-white p-4 shadow-md">
    <div className="container mx-auto">
      <h1 className="text-2xl font-bold">Wellchemy</h1>
      <p className="text-sm text-green-100">Your AI Wellness Assistant</p>
    </div>
  </header>
);

const LeftRail = () => (
  <div className="bg-white p-4 h-full border-r border-gray-200">
    <h2 className="text-lg font-semibold mb-4 text-gray-700">Chat History</h2>
    <ul className="space-y-2">
      <li className="p-3 bg-green-50 rounded-lg hover:bg-green-100 cursor-pointer transition-colors">
        <span className="text-sm text-gray-600">Today's Chat</span>
      </li>
      <li className="p-3 bg-green-50 rounded-lg hover:bg-green-100 cursor-pointer transition-colors">
        <span className="text-sm text-gray-600">Dietary Assessment</span>
      </li>
      <li className="p-3 bg-green-50 rounded-lg hover:bg-green-100 cursor-pointer transition-colors">
        <span className="text-sm text-gray-600">Wellness Plan</span>
      </li>
    </ul>
  </div>
);

const ChatArea = ({ messages, onSendMessage }: { messages: Message[], onSendMessage: (text: string) => void }) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      onSendMessage(inputText);
      setInputText('');
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      <div className="flex-1 p-4 overflow-y-auto">
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                  message.isUser 
                    ? 'bg-green-600 text-white rounded-br-none' 
                    : 'bg-white text-gray-800 rounded-bl-none shadow-sm'
                }`}
              >
                <p className="text-sm sm:text-base">{message.text}</p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>
      <form onSubmit={handleSubmit} className="border-t border-gray-200 bg-white p-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 p-3 border border-gray-300 rounded-full focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500"
            />
            <button
              type="submit"
              className="bg-green-600 text-white px-6 py-3 rounded-full hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            >
              Send
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

const Footer = () => (
  <footer className="bg-gradient-to-r from-green-700 to-green-800 text-white p-4 text-center text-sm">
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
    <div className="flex flex-col h-screen bg-gray-50">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <div className="w-1/4 hidden md:block">
          <LeftRail />
        </div>
        <div className="w-full md:w-3/4">
          <ChatArea messages={messages} onSendMessage={handleSendMessage} />
        </div>
      </div>
      <Footer />
    </div>
  );
}
