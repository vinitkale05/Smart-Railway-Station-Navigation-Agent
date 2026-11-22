import { Station, StationGraph, Train, MessageResponse, RouteResult } from '../types';

const BASE_URL = '/api';

export async function fetchStations(): Promise<Station[]> {
  const res = await fetch(`${BASE_URL}/stations`);
  return res.json();
}

export async function fetchStationGraph(stationId: string = 'pune_junction'): Promise<StationGraph> {
  const res = await fetch(`${BASE_URL}/stations/${stationId}/graph`);
  return res.json();
}

export async function fetchTrains(): Promise<Train[]> {
  const res = await fetch(`${BASE_URL}/trains`);
  return res.json();
}

export async function fetchTrainInfo(trainNo: string): Promise<Train> {
  const res = await fetch(`${BASE_URL}/trains/${trainNo}`);
  return res.json();
}

export async function createSession(data: {
  station_id?: string;
  train_no?: string;
  accessibility_prefs?: boolean;
  current_node_id?: string;
}): Promise<{ id: string }> {
  const res = await fetch(`${BASE_URL}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function sendAgentMessage(sessionId: string, message: string): Promise<MessageResponse> {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  return res.json();
}

export async function advanceSessionStep(sessionId: string): Promise<{
  current_step_index: number;
  current_node_id: string;
  completed: boolean;
  total_steps: number;
}> {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}/step`, {
    method: 'POST'
  });
  return res.json();
}

export async function adminLogin(username: string, password: string): Promise<{ access_token: string }> {
  const res = await fetch(`${BASE_URL}/admin/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return res.json();
}

export async function publishPlatformChange(token: string, payload: {
  train_no: string;
  new_platform: string;
  delay_minutes: number;
  reason: string;
}) {
  const res = await fetch(`${BASE_URL}/admin/platform-changes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function publishClosure(token: string, payload: {
  node_id: string;
  is_closed: boolean;
  reason: string;
}) {
  const res = await fetch(`${BASE_URL}/admin/closures`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });
  return res.json();
}
