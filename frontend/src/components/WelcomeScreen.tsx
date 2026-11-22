import React, { useState } from 'react';
import { useNavigation } from '../context/NavigationContext';

export const WelcomeScreen: React.FC<{ onStartJourney: (trainNo: string, startLoc: string, isAcc: boolean) => void }> = ({ onStartJourney }) => {
  const { setCurrentLocation, setCurrentTrain, setIsAccessible, setActiveScreen } = useNavigation();
  const [train, setTrain] = useState('');
  const [startLoc, setStartLoc] = useState('gate_1_main');
  const [accessible, setAccessible] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentTrain(train || null);
    setCurrentLocation(startLoc);
    setIsAccessible(accessible);
    setActiveScreen('chat');
    onStartJourney(train, startLoc, accessible);
  };

  return (
    <div className="max-w-2xl mx-auto my-auto py-8 w-full">
      <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 text-blue-600 mb-3 text-3xl">
            🧳
          </div>
          <h2 className="text-2xl font-bold text-slate-800">Welcome to Pune Junction</h2>
          <p className="text-slate-600 text-sm mt-1">Let our AI agent guide you smoothly from station entry to your train coach.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Select Station</label>
            <select className="w-full px-4 py-2.5 rounded-lg border border-slate-300 bg-slate-50 outline-none">
              <option value="pune_junction">Pune Junction (PUNE) - Central Railway</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Train Number or Name (Optional)</label>
            <input
              type="text"
              value={train}
              onChange={(e) => setTrain(e.target.value)}
              placeholder="e.g. 12951, 12124 (Deccan Queen)"
              className="w-full px-4 py-2.5 rounded-lg border border-slate-300 outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Your Starting Location</label>
            <select
              value={startLoc}
              onChange={(e) => setStartLoc(e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg border border-slate-300 bg-slate-50 outline-none"
            >
              <option value="gate_1_main">Gate 1 (Main Entrance / Concourse)</option>
              <option value="gate_2_reservation">Gate 2 (PRS Ticket Office Entrance)</option>
              <option value="gate_4_parking">Gate 4 (Parking & Auto Stand)</option>
              <option value="gate_3_east">Gate 3 (East Side Sassoon Exit)</option>
            </select>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start space-x-3">
            <input
              type="checkbox"
              id="accCheck"
              checked={accessible}
              onChange={(e) => setAccessible(e.target.checked)}
              className="mt-1 w-5 h-5 text-blue-600 rounded"
            />
            <div>
              <label htmlFor="accCheck" className="font-semibold text-slate-800 text-sm cursor-pointer">
                ♿ Require Step-Free / Accessible Route
              </label>
              <p className="text-xs text-slate-600 mt-0.5">Mandates lifts and gentle ramps; strictly avoids stairs. Recommended for wheelchairs and heavy luggage.</p>
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl shadow-lg transition"
          >
            Start Station Journey →
          </button>
        </form>
      </div>
    </div>
  );
};
