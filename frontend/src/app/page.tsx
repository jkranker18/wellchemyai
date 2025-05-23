"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { api } from "@/services/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, MessageSquare, History, Calendar, Leaf, ChevronRight, Sparkles, Apple } from "lucide-react"

interface Message {
  id: number
  text: string
  isUser: boolean
}

const Header = () => (
  <header className="bg-gradient-to-r from-[#2A6657] to-[#1d4a3e] text-white p-4 shadow-lg sticky top-0 z-10">
    <div className="container mx-auto flex items-center justify-between">
      <div className="flex items-center justify-center gap-3">
        <div className="bg-white/20 p-2 rounded-full backdrop-blur-sm">
          <Apple className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-display font-semibold tracking-tight">Wellchemy</h1>
          <p className="text-sm text-[#f7eee3] font-sans">Your AI Wellness Assistant</p>
        </div>
      </div>
      <Button variant="ghost" className="text-white hover:bg-white/10 rounded-xl font-sans">
        <Calendar className="h-5 w-5 mr-2" />
        My Wellness Plan
      </Button>
    </div>
  </header>
)

const LeftRail = () => (
  <div className="bg-gradient-to-b from-[#f0f9f0] to-white rounded-r-2xl shadow-md h-full border-r border-[#e6d2b3]/30">
    <div className="p-6">
      <h2 className="text-xl font-display font-semibold mb-5 text-[#11211c] flex items-center gap-2">
        <History className="h-5 w-5 text-[#2A6657]" />
        Chat History
      </h2>
      <ul className="space-y-4">
        <li className="p-4 bg-[#2A6657]/10 rounded-2xl hover:bg-[#2A6657]/15 cursor-pointer transition-all duration-300 border border-[#2A6657]/20 shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-[#17322a]">Today's Chat</span>
            <ChevronRight className="h-4 w-4 text-[#2A6657]" />
          </div>
        </li>
        <li className="p-4 bg-white/80 backdrop-blur-md rounded-2xl hover:bg-[#f7eee3]/50 cursor-pointer transition-all duration-300 border border-[#e6d2b3]/30 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-[#17322a]">Dietary Assessment</span>
            <ChevronRight className="h-4 w-4 text-[#c19e63]" />
          </div>
        </li>
        <li className="p-4 bg-white/80 backdrop-blur-md rounded-2xl hover:bg-[#f7eee3]/50 cursor-pointer transition-all duration-300 border border-[#e6d2b3]/30 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-[#17322a]">Wellness Plan</span>
            <ChevronRight className="h-4 w-4 text-[#c19e63]" />
          </div>
        </li>
      </ul>
    </div>

    <div className="mt-6 p-6">
      <Card className="bg-gradient-to-br from-[#f7eee3] to-white border-[#d3b787] rounded-2xl overflow-hidden shadow-lg">
        <CardContent className="p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-[#2A6657] p-2.5 rounded-full shadow-md">
              <Leaf className="h-5 w-5 text-white" />
            </div>
            <h3 className="font-display font-semibold text-[#11211c] text-lg">Wellness Tip</h3>
          </div>
          <p className="text-[#17322a] leading-relaxed">
            Try incorporating more leafy greens into your diet for increased energy and better digestion.
          </p>
        </CardContent>
      </Card>
    </div>
  </div>
)

const ChatArea = ({ messages, onSendMessage }: { messages: Message[]; onSendMessage: (text: string) => void }) => {
  const [inputText, setInputText] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputText.trim()) {
      onSendMessage(inputText)
      setInputText("")
    }
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-[#f0f9f0] via-white to-[#f0f9f0]">
      <div className="p-4 border-b border-[#e6d2b3]/30 bg-white/80 backdrop-blur-md">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <div className="bg-[#2A6657]/10 p-2.5 rounded-full">
            <MessageSquare className="h-5 w-5 text-[#2A6657]" />
          </div>
          <h2 className="font-display font-semibold text-xl text-[#11211c]">Wellness Conversation</h2>
        </div>
      </div>

      <ScrollArea className="flex-1 p-6">
        <div className="max-w-3xl mx-auto space-y-8">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}
            >
              {!message.isUser && (
                <div className="w-10 h-10 rounded-full bg-[#2A6657] flex items-center justify-center text-white mr-3 mt-1 flex-shrink-0 shadow-md">
                  <Sparkles className="h-5 w-5" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-2xl px-6 py-4 ${
                  message.isUser
                    ? "bg-gradient-to-r from-[#2A6657] to-[#1d4a3e] text-white rounded-br-none shadow-lg"
                    : "bg-white/80 backdrop-blur-md text-[#17322a] rounded-bl-none border border-[#e6d2b3]/40 shadow-md"
                }`}
              >
                <p className="text-base leading-relaxed">{message.text}</p>
              </div>
              {message.isUser && (
                <div className="w-10 h-10 rounded-full bg-[#f7eee3] flex items-center justify-center text-[#2A6657] ml-3 mt-1 flex-shrink-0 shadow-md border border-[#e6d2b3]/40">
                  <div className="w-5 h-5 rounded-full bg-[#2A6657]"></div>
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <form onSubmit={handleSubmit} className="border-t border-[#e6d2b3]/30 bg-white/90 backdrop-blur-md p-5 shadow-lg">
        <div className="max-w-3xl mx-auto">
          <div className="flex gap-3 items-center">
            <Input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 p-4 border border-[#d3b787]/50 rounded-full focus:outline-none focus:border-[#2A6657] focus:ring-1 focus:ring-[#2A6657] shadow-md text-[#11211c] bg-white/80 backdrop-blur-sm font-sans text-base"
            />
            <Button
              type="submit"
              className="bg-[#2A6657] text-white px-6 py-6 rounded-full hover:bg-[#1d4a3e] transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-[#2A6657]/50 focus:ring-offset-2 shadow-lg"
            >
              <Send className="h-5 w-5" />
              <span className="sr-only">Send</span>
            </Button>
          </div>
          <div className="mt-3 text-sm text-center text-[#17322a] font-sans">
            Ask about nutrition, wellness plans, or dietary recommendations
          </div>
        </div>
      </form>
    </div>
  )
}

const Footer = () => (
  <footer className="bg-gradient-to-r from-[#2A6657] to-[#1d4a3e] text-white p-4 text-center">
    <p className="font-sans text-sm">© 2025 Wellchemy. All rights reserved.</p>
  </footer>
)

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your Wellchemy AI assistant. How can I help you today?",
      isUser: false,
    },
  ])

  const handleSendMessage = async (text: string) => {
    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text,
      isUser: true,
    }
    setMessages((prev) => [...prev, userMessage])

    try {
      // Send message to backend
      const response = await api.chat(text)

      // Add AI response
      if (response.success) {
        const aiMessage: Message = {
          id: messages.length + 2,
          text: response.data.response,
          isUser: false,
        }
        setMessages((prev) => [...prev, aiMessage])
      } else {
        // Handle error
        const errorMessage: Message = {
          id: messages.length + 2,
          text: "Sorry, I encountered an error. Please try again.",
          isUser: false,
        }
        setMessages((prev) => [...prev, errorMessage])
      }
    } catch (error) {
      console.error("Error sending message:", error)
      const errorMessage: Message = {
        id: messages.length + 2,
        text: "Sorry, I encountered an error. Please try again.",
        isUser: false,
      }
      setMessages((prev) => [...prev, errorMessage])
    }
  }

  return (
    <div className="flex flex-col h-screen bg-[#f0f9f0]">
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
  )
}

// Add this to globals.css or include it inline for the animation
const fadeIn = `
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`
