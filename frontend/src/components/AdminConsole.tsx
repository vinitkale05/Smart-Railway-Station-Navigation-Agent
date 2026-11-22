import React, { useState } from 'react';
import { adminLogin, publishPlatformChange, publishClosure } from '../services/api';

export const AdminConsole: React.FC = () => {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState('station_admin');
  const [password, setPassword] = useState('admin123');

  const [trainNo, setTrainNo] = useState('12951');
  const [newPlatform, setNewPlatform] = useState('Platform 3');
  const [delay, setDelay] = useState(15);
  const [reason, setReason] = useState('Track maintenance');

  const [closureNode, setClosureNode] = useState('lift_l1_p1');
  const [isClosed, setIsClosed] = useState(true);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await adminLogin(username, password);
      if (res.access_token) setToken(res.access_token);
      else alert('Invalid credentials');
    } catch {
      alert('Login failed');
    }
  };

  const handlePlatformChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    try {
      const res = await publishPlatformChange(token, {
        train_no: trainNo,
        new_platform: newPlatform,
        delay_minutes: Number(delay),
        reason
      });
      alert(`Platform update broadcasted: ${res.message}`);
    } catch {
      alert('Failed to publish');
    }
  };

  const handleClosure = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    try {
      await publishClosure(token, {
        node_id: closureNode,
        is_closed: isClosed,
        reason: 'Maintenance inspection'
      });
      alert(`Closure status updated for ${closureNode}`);
    } catch {
      alert('Failed to update closure');
    }
  };

  if (!token) {
    return (
      <div className="max-w-md mx-auto my-auto py-10 w-full bg-white rounded-2xl shadow p-6 border border-slate-200">
        <h2 className="text-xl font-bold text-slate-800 text-center mb-4">Station Admin Sign In</h2>
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
          </div>
          <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg text-sm transition">
            Sign In
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-6 bg-white rounded-2xl shadow border border-slate-200 p-6">
      <div className="bg-slate-50 border border-slate-200 p-5 rounded-xl">
        <h3 className="font-bold text-slate-800 text-sm mb-3">Broadcast Platform Change</h3>
        <form onSubmit={handlePlatformChange} className="space-y-3">
          <div>
            <label className="block text-xs font-semibold mb-1">Train Number</label>
            <input
              type="text"
              value={trainNo}
              onChange={(e) => setTrainNo(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1">New Platform</label>
            <select
              value={newPlatform}
              onChange={(e) => setNewPlatform(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white"
            >
              {['Platform 1', 'Platform 2', 'Platform 3', 'Platform 4', 'Platform 5', 'Platform 6'].map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1">Delay (mins)</label>
            <input
              type="number"
              value={delay}
              onChange={(e) => setDelay(Number(e.target.value))}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white"
            />
          </div>
          <button type="submit" className="w-full bg-rose-600 hover:bg-rose-700 text-white font-semibold py-2 rounded-lg text-sm transition">
            Broadcast Change
          </button>
        </form>
      </div>

      <div className="bg-slate-50 border border-slate-200 p-5 rounded-xl">
        <h3 className="font-bold text-slate-800 text-sm mb-3">Manage Closures (Lifts / Paths)</h3>
        <form onSubmit={handleClosure} className="space-y-3">
          <div>
            <label className="block text-xs font-semibold mb-1">Node</label>
            <select
              value={closureNode}
              onChange={(e) => setClosureNode(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white"
            >
              <option value="lift_l1_p1">Lift L1 (Platform 1)</option>
              <option value="lift_l2_p2_3">Lift L2 (Platform 2/3)</option>
              <option value="lift_l3_p4_5">Lift L3 (Platform 4/5)</option>
              <option value="lift_l4_p6">Lift L4 (Platform 6)</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1">State</label>
            <select
              value={String(isClosed)}
              onChange={(e) => setIsClosed(e.target.value === 'true')}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white"
            >
              <option value="true">Closed (Maintenance)</option>
              <option value="false">Open (Operational)</option>
            </select>
          </div>
          <button type="submit" className="w-full bg-amber-600 hover:bg-amber-700 text-white font-semibold py-2 rounded-lg text-sm transition">
            Update Closure
          </button>
        </form>
      </div>
    </div>
  );
};
