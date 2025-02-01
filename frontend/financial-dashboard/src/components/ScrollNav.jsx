
import React from 'react';

// ScrollNav.jsx
export const ScrollNav = () => {
    const scrollToSection = (sectionId) => {
      const section = document.getElementById(sectionId);
      if (section) {
        section.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    };
  
    return (
      <nav className=" w-full bg-gray-50 ">
        <div className="max-w-7xl mx-auto px-4 py-3 flex gap-6">
          <button 
            onClick={() => scrollToSection('reports')}
            className="hover:text-blue-600 transition-colors"
          >
            Reports
          </button>
          <button 
            onClick={() => scrollToSection('insights')}
            className="hover:text-blue-600 transition-colors"
          >
            Insights
          </button>
          <button 
            onClick={() => scrollToSection('news')}
            className="hover:text-blue-600 transition-colors"
          >
            News
          </button>
        </div>
      </nav>
    );
  };