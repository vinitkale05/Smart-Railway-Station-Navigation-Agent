import React from 'react';
import { useNavigation } from '../context/NavigationContext';

export const Header: React.FC = () => {
  const { activeScreen, setActiveScreen, toggleHighContrast } = useNavigation();

  return (
    <header className="bg-slate-900 text-white shadow-lg sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveScreen('welcome')}>
          <div className="bg-blue-600 text-white w-10 h-10 rounded-lg flex items-center justify-center font-black text-xl shadow">
            🚆
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight flex items-center gap-2">
              Smart Railway Station Navigation Agent
              <span className="text-xs font-normal bg-blue-800 text-blue-200 px-2 py-0.5 rounded-full">Pune Jn (PUNE)</span>
            </h1>
            <p className="text-xs text-slate-400 hidden sm:block">MIT-ADT University AI Major Project • Accessibility & Multi-intent Routing</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 sm:space-x-4 text-sm font-medium">
          <button
            onClick={() => setActiveScreen('chat')}
            className={`px-3 py-1.5 rounded-md transition ${activeScreen === 'chat' ? 'bg-blue-700' : 'hover:bg-slate-800'}`}
          >
            Chat
          </button>
          <button
            onClick={() => setActiveScreen('navigation')}
            className={`px-3 py-1.5 rounded-md transition ${activeScreen === 'navigation' ? 'bg-blue-700' : 'hover:bg-slate-800'}`}
          >
            Map & Directions
          </button>
          <button
            onClick={() => setActiveScreen('trains')}
            className={`px-3 py-1.5 rounded-md transition ${activeScreen === 'trains' ? 'bg-blue-700' : 'hover:bg-slate-800'}`}
          >
            Train Status
          </button>
          <button
            onClick={() => setActiveScreen('admin')}
            className={`px-3 py-1.5 rounded-md transition ${activeScreen === 'admin' ? 'bg-blue-700' : 'hover:bg-slate-800'}`}
          >
            Admin
          </button>

          <button
            onClick={toggleHighContrast}
            title="Toggle High Contrast Mode"
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-yellow-300"
          >
            ◐
          </button>
        </div>
      </div>
    </header>
  );
};
