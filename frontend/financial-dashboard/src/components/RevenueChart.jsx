import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { month: 'Jan', revenue: 8000, profit: 2400 },
  { month: 'Feb', revenue: 9500, profit: 2800 },
  { month: 'Mar', revenue: 7000, profit: 2200 },
  { month: 'Apr', revenue: 8500, profit: 2600 },
  { month: 'May', revenue: 9000, profit: 2900 },
  { month: 'Jun', revenue: 9200, profit: 3100 },
];

export default function RevenueChart() {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Line 
            type="monotone" 
            dataKey="revenue" 
            stroke="#3b82f6" 
            strokeWidth={2}
          />
          <Line 
            type="monotone" 
            dataKey="profit" 
            stroke="#10b981" 
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}