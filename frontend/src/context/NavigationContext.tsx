import React, { createContext, useContext, useState, useEffect } from 'react';
import { StationGraph, RouteResult, Train, WSEvent } from '../types';
import { fetchStationGraph, createSession } from '../services/api';
import { StationWebSocketClient } from '../services/websocket';

interface NavigationContextType {
  activeScreen: 'welcome' | 'chat' | 'navigation' | 'trains' | 'admin';
  setActiveScreen: (screen: 'welcome' | 'chat' | 'navigation' | 'trains' | 'admin') => void;
  sessionId: string;
  graph: StationGraph | null;
  activeRoute: RouteResult | null;
  setActiveRoute: (route: RouteResult | null) => void;
  currentStepIndex: number;
  setCurrentStepIndex: (idx: number) => void;
  currentLocation: string;
  setCurrentLocation: (loc: string) => void;
  currentTrain: string | null;
  setCurrentTrain: (train: string | null) => void;
  isAccessible: boolean;
  setIsAccessible: (acc: boolean) => void;
  highContrast: boolean;
  toggleHighContrast: () => void;
  liveAlert: WSEvent | null;
  setLiveAlert: (alert: WSEvent | null) => void;
}

const NavigationContext = createContext<NavigationContextType | undefined>(undefined);

export const NavigationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeScreen, setActiveScreen] = useState<'welcome' | 'chat' | 'navigation' | 'trains' | 'admin'>('chat');
  const [sessionId, setSessionId] = useState<string>('');
  const [graph, setGraph] = useState<StationGraph | null>(null);
  const [activeRoute, setActiveRoute] = useState<RouteResult | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [currentLocation, setCurrentLocation] = useState<string>('gate_1_main');
  const [currentTrain, setCurrentTrain] = useState<string | null>(null);
  const [isAccessible, setIsAccessible] = useState<boolean>(false);
  const [highContrast, setHighContrast] = useState<boolean>(false);
  const [liveAlert, setLiveAlert] = useState<WSEvent | null>(null);

  useEffect(() => {
    async function init() {
      try {
        const g = await fetchStationGraph('pune_junction');
        setGraph(g);
        const sess = await createSession({
          station_id: 'pune_junction',
          current_node_id: currentLocation,
          accessibility_prefs: isAccessible
        });
        setSessionId(sess.id);
      } catch (e) {
        console.error('Initialization error:', e);
      }
    }
    init();
  }, []);

  useEffect(() => {
    if (!sessionId) return;
    const ws = new StationWebSocketClient(sessionId, (event) => {
      setLiveAlert(event);
      if (event.data && event.data.new_route) {
        setActiveRoute(event.data.new_route);
        setCurrentStepIndex(0);
      }
    });
    return () => ws.disconnect();
  }, [sessionId]);

  const toggleHighContrast = () => setHighContrast(prev => !prev);

  return (
    <NavigationContext.Provider
      value={{
        activeScreen,
        setActiveScreen,
        sessionId,
        graph,
        activeRoute,
        setActiveRoute,
        currentStepIndex,
        setCurrentStepIndex,
        currentLocation,
        setCurrentLocation,
        currentTrain,
        setCurrentTrain,
        isAccessible,
        setIsAccessible,
        highContrast,
        toggleHighContrast,
        liveAlert,
        setLiveAlert
      }}
    >
      <div className={highContrast ? 'high-contrast' : ''}>
        {children}
      </div>
    </NavigationContext.Provider>
  );
};

export const useNavigation = () => {
  const context = useContext(NavigationContext);
  if (!context) throw new Error('useNavigation must be used within NavigationProvider');
  return context;
};
