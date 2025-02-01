import React from 'react';
export default function MetricCard({ title, value, change }) {
    const isPositive = change?.includes('+');
    const isNegative = change?.includes('↓');
  
    return (
      <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        <p className="text-3xl font-semibold mt-2">{value}</p>
        {change && (
          <div className={`mt-2 flex items-center text-sm ${
            isPositive ? 'text-green-600' : 
            isNegative ? 'text-red-600' : 'text-gray-500'
          }`}>
            {isPositive && <span className="mr-1">↑</span>}
            {isNegative && <span className="mr-1">↓</span>}
            {change}
          </div>
        )}
      </div>
    );
  }