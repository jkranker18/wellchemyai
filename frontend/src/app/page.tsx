"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { api } from "@/services/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Bot, Send, MessageSquare, History, Calendar, Leaf, ChevronRight } from "lucide-react"

interface Message {
  id: number
  text: string
  isUser: boolean
}

const Header = () => (
  <header className="bg-gradient-to-r from-green-600 to-green-800 text-white p-4 shadow-lg sticky top-0 z-10">
    <div className="container mx-auto flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="bg-white/20 p-2 rounded-full">
          <img src="/Wellchemy white apple.png" alt="Wellchemy Logo" className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Wellchemy</h1>
          <p className="text-sm text-green-100">Your AI Wellness Assistant</p>
        </div>
      </div>
      <Button variant="ghost" className="text-white hover:bg-white/10">
        <Calendar className="h-5 w-5 mr-2" />
        My Wellness Plan
      </Button>
    </div>
  </header>
)

const LeftRail = () => (
  <div className="bg-white rounded-r-xl shadow-md h-full border-r border-gray-100">
    <div className="p-5">
      <h2 className="text-lg font-semibold mb-4 text-gray-800 flex items-center gap-2">
        <History className="h-5 w-5 text-green-600" />
        Chat History
      </h2>
      <ul className="space-y-3">
        <li className="p-3 bg-green-50 rounded-lg hover:bg-green-100 cursor-pointer transition-colors border border-green-100 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Today's Chat</span>
            <ChevronRight className="h-4 w-4 text-green-600" />
          </div>
        </li>
        <li className="p-3 bg-white rounded-lg hover:bg-green-50 cursor-pointer transition-colors border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Dietary Assessment</span>
            <ChevronRight className="h-4 w-4 text-gray-400" />
          </div>
        </li>
        <li className="p-3 bg-white rounded-lg hover:bg-green-50 cursor-pointer transition-colors border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Wellness Plan</span>
            <ChevronRight className="h-4 w-4 text-gray-400" />
          </div>
        </li>
      </ul>
    </div>

    <div className="mt-6 p-5">
      <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
        <CardContent className="p-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-green-600 p-2 rounded-full">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <h3 className="font-semibold text-green-800">Wellness Tip</h3>
          </div>
          <p className="text-sm text-gray-700">
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
    <div className="flex flex-col h-full bg-gradient-to-br from-green-50 via-white to-green-50">
      <div className="p-4 border-b border-gray-100 bg-white/80 backdrop-blur-sm">
        <div className="max-w-3xl mx-auto flex items-center gap-2">
          <div className="bg-green-100 p-2 rounded-full">
            <MessageSquare className="h-5 w-5 text-green-600" />
          </div>
          <h2 className="font-semibold text-gray-800">Wellness Conversation</h2>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}>
              {!message.isUser && (
                <div className="w-8 h-8 rounded-full bg-green-600 flex items-center justify-center text-white mr-2 mt-1 flex-shrink-0">
                  <Bot className="h-4 w-4" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-2xl px-5 py-3 shadow-sm ${
                  message.isUser
                    ? "bg-gradient-to-r from-green-600 to-green-700 text-white rounded-br-none"
                    : "bg-white text-gray-800 rounded-bl-none border border-gray-100"
                }`}
              >
                <p className="text-sm sm:text-base leading-relaxed">{message.text}</p>
              </div>
              {message.isUser && (
                <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-600 ml-2 mt-1 flex-shrink-0">
                  <div className="w-4 h-4 rounded-full bg-green-600"></div>
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <form onSubmit={handleSubmit} className="border-t border-gray-200 bg-white p-4 shadow-lg">
        <div className="max-w-3xl mx-auto">
          <div className="flex gap-2 items-center">
            <Input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 p-3 border border-gray-300 rounded-full focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 shadow-sm text-black"
            />
            <Button
              type="submit"
              className="bg-green-600 text-white px-6 py-6 rounded-full hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 shadow-md"
            >
              <Send className="h-5 w-5" />
              <span className="sr-only">Send</span>
            </Button>
          </div>
          <div className="mt-2 text-xs text-center text-gray-500">
            Ask about nutrition, wellness plans, or dietary recommendations
          </div>
        </div>
      </form>
    </div>
  )
}

const Footer = () => (
  <footer className="bg-gradient-to-r from-green-700 to-green-800 text-white p-4 text-center text-sm">
    <p>© 2025 Wellchemy. All rights reserved.</p>
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
    <div className="flex flex-col h-screen bg-white">
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
