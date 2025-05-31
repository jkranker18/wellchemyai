"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { api } from "@/services/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, MessageSquare, History, Calendar, Leaf, ChevronRight, Sparkles } from "lucide-react"
import Image from "next/image"
import ReactMarkdown from "react-markdown"

interface Message {
  id: number
  text: string
  isUser: boolean
}

const Header = () => (
  <header className="bg-gradient-to-r from-[#2A6657] to-[#1d4a3e] text-white p-4 shadow-lg fixed top-0 left-0 right-0 z-50">
    <div className="container mx-auto flex items-center justify-center">
      <div className="flex items-center justify-center gap-3">
        <Image
          src="/Wellchemy white apple.png"
          alt="Wellchemy Logo"
          width={40}
          height={40}
          className="object-contain"
        />
        <div className="text-center">
          <h1 className="text-2xl font-display font-semibold tracking-tight">Wellchemy</h1>
          <p className="text-sm text-[#f7eee3] font-sans">Your AI Wellness Assistant</p>
        </div>
      </div>
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
    <div className="flex flex-col h-[calc(100vh-72px)] bg-gradient-to-br from-[#f0f9f0] via-white to-[#f0f9f0]">
      <div className="p-4 border-b border-[#e6d2b3]/30 bg-white/80 backdrop-blur-md">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <div className="bg-[#2A6657]/10 p-2.5 rounded-full">
            <MessageSquare className="h-5 w-5 text-[#2A6657]" />
          </div>
          <h2 className="font-display font-semibold text-xl text-[#11211c]">Wellness Conversation</h2>
        </div>
      </div>

      <ScrollArea className="flex-1 p-3 sm:p-4">
        <div className="max-w-xl mx-auto space-y-4 sm:space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}
            >
              {!message.isUser && (
                <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-[#2A6657] flex items-center justify-center text-white mr-2 sm:mr-3 mt-1 flex-shrink-0 shadow-md">
                  <Sparkles className="h-4 w-4 sm:h-5 sm:w-5" />
                </div>
              )}
              <div
                className={`max-w-[85%] sm:max-w-[80%] rounded-2xl px-4 sm:px-6 py-3 sm:py-4 ${
                  message.isUser
                    ? "bg-gradient-to-r from-[#2A6657] to-[#1d4a3e] text-white rounded-br-none shadow-lg"
                    : "bg-white/80 backdrop-blur-md text-[#17322a] rounded-bl-none border border-[#e6d2b3]/40 shadow-md"
                }`}
              >
                <div className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap break-words">
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                </div>
              </div>
              {message.isUser && (
                <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-[#f7eee3] flex items-center justify-center text-[#2A6657] ml-2 sm:ml-3 mt-1 flex-shrink-0 shadow-md border border-[#e6d2b3]/40">
                  <div className="w-4 h-4 sm:w-5 sm:h-5 rounded-full bg-[#2A6657]"></div>
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <form onSubmit={handleSubmit} className="border-t border-[#e6d2b3]/30 bg-white/90 backdrop-blur-md p-3 sm:p-4 shadow-lg">
        <div className="max-w-xl mx-auto">
          <div className="flex gap-2 sm:gap-3 items-center">
            <Input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 p-3 sm:p-4 border border-[#d3b787]/50 rounded-full focus:outline-none focus:border-[#2A6657] focus:ring-1 focus:ring-[#2A6657] shadow-md text-[#11211c] bg-white/80 backdrop-blur-sm font-sans text-sm sm:text-base"
            />
            <Button
              type="submit"
              className="bg-[#2A6657] text-white p-3 sm:p-4 rounded-full hover:bg-[#1d4a3e] transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-[#2A6657]/50 focus:ring-offset-2 shadow-lg"
            >
              <Send className="h-4 w-4 sm:h-5 sm:w-5" />
              <span className="sr-only">Send</span>
            </Button>
          </div>
          <div className="mt-2 sm:mt-3 text-xs sm:text-sm text-center text-[#17322a] font-sans">
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
    const userMessage: Message = {
      id: messages.length + 1,
      text,
      isUser: true,
    }
    setMessages((prev) => [...prev, userMessage])

    try {
      let userId = localStorage.getItem("user_id")
      if (!userId) {
        userId = "default"  // Use default if no user_id exists
      }
      const response = await api.chat(text, userId)

      if (response.success) {
        const aiMessage: Message = {
          id: messages.length + 2,
          text: response.data.response,
          isUser: false,
        }
        setMessages((prev) => [...prev, aiMessage])

        if (response.data?.user_id) {
          localStorage.setItem("user_id", response.data.user_id)
        }
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: messages.length + 2,
            text: "Sorry, I encountered an error. Please try again.",
            isUser: false,
          },
        ])
      }
    } catch (error) {
      console.error("Error sending message:", error)
      setMessages((prev) => [
        ...prev,
        {
          id: messages.length + 2,
          text: "Sorry, I encountered an error. Please try again.",
          isUser: false,
        },
      ])
    }
  }

  return (
    <div className="flex flex-col min-h-screen bg-[#f0f9f0]">
      <Header />
      <div className="flex flex-1 overflow-hidden pt-[72px]">
        <div className="w-1/4 min-w-[250px] hidden xl:block">
          <LeftRail />
        </div>
        <div className="w-full xl:w-3/4">
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
