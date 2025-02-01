import React from 'react';
import Header from './components/Header';
import MetricCard from './components/MetricCard';
import RevenueChart from './components/RevenueChart';
import MarketTrends from './components/MarketTrends';

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <Header />

        {/* Metric Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricCard
            title="Total Revenue"
            value="$45,231.89"
            change="+20.5% from last month"
          />
          <MetricCard
            title="Profit Margin"
            value="23.4%"
            change="↓2.6% from last month"
          />
          <MetricCard
            title="Active Customers"
            value="2,350"
            change="+180 from last month"
          />
          <MetricCard
            title="Risk Score"
            value="Low"
            change="No change from last month"
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <h2 className="text-lg font-semibold mb-4">Revenue vs Profit</h2>
            <RevenueChart />
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <h2 className="text-lg font-semibold mb-4">Market Trends</h2>
            <MarketTrends />
          </div>
        </div>

        {/* Download Button */}
        <div className="flex justify-end">
          <button className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            Download PDF Report
          </button>
        </div>
      </div>
    </div>
  );
}