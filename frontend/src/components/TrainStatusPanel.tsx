import React, { useState, useEffect } from 'react';
import { Train } from '../types';
import { fetchTrains } from '../services/api';
import { useNavigation } from '../context/NavigationContext';

export const TrainStatusPanel: React.FC = () => {
  const [trains, setTrains] = useState<Train[]>([]);
  const [search, setSearch] = useState('');
  const { setCurrentTrain, setActiveScreen } = useNavigation();

  useEffect(() => {
    fetchTrains().then(setTrains).catch(console.error);
  }, []);

  const filtered = trains.filter(t =>
    t.train_no.includes(search) ||
    t.name.toLowerCase().includes(search.toLowerCase()) ||
    t.destination.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex-1 bg-white rounded-2xl shadow border border-slate-200 p-6 flex flex-col">
      <div className="flex items-center justify-between pb-4 border-b border-slate-200 mb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Train Schedule & Platform Allocation</h2>
          <p className="text-xs text-slate-500">Live platform assignments and delays across Pune Junction</p>
        </div>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search train no. or name..."
          className="px-3 py-2 border border-slate-300 rounded-lg text-sm w-72 outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="flex-1 overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-600">
          <thead className="bg-slate-100 text-slate-800 font-semibold uppercase text-xs">
            <tr>
              <th className="py-3 px-4">Train No.</th>
              <th className="py-3 px-4">Train Name</th>
              <th className="py-3 px-4">Destination</th>
              <th className="py-3 px-4">Scheduled</th>
              <th className="py-3 px-4">Platform</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {filtered.map(t => (
              <tr key={t.train_no} className="hover:bg-slate-50">
                <td className="py-3 px-4 font-mono font-bold text-slate-800">{t.train_no}</td>
                <td className="py-3 px-4 font-semibold text-slate-800">{t.name}</td>
                <td className="py-3 px-4 text-xs">{t.destination}</td>
                <td className="py-3 px-4 font-mono font-bold">{t.scheduled_departure}</td>
                <td className="py-3 px-4 font-bold text-blue-700">{t.current_platform || t.default_platform}</td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-0.5 rounded text-xs font-semibold ${t.delay_minutes > 0 ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}`}>
                    {t.status}
                  </span>
                </td>
                <td className="py-3 px-4 text-center">
                  <button
                    onClick={() => {
                      setCurrentTrain(t.train_no);
                      setActiveScreen('chat');
                    }}
                    className="px-3 py-1 bg-blue-50 text-blue-700 hover:bg-blue-600 hover:text-white rounded-lg text-xs font-semibold transition"
                  >
                    Guide Me
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
