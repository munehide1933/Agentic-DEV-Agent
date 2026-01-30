import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { Message } from '@/types';
import { Bot, User, Clock, AlertTriangle, Code } from 'lucide-react';
import { format } from 'date-fns';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
      {messages.length === 0 && !isLoading && (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <Bot className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">开始新的对话</p>
            <p className="text-sm text-gray-400 mt-2">
              我是你的AI开发助手，支持多角色协作开发
            </p>
          </div>
        </div>
      )}

      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}

      {isLoading && (
        <div className="flex items-start gap-4">
          <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
            <Bot className="w-5 h-5 text-primary-600" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-medium text-gray-700">AI Assistant</span>
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
            <div className="text-sm text-gray-500">正在思考...</div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const hasMetadata = message.meta_info && Object.keys(message.meta_info).length > 0;

  return (
    <div className={`flex items-start gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-gray-200' : 'bg-primary-100'
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5 text-gray-600" />
        ) : (
          <Bot className="w-5 h-5 text-primary-600" />
        )}
      </div>

      {/* Content */}
      <div className={`flex-1 ${isUser ? 'flex flex-col items-end' : ''}`}>
        {/* Header */}
        <div className={`flex items-center gap-2 mb-2 ${isUser ? 'flex-row-reverse' : ''}`}>
          <span className="font-medium text-gray-700">
            {isUser ? 'You' : 'AI Assistant'}
          </span>
          {message.meta_info?.workflow_phase && (
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
              {message.meta_info.workflow_phase}
            </span>
          )}
          <span className="text-xs text-gray-400 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {format(new Date(message.created_at), 'HH:mm')}
          </span>
        </div>

        {/* Message Content */}
        <div
          className={`prose prose-sm max-w-none ${
            isUser
              ? 'bg-primary-600 text-white px-4 py-3 rounded-2xl rounded-tr-sm'
              : 'bg-gray-50 px-4 py-3 rounded-2xl rounded-tl-sm'
          }`}
        >
          {isUser ? (
            <p className="text-white whitespace-pre-wrap">{message.content}</p>
          ) : (
            <ReactMarkdown
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* Metadata */}
        {hasMetadata && !isUser && (
          <div className="mt-3 space-y-2">
            {/* Code Modifications */}
{message.meta_info?.code_modifications && message.meta_info.code_modifications.length > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <Code className="w-4 h-4 text-amber-600" />
                  <span className="text-sm font-medium text-amber-800">
                    代码修改 ({message.meta_info.code_modifications.length})
                  </span>
                </div>
                <div className="space-y-1">
                  {message.meta_info.code_modifications.map((mod, idx) => (
                    <div key={idx} className="text-xs text-amber-700">
                      <span className="font-mono">{mod.file_path}</span>
                      <span className="ml-2 px-1.5 py-0.5 bg-amber-200 rounded">
                        {mod.modification_type}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Security Warnings */}
            {message.meta_info?.security_warnings && message.meta_info.security_warnings.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  <span className="text-sm font-medium text-red-800">安全提示</span>
                </div>
                <div className="space-y-1">
                  {message.meta_info.security_warnings.map((warning, idx) => (
                    <p key={idx} className="text-xs text-red-700">
                      {warning}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {/* Token Usage */}
            {message.meta_info?.usage && (
              <div className="text-xs text-gray-400">
                Tokens: {message.meta_info.usage.total_tokens} (
                {message.meta_info.usage.prompt_tokens} prompt + {message.meta_info.usage.completion_tokens} completion)
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageList;
