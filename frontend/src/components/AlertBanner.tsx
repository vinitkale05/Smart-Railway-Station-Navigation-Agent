import React from 'react';
import { useNavigation } from '../context/NavigationContext';

export const AlertBanner: React.FC = () => {
  const { liveAlert, setLiveAlert } = useNavigation();

  if (!liveAlert) return null;

  return (
    <div className="bg-amber-600 text-white px-4 py-3 shadow-md flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <span className="text-xl">⚠️</span>
        <div>
          <span className="font-bold text-sm block">{liveAlert.title}</span>
          <span className="text-xs">{liveAlert.message}</span>
        </div>
      </div>
      <button
        onClick={() => setLiveAlert(null)}
        className="bg-amber-700 hover:bg-amber-800 px-3 py-1 rounded text-xs font-semibold"
      >
        Dismiss
      </button>
    </div>
  );
};
