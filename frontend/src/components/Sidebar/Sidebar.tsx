import React, { useState } from 'react';
import { useProjectStore } from '@/stores/projectStore';
import { useChatStore } from '@/stores/chatStore';
import { Plus, FolderOpen, MessageSquare, Upload, FileText, Trash2 } from 'lucide-react';
import type { Project } from '@/types';

const Sidebar: React.FC = () => {
  const {
    projects,
    currentProject,
    conversations,
    files,
    createProject,
    setCurrentProject,
    deleteProject,
    uploadFile,
  } = useProjectStore();
  
  const { setCurrentConversation, loadConversation, clearMessages } = useChatStore();
  
  const [showNewProject, setShowNewProject] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDesc, setNewProjectDesc] = useState('');
  const [activeTab, setActiveTab] = useState<'conversations' | 'files'>('conversations');

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newProjectName.trim()) {
      const project = await createProject(newProjectName, newProjectDesc);
      if (project) {
        setNewProjectName('');
        setNewProjectDesc('');
        setShowNewProject(false);
        setCurrentProject(project);
      }
    }
  };

  const handleProjectClick = (project: Project) => {
    setCurrentProject(project);
    clearMessages();
  };

  const handleConversationClick = async (conversationId: number) => {
    await loadConversation(conversationId);
  };

  const handleNewChat = () => {
    clearMessages();
    setCurrentConversation(null);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0] && currentProject) {
      await uploadFile(currentProject.id, e.target.files[0]);
    }
  };

  const handleDeleteProject = async (projectId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('确定要删除这个项目吗？所有对话和文件都将被删除。')) {
      await deleteProject(projectId);
    }
  };

  return (
    <aside className="w-80 bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-800">Meta-Agent</h1>
        <p className="text-xs text-gray-500 mt-1">Development System</p>
      </div>

      {/* Projects List */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-700">项目</h2>
            <button
              onClick={() => setShowNewProject(!showNewProject)}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <Plus className="w-4 h-4 text-gray-600" />
            </button>
          </div>

          {/* New Project Form */}
          {showNewProject && (
            <form onSubmit={handleCreateProject} className="mb-3 p-3 bg-gray-50 rounded-lg">
              <input
                type="text"
                placeholder="项目名称"
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded mb-2 text-sm"
                autoFocus
              />
              <textarea
                placeholder="项目描述（可选）"
                value={newProjectDesc}
                onChange={(e) => setNewProjectDesc(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded mb-2 text-sm"
                rows={2}
              />
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 px-3 py-1.5 bg-primary-600 text-white rounded text-sm hover:bg-primary-700"
                >
                  创建
                </button>
                <button
                  type="button"
                  onClick={() => setShowNewProject(false)}
                  className="flex-1 px-3 py-1.5 bg-gray-200 text-gray-700 rounded text-sm hover:bg-gray-300"
                >
                  取消
                </button>
              </div>
            </form>
          )}

          {/* Projects */}
          <div className="space-y-1">
            {projects.map((project) => (
              <div
                key={project.id}
                className={`flex items-center justify-between p-2 rounded cursor-pointer hover:bg-gray-100 ${
                  currentProject?.id === project.id ? 'bg-primary-50 border border-primary-200' : ''
                }`}
                onClick={() => handleProjectClick(project)}
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <FolderOpen className="w-4 h-4 text-gray-500 flex-shrink-0" />
                  <span className="text-sm text-gray-700 truncate">{project.name}</span>
                </div>
                <button
                  onClick={(e) => handleDeleteProject(project.id, e)}
                  className="p-1 hover:bg-red-100 rounded opacity-0 group-hover:opacity-100"
                >
                  <Trash2 className="w-3 h-3 text-red-500" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Project Details */}
        {currentProject && (
          <div className="border-t border-gray-200 p-4">
            {/* Tabs */}
            <div className="flex gap-2 mb-3">
              <button
                onClick={() => setActiveTab('conversations')}
                className={`flex-1 px-3 py-1.5 rounded text-sm font-medium ${
                  activeTab === 'conversations'
                    ? 'bg-primary-100 text-primary-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                对话
              </button>
              <button
                onClick={() => setActiveTab('files')}
                className={`flex-1 px-3 py-1.5 rounded text-sm font-medium ${
                  activeTab === 'files'
                    ? 'bg-primary-100 text-primary-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                文件
              </button>
            </div>

            {/* Conversations Tab */}
            {activeTab === 'conversations' && (
              <div>
                <button
                  onClick={handleNewChat}
                  className="w-full mb-2 px-3 py-2 bg-primary-600 text-white rounded text-sm hover:bg-primary-700 flex items-center justify-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  新建对话
                </button>
                <div className="space-y-1 max-h-64 overflow-y-auto">
                  {conversations.map((conv) => (
                    <div
                      key={conv.id}
                      onClick={() => handleConversationClick(conv.id)}
                      className="p-2 rounded cursor-pointer hover:bg-gray-100 flex items-start gap-2"
                    >
                      <MessageSquare className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-700 truncate">{conv.title}</p>
                        <p className="text-xs text-gray-400">
                          {new Date(conv.updated_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Files Tab */}
            {activeTab === 'files' && (
              <div>
                <label className="w-full mb-2 px-3 py-2 bg-primary-600 text-white rounded text-sm hover:bg-primary-700 flex items-center justify-center gap-2 cursor-pointer">
                  <Upload className="w-4 h-4" />
                  上传文件
                  <input
                    type="file"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
                <div className="space-y-1 max-h-64 overflow-y-auto">
                  {files.map((file) => (
                    <div
                      key={file.id}
                      className="p-2 rounded hover:bg-gray-100 flex items-start gap-2"
                    >
                      <FileText className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-700 truncate">{file.filename}</p>
                        <p className="text-xs text-gray-400">
                          {file.semantic_tag} • {file.chunk_count} chunks
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;
