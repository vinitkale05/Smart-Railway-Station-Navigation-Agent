import React, { useState, useRef, useEffect } from 'react';
import { useNavigation } from '../context/NavigationContext';
import { sendAgentMessage } from '../services/api';
import { QuickAction, WSEvent } from '../types';

interface MessageItem {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  quickActions?: QuickAction[];
}

export const ChatScreen: React.FC = () => {
  const { sessionId, setActiveRoute, setCurrentStepIndex, setActiveScreen, currentTrain, isAccessible, liveAlert } = useNavigation();
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: 'm1',
      sender: 'agent',
      text: "Namaste! I am your Smart Railway Station Navigation Agent at Pune Junction.\nI can locate your train platform, find accessible step-free paths, guide you to washrooms or food stalls, and answer your journey questions."
    }
  ]);
  const [activeSubTab, setActiveSubTab] = useState<'platform' | 'closures'>('platform');
  const [disruptions, setDisruptions] = useState<{ platform_changes: any[]; closures: any[] }>({
    platform_changes: [],
    closures: []
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const fetchDisruptions = async () => {
    try {
      const res = await fetch('/api/disruptions');
      const data = await res.json();
      setDisruptions(data);
    } catch (e) {
      console.error('Failed to load disruptions:', e);
    }
  };

  useEffect(() => {
    fetchDisruptions();
  }, []);

  useEffect(() => {
    if (liveAlert) {
      fetchDisruptions();
      if (liveAlert.event_type === 'platform_change') {
        setActiveSubTab('platform');
      } else if (liveAlert.event_type === 'closure_alert') {
        setActiveSubTab('closures');
      }
    }
  }, [liveAlert]);

  const handleSend = async (textToSend: string) => {
    if (!textToSend.trim() || !sessionId) return;
    const userMsg: MessageItem = { id: String(Date.now()), sender: 'user', text: textToSend };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const resp = await sendAgentMessage(sessionId, textToSend);
      setLoading(false);
      const agentMsg: MessageItem = {
        id: String(Date.now() + 1),
        sender: 'agent',
        text: resp.text,
        quickActions: resp.quick_actions
      };
      setMessages(prev => [...prev, agentMsg]);

      if (resp.route) {
        setActiveRoute(resp.route);
        setCurrentStepIndex(0);
      }
    } catch (err) {
      setLoading(false);
      setMessages(prev => [
        ...prev,
        {
          id: String(Date.now() + 1),
          sender: 'agent',
          text: "I experienced a temporary communication glitch with the station server. Please check physical platform indicators."
        }
      ]);
    }
  };

  const handleQuickAction = (action: string) => {
    if (action === 'start_navigation' || action === 'show_map') {
      setActiveScreen('navigation');
    } else if (action === 'find_washroom') {
      handleSend('Where is the nearest washroom?');
    } else if (action === 'find_water') {
      handleSend('Where can I get drinking water?');
    } else {
      handleSend(`Please help me with ${action}`);
    }
  };

  return (
    <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-5 min-h-0">
      {/* Left Column: Pure Conversational Chat (8 cols) */}
      <div className="lg:col-span-8 flex flex-col bg-white rounded-2xl shadow border border-slate-200 overflow-hidden">
        <div className="px-6 py-3 bg-slate-100 border-b border-slate-200 flex items-center justify-between text-xs text-slate-600">
          <div className="flex items-center space-x-4">
            <span><strong>Station:</strong> Pune Junction (PUNE)</span>
            {currentTrain && <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-semibold">Train {currentTrain}</span>}
            {isAccessible && <span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-semibold">♿ Step-free</span>}
          </div>
          <div className="flex items-center space-x-2 text-emerald-700">
            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
            <span>Live Dispatch Connected</span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4">
          {messages.map(m => (
            <div key={m.id} className={`flex items-start space-x-3 ${m.sender === 'user' ? 'justify-end' : ''}`}>
              {m.sender === 'agent' && (
                <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold shadow flex-shrink-0">
                  🤖
                </div>
              )}
              <div className={`rounded-2xl px-4 py-3 text-sm max-w-xl shadow-sm ${m.sender === 'user' ? 'bg-blue-600 text-white rounded-tr-sm' : 'bg-slate-100 text-slate-800 rounded-tl-sm'}`}>
                <div className="whitespace-pre-line">{m.text}</div>
                {m.quickActions && m.quickActions.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {m.quickActions.map((qa, i) => (
                      <button
                        key={i}
                        onClick={() => handleQuickAction(qa.action)}
                        className="text-xs bg-white hover:bg-blue-50 border border-slate-300 text-blue-700 font-semibold px-3 py-1.5 rounded-full transition shadow-sm"
                      >
                        {qa.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold shadow flex-shrink-0">
                🤖
              </div>
              <div className="bg-slate-100 rounded-2xl rounded-tl-sm px-4 py-3 text-slate-600 text-sm flex items-center space-x-2">
                <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                <span className="text-xs ml-1">Analyzing station layout...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 bg-white border-t border-slate-200">
          <form onSubmit={(e) => { e.preventDefault(); handleSend(input); }} className="flex items-center space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything, e.g. 'Where is train 12951 and where can I find water?'"
              className="flex-1 px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm"
            />
            <button
              type="submit"
              className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-xl font-semibold shadow transition"
            >
              Send
            </button>
          </form>
        </div>
      </div>

      {/* Right Column: Station Disruption Alert Tables (4 cols) */}
      <div className="lg:col-span-4 flex flex-col bg-white rounded-2xl shadow border border-slate-200 p-4 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-2">
          <div className="flex items-center space-x-2 font-bold text-sm text-slate-800">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-600"></span>
            </span>
            <span>Station Disruptions & Alerts</span>
          </div>
          <button
            onClick={fetchDisruptions}
            title="Refresh Alert Tables"
            className="text-xs text-blue-600 hover:text-blue-800 p-1 flex items-center gap-1 font-semibold"
          >
            ↻ Refresh
          </button>
        </div>

        {/* Sub-Tabs: Platform Changes vs Lift Closures */}
        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-xl mb-3 text-xs font-semibold">
          <button
            onClick={() => setActiveSubTab('platform')}
            className={`flex-1 py-1.5 px-2 rounded-lg transition flex items-center justify-center gap-1.5 ${
              activeSubTab === 'platform' ? 'bg-white text-blue-700 shadow-sm font-bold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <span>Platform Changes</span>
            <span className="bg-blue-100 text-blue-800 text-[10px] px-1.5 py-0.2 rounded-full">
              {disruptions.platform_changes.length}
            </span>
          </button>
          <button
            onClick={() => setActiveSubTab('closures')}
            className={`flex-1 py-1.5 px-2 rounded-lg transition flex items-center justify-center gap-1.5 ${
              activeSubTab === 'closures' ? 'bg-white text-blue-700 shadow-sm font-bold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <span>Lift/Facility Closures</span>
            <span className="bg-slate-200 text-slate-700 text-[10px] px-1.5 py-0.2 rounded-full">
              {disruptions.closures.filter((c: any) => c.is_closed).length}
            </span>
          </button>
        </div>

        {/* 1. Platform Changes Table (Publish Platform Change) */}
        {activeSubTab === 'platform' && (
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="text-[11px] text-slate-500 mb-1 flex items-center justify-between">
              <span>Live Platform Shifts & Delays</span>
              <span className="text-[10px] text-emerald-600 font-bold">Auto-Replanned</span>
            </div>
            <div className="flex-1 overflow-x-auto overflow-y-auto border border-slate-200 rounded-xl">
              <table className="w-full text-left text-xs text-slate-600">
                <thead className="bg-slate-100 text-slate-800 font-semibold uppercase text-[10px] sticky top-0">
                  <tr>
                    <th className="py-2 px-2.5">Train</th>
                    <th className="py-2 px-2">New Plat</th>
                    <th className="py-2 px-2">Delay</th>
                    <th className="py-2 px-2">Reason</th>
                    <th className="py-2 px-2 text-center">Map</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-[11px]">
                  {disruptions.platform_changes.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-10 text-center text-slate-400">
                        All trains on scheduled platforms
                      </td>
                    </tr>
                  ) : (
                    disruptions.platform_changes.map((ch: any, idx: number) => (
                      <tr key={idx} className="hover:bg-blue-50/50 transition">
                        <td className="py-2.5 px-2.5 font-semibold text-slate-800">
                          <div>{ch.train_no}</div>
                          <div className="text-[9px] text-slate-400 truncate max-w-[85px]">{ch.train_name}</div>
                        </td>
                        <td className="py-2.5 px-2">
                          <span className="bg-blue-600 text-white font-bold text-[10px] px-1.5 py-0.5 rounded">
                            {(ch.current_platform || ch.platform_node_id || '').replace('platform_', 'Platform ').replace('_mid', '')}
                          </span>
                        </td>
                        <td className="py-2.5 px-2">
                          <span className="text-rose-600 font-bold">{ch.delay_minutes > 0 ? `+${ch.delay_minutes}m` : 'On Time'}</span>
                        </td>
                        <td className="py-2.5 px-2 text-[10px] text-slate-500 max-w-[90px] truncate" title={ch.reason}>
                          {ch.reason || 'Operational shift'}
                        </td>
                        <td className="py-2.5 px-2 text-center">
                          <button
                            onClick={() => {
                              handleSend(`Where is train ${ch.train_no}?`);
                              setActiveScreen('navigation');
                            }}
                            className="bg-blue-50 hover:bg-blue-600 hover:text-white text-blue-700 text-[10px] font-semibold py-1 px-1.5 rounded transition"
                          >
                            Route
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 2. Lift / Facility Closures Table (Mark Lift / Facility Closure) */}
        {activeSubTab === 'closures' && (
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="text-[11px] text-slate-500 mb-1 flex items-center justify-between">
              <span>Lifts, Escalators & Restroom Outages</span>
              <span className="text-[10px] text-amber-600 font-bold">Detours Active</span>
            </div>
            <div className="flex-1 overflow-x-auto overflow-y-auto border border-slate-200 rounded-xl">
              <table className="w-full text-left text-xs text-slate-600">
                <thead className="bg-slate-100 text-slate-800 font-semibold uppercase text-[10px] sticky top-0">
                  <tr>
                    <th className="py-2 px-2.5">Facility / Lift</th>
                    <th className="py-2 px-2">Status</th>
                    <th className="py-2 px-2">Reason</th>
                    <th className="py-2 px-2 text-center">Map</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-[11px]">
                  {disruptions.closures.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-10 text-center text-slate-400">
                        All station lifts & facilities open
                      </td>
                    </tr>
                  ) : (
                    disruptions.closures.map((c: any, idx: number) => (
                      <tr key={idx} className="hover:bg-amber-50/50 transition">
                        <td className="py-2.5 px-2.5 font-semibold text-slate-800 text-[10px]">
                          {(c.node_label || c.node_id || '').replace('_', ' ')}
                        </td>
                        <td className="py-2.5 px-2">
                          <span className={`px-1.5 py-0.5 rounded font-bold text-[9px] ${c.is_closed ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}`}>
                            {c.is_closed ? 'CLOSED' : 'OPEN'}
                          </span>
                        </td>
                        <td className="py-2.5 px-2 text-[10px] text-slate-500 max-w-[85px] truncate" title={c.reason}>
                          {c.reason || 'Routine inspection'}
                        </td>
                        <td className="py-2.5 px-2 text-center">
                          <button
                            onClick={() => setActiveScreen('navigation')}
                            className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-[10px] font-medium py-1 px-1.5 rounded transition"
                          >
                            Locate
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="pt-2.5 mt-2 border-t border-slate-200 text-[10px] text-slate-500 flex items-center justify-between">
          <span>Real-time WebSocket Dispatch</span>
          <span className="text-emerald-600 font-bold flex items-center gap-1">● Live Sync</span>
        </div>
      </div>
    </div>
  );
};
