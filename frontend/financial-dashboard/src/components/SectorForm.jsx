import { useState } from 'react';
import React from 'react';

export default function SectorForm() {
  const [selectedSector, setSelectedSector] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedSector) {
      alert('Please select a sector');
      return;
    }

    // Simulate sending data to the backend
    try {
      const response = await fetch('/api/sectors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sector: selectedSector }),
      });

      if (!response.ok) {
        throw new Error('Failed to send data to the backend');
      }

      const result = await response.json();
      console.log('Backend response:', result);
      alert(`Sector "${selectedSector}" sent successfully!`);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to send sector to the backend');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 rounded-lg">
      <div className="flex items-center">
        <select
          id="sector"
          name="sector"
          value={selectedSector}
          onChange={(e) => setSelectedSector(e.target.value)}
          required
          className="flex-1 p-2 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="">Search by Sector</option>
          <option value="Healthcare">Healthcare</option>
          <option value="Technology & Communication Services">Technology & Communication Services</option>
          <option value="Financials & Real Estate">Financials & Real Estate</option>
          <option value="Consumer Goods">Consumer Goods</option>
          <option value="Industrials & Energy">Industrials & Energy</option>
        </select>
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded-r-lg hover:bg-blue-700 transition-colors"
        >
          Submit
        </button>
      </div>
    </form>
  );
}