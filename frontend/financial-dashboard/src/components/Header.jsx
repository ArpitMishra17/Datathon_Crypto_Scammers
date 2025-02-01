import React from 'react';
import { ScrollNav } from './ScrollNav';

export default function Header({ onChatClick }) {
    
    return (
      <header className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
        <h1 className="text-2xl font-bold text-gray-900">AI Financial Insights</h1>
        <nav className="flex  gap-3">
            <ScrollNav />
          <button
           className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" onClick={onChatClick}>
            Chat
          </button>
        </nav>
      </header>
    );
  };

