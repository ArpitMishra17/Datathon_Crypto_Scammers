import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { sector: 'Tech', value: 32 },
  { sector: 'Finance', value: 24 },
  { sector: 'Healthcare', value: 16 },
  { sector: 'Energy', value: 8 },
  { sector: 'Consumer', value: 12 },
];

export default function MarketTrends() {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="sector" />
          <YAxis />
          <Tooltip />
          <Bar 
            dataKey="value" 
            fill="#8b5cf6" 
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}