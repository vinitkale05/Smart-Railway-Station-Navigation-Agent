import React from 'react';
import { NavigationProvider, useNavigation } from './context/NavigationContext';
import { Header } from './components/Header';
import { AlertBanner } from './components/AlertBanner';
import { WelcomeScreen } from './components/WelcomeScreen';
import { ChatScreen } from './components/ChatScreen';
import { NavigationSplitView } from './components/NavigationSplitView';
import { TrainStatusPanel } from './components/TrainStatusPanel';
import { AdminConsole } from './components/AdminConsole';

const AppContent: React.FC = () => {
  const { activeScreen } = useNavigation();

  return (
    <div className="bg-slate-50 text-slate-900 min-h-screen flex flex-col font-sans">
      <AlertBanner />
      <Header />
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 flex flex-col">
        {activeScreen === 'welcome' && <WelcomeScreen onStartJourney={() => {}} />}
        {activeScreen === 'chat' && <ChatScreen />}
        {activeScreen === 'navigation' && <NavigationSplitView />}
        {activeScreen === 'trains' && <TrainStatusPanel />}
        {activeScreen === 'admin' && <AdminConsole />}
      </main>
      <footer className="bg-slate-900 text-slate-400 text-xs py-3 px-4 text-center">
        Smart Railway Station Navigation Agent • MIT-ADT University Pune • Major Project
      </footer>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <NavigationProvider>
      <AppContent />
    </NavigationProvider>
  );
};

export default App;
