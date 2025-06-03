"use client";

import React, { useState, useRef, useEffect } from "react";
import { api } from "../services/api";
import { Message } from "../types/Message";
import { Send, MessageSquare, History, Leaf, ChevronRight, Sparkles } from "lucide-react";
import Image from "next/image";
import ReactMarkdown from "react-markdown";
import { ScrollArea } from "@/components/ui/scroll-area";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");

  useEffect(() => {
    const fetchInitialMessage = async () => {
      try {
        let userId = localStorage.getItem("user_id") || "default";
        const response = await api.chat("start", userId);

        if (response.success) {
          const aiMessage: Message = {
            id: 1,
            text: response.data.response,
            isUser: false,
          };
          setMessages([aiMessage]);

          if (response.data.user_id) {
            localStorage.setItem("user_id", response.data.user_id);
          }
        }
      } catch (error) {
        console.error("Error fetching initial message:", error);
      }
    };

    fetchInitialMessage();
  }, []);

  const handleSendMessage = async (text: string) => {
    const userMessage: Message = {
      id: messages.length + 1,
      text,
      isUser: true,
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      let userId = localStorage.getItem("user_id") || "default";
      const response = await api.chat(text, userId);

      if (response.success) {
        const aiMessage: Message = {
          id: messages.length + 2,
          text: response.data.response,
          isUser: false,
        };
        setMessages((prev) => [...prev, aiMessage]);

        if (response.data.user_id) {
          localStorage.setItem("user_id", response.data.user_id);
        }
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: messages.length + 2,
          text: "Sorry, I encountered an error. Please try again.",
          isUser: false,
        },
      ]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      handleSendMessage(inputText);
      setInputText("");
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#f0f9f0]">
      <Header />
      <div className="flex flex-1 pt-[72px] pb-[60px] relative">
        <div className="w-1/4 min-w-[250px] hidden xl:block fixed top-[72px] bottom-[60px] left-0">
          <LeftRail />
        </div>
        <div className="w-full xl:w-3/4 xl:ml-[25%]">
          <ChatArea
            messages={messages}
            onSendMessage={handleSendMessage}
            inputText={inputText}
            setInputText={setInputText}
            handleSubmit={handleSubmit}
          />
        </div>
      </div>
      <Footer />
    </div>
  );
}

const Header = () => (
  <header className="bg-gradient-to-r from-[#2A6657] to-[#1d4a3e] text-white p-4 shadow-lg fixed top-0 left-0 right-0 z-50">
    <div className="container mx-auto flex items-center justify-center">
      <div className="flex items-center justify-center gap-3">
        <Image src="/Wellchemy white apple.png" alt="Wellchemy Logo" width={40} height={40} className="object-contain" />
        <div className="text-center">
          <h1 className="text-2xl font-display font-semibold tracking-tight">Wellchemy</h1>
          <p className="text-sm text-[#f7eee3] font-sans">Your AI Wellness Assistant</p>
        </div>
      </div>
    </div>
  </header>
);

const LeftRail = () => (
  <div className="bg-gradient-to-b from-[#f0f9f0] to-white rounded-r-2xl shadow-md h-full border-r border-[#e6d2b3]/30">
    <nav className="p-6">
      <ul className="space-y-4">
        <li>
          <a href="#" className="flex items-center gap-3 p-3 rounded-xl hover:bg-[#2A6657]/10 transition-colors duration-200 text-[#17322a] bg-white/80 backdrop-blur-md border border-[#e6d2b3]/40 shadow-md">
            <MessageSquare className="w-5 h-5" />
            <span className="font-medium">Chat</span>
            <ChevronRight className="w-4 h-4 ml-auto opacity-50" />
          </a>
        </li>
        <li>
          <a href="#" className="flex items-center gap-3 p-3 rounded-xl hover:bg-[#2A6657]/10 transition-colors duration-200 text-[#17322a] bg-white/80 backdrop-blur-md border border-[#e6d2b3]/40 shadow-md">
            <Leaf className="w-5 h-5" />
            <span className="font-medium">Assessments</span>
            <ChevronRight className="w-4 h-4 ml-auto opacity-50" />
          </a>
        </li>
        <li>
          <a href="#" className="flex items-center gap-3 p-3 rounded-xl hover:bg-[#2A6657]/10 transition-colors duration-200 text-[#17322a] bg-white/80 backdrop-blur-md border border-[#e6d2b3]/40 shadow-md">
            <History className="w-5 h-5" />
            <span className="font-medium">History</span>
            <ChevronRight className="w-4 h-4 ml-auto opacity-50" />
          </a>
        </li>
      </ul>
    </nav>
  </div>
);

const ChatArea = ({ messages, onSendMessage, inputText, setInputText, handleSubmit }: any) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-[#f0f9f0] via-white to-[#f0f9f0] relative">
      <div className="flex-1 min-h-0 pb-[80px]">
        <ScrollArea className="h-full">
          <div className="p-6">
            <div className="max-w-xl mx-auto space-y-4 sm:space-y-6">
              {messages.map((message: Message) => (
                <div key={message.id} className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[85%] sm:max-w-[80%] rounded-2xl px-4 sm:px-6 py-3 sm:py-4 ${message.isUser ? "bg-gradient-to-r from-[#2A6657] to-[#1d4a3e] text-white rounded-br-none shadow-lg" : "bg-white/80 backdrop-blur-md text-[#17322a] rounded-bl-none border border-[#e6d2b3]/40 shadow-md"}`}>
                    <div className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap break-words">
                      <ReactMarkdown>{message.text}</ReactMarkdown>
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </div>
        </ScrollArea>
      </div>

      <form onSubmit={handleSubmit} className="fixed bottom-[60px] left-0 right-0 xl:left-[25%] p-4 border-t border-[#e6d2b3]/30 bg-white/90 backdrop-blur-md z-30">
        <div className="max-w-xl mx-auto">
          <div className="flex gap-2 sm:gap-3 items-center">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 p-3 sm:p-4 border border-[#d3b787]/50 rounded-full focus:outline-none focus:border-[#2A6657] focus:ring-1 focus:ring-[#2A6657] shadow-md text-[#11211c] bg-white/80 backdrop-blur-sm font-sans text-sm sm:text-base"
            />
            <button
              type="submit"
              className="bg-[#2A6657] text-white p-3 sm:p-4 rounded-full hover:bg-[#1d4a3e] transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-[#2A6657]/50 focus:ring-offset-2 shadow-lg"
            >
              <Send className="h-4 w-4 sm:h-5 sm:w-5" />
              <span className="sr-only">Send</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

const Footer = () => (
  <footer className="fixed bottom-0 left-0 right-0 bg-gradient-to-r from-[#2A6657] to-[#1d4a3e] text-white p-4 text-center z-40">
    <p className="font-sans text-sm">© 2025 Wellchemy. All rights reserved.</p>
  </footer>
);
