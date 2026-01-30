import React, { useEffect } from 'react';
import { useProjectStore } from '@/stores/projectStore';
import Sidebar from '../Sidebar/Sidebar';
import ChatInterface from '../Chat/ChatInterface';

const MainLayout: React.FC = () => {
  const { loadProjects } = useProjectStore();

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden">
        <ChatInterface />
      </main>
    </div>
  );
};

export default MainLayout;
