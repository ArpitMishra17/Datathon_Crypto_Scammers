import React from 'react';

export default function Header() {
    return (
      <header className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
        <h1 className="text-2xl font-bold text-gray-900">AI Financial Insights</h1>
        <nav className="flex flex-wrap gap-3">
          {['Reports', 'All Insights', 'News'].map((item) => (
            <button key={item} className="text-gray-600 hover:text-gray-900 px-2 py-1">
              {item}
            </button>
          ))}
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Chat
          </button>
        </nav>
      </header>
    );
  }