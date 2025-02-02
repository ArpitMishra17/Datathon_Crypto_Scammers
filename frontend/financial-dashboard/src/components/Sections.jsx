import React from "react";
import axios from 'axios';
import { useState, useEffect } from 'react';
const API_BASE_URL = 'http://127.0.0.1:8000';

export const getFinancialData = async (companyName) => {
  console.log('Fetching financial data for:', companyName);
  try {
    const response = await axios.post(`${API_BASE_URL}/get-top-articles/`, {
      company_name: companyName,
    });
    console.log('Fetched financial-news data:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching financial data:', error);
    throw error;
  }
};

const NewsSection = ({ data }) => {
  return (
  <section id="news" className="min-h-screen pt-20 bg-gray-100 p-6">
    <h2 className="text-2xl font-bold mb-4">News Section</h2>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {data.top_articles?.map((article, index) => (
        <div key={index} className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xl font-semibold text-blue-600 hover:text-blue-800"
          >
            {article.title}
          </a>
          <p className="text-gray-700 mt-2">{article.description}</p>
        </div>
      ))}
    </div>
  </section>
  );
};

// Sections.jsx

export const Sections = ({ query }) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const result = await getFinancialData(query);
      setData(result);
    };
    fetchData();
  }, [query]);

  return (
    <>
      <section id="reports" className="min-h-screen pt-20">
        <h2 className="text-2xl font-bold mb-4">Reports Section</h2>
        {/* Reports content */}
      </section>

      <section id="news" className="min-h-screen pt-20">
        <h2 className="text-2xl font-bold mb-4">News Section</h2>
        {data && <NewsSection data={data} />}
      </section>
    </>
  );
};