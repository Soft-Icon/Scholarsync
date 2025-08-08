import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Send, Bot, User } from 'lucide-react'
import Sidebar from './Sidebar'

const AIAssistant = ({ user, onLogout }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: `Hello! I'm your ScholarSync AI assistant. How can I help you with scholarships today?`,
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const quickQuestions = [
    "How do I write a good personal statement?",
    "What scholarships match my profile?",
    "Tips for scholarship interviews",
    "Application deadlines this month"
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setLoading(true)

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      })

      if (response.ok) {
        const data = await response.json()
        const botResponse = {
          id: messages.length + 2,
          type: 'bot',
          content: data.response,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, botResponse])
      } else {
        const errorResponse = {
          id: messages.length + 2,
          type: 'bot',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, errorResponse])
      }
    } catch (error) {
      const errorResponse = {
        id: messages.length + 2,
        type: 'bot',
        content: 'Network error. Please check your connection and try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorResponse])
    } finally {
      setLoading(false)
    }
  }

  const generateAIResponse = (question) => {
    // Simple response generation (replace with actual AI)
    if (question.toLowerCase().includes('personal statement')) {
      return `Great question! Here are some tips for writing a compelling personal statement:

1. **Start with a hook** - Begin with an engaging story or experience
2. **Show, don't tell** - Use specific examples to demonstrate your qualities
3. **Connect to your goals** - Explain how the scholarship aligns with your aspirations
4. **Be authentic** - Write in your own voice and be genuine
5. **Proofread carefully** - Ensure there are no grammatical errors

Would you like me to help you brainstorm ideas for your personal statement?`
    }
    
    if (question.toLowerCase().includes('match') || question.toLowerCase().includes('profile')) {
      return `Based on your profile, I found several Computer Science scholarships that might be a good fit:

1. **MTN Foundation Scholarship** - For Nigerian undergraduates in STEM fields (92% match)
2. **Google Africa Developer Scholarship** - For students interested in mobile and web development (85% match)
3. **IBM Quantum Computing Scholarship** - For students interested in quantum computing research (78% match)

Would you like more details about any of these scholarships?`
    }

    return `I understand you're asking about "${question}". While I'm still learning, I can help you with:

• Writing scholarship essays and personal statements
• Finding scholarships that match your profile
• Preparing for scholarship interviews
• Understanding application requirements
• Deadline reminders and planning

What specific aspect would you like help with?`
  }

  const handleQuickQuestion = (question) => {
    setInputMessage(question)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar user={user} onLogout={onLogout} />
      
      <div className="flex-1 p-6">
        <div className="max-w-4xl mx-auto h-full flex flex-col">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Scholarship Assistant</h1>
            <p className="text-gray-600">
              Ask questions about scholarships, application tips, or get personalized recommendations.
            </p>
          </div>

          {/* Quick Questions */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg">Quick Questions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {quickQuestions.map((question, index) => (
                  <Badge
                    key={index}
                    variant="outline"
                    className="cursor-pointer hover:bg-teal-50 hover:border-teal-300"
                    onClick={() => handleQuickQuestion(question)}
                  >
                    {question}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Chat Messages */}
          <Card className="flex-1 flex flex-col">
            <CardContent className="flex-1 p-6 overflow-y-auto max-h-96">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`flex max-w-xs lg:max-w-md ${
                        message.type === 'user' ? 'flex-row-reverse' : 'flex-row'
                      }`}
                    >
                      <div
                        className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                          message.type === 'user' 
                            ? 'bg-teal-600 text-white ml-2' 
                            : 'bg-gray-200 text-gray-600 mr-2'
                        }`}
                      >
                        {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                      </div>
                      <div
                        className={`px-4 py-2 rounded-lg ${
                          message.type === 'user'
                            ? 'bg-teal-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        <p className="text-xs mt-1 opacity-70">
                          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
                
                {loading && (
                  <div className="flex justify-start">
                    <div className="flex flex-row">
                      <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-200 text-gray-600 mr-2 flex items-center justify-center">
                        <Bot className="h-4 w-4" />
                      </div>
                      <div className="px-4 py-2 rounded-lg bg-gray-100">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            </CardContent>

            {/* Message Input */}
            <div className="border-t p-4">
              <div className="flex space-x-2">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message here..."
                  className="flex-1"
                  disabled={loading}
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={loading || !inputMessage.trim()}
                  className="bg-teal-600 hover:bg-teal-700"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default AIAssistant

