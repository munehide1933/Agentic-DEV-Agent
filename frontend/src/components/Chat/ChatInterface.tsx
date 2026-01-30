import React from 'react';
import { useProjectStore } from '@/stores/projectStore';
import { useChatStore } from '@/stores/chatStore';
import MessageList from './MessageList';
import InputArea from './InputArea';
import { AlertCircle } from 'lucide-react';

const ChatInterface: React.FC = () => {
  const { currentProject } = useProjectStore();
  const { messages, isLoading, error } = useChatStore();

  if (!currentProject) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">
            欢迎使用 Meta-Agent
          </h2>
          <p className="text-gray-500">
            请在左侧创建或选择一个项目开始
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      {/* Header */}
      <header className="px-6 py-4 border-b border-gray-200 bg-white">
        <h2 className="text-lg font-semibold text-gray-800">
          {currentProject.name}
        </h2>
        {currentProject.description && (
          <p className="text-sm text-gray-500 mt-1">
            {currentProject.description}
          </p>
        )}
      </header>

      {/* Error Display */}
      {error && (
        <div className="mx-6 mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-medium text-red-800">错误</h3>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Messages */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Input */}
      <InputArea />
    </div>
  );
};

export default ChatInterface;
