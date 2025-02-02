import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

export const getFinancialData = async (companyName) => {
  console.log('Fetching financial data for:', companyName);
  try {
    const response = await axios.post(`${API_BASE_URL}/get-financial-data/`, {
      company_name: companyName,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching financial data:', error);
    throw error;
  }
};

export default function RevenueChart({ query }) {
  const [financialData, setFinancialData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getFinancialData(query);
        console.log('Fetched financial data:', data);

        // Transform the data for the chart
        const transformedData = Object.keys(data.financial_data.revenue).map((year) => ({
          year: parseInt(year),
          revenue: data.financial_data.revenue[year],
          profit: data.financial_data.net_income[year],
        }));

        setFinancialData(transformedData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching financial data:', err);
        setError(err);
        setLoading(false);
      }
    };

    if (query) {
      fetchData();
    }
  }, [query]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div className="h-64 w-full">
      <h2 className="text-lg font-semibold mb-4">Financial Data for {query}</h2>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={financialData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="revenue"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Revenue"
          />
          <Line
            type="monotone"
            dataKey="profit"
            stroke="#10b981"
            strokeWidth={2}
            name="Profit"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}