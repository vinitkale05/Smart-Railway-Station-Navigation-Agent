import { WSEvent } from '../types';

export class StationWebSocketClient {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private onEventCallback: (event: WSEvent) => void;
  private reconnectTimer: any = null;

  constructor(sessionId: string, onEvent: (event: WSEvent) => void) {
    this.sessionId = sessionId;
    this.onEventCallback = onEvent;
    this.connect();
  }

  private connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}/ws/sessions/${this.sessionId}`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('Station WebSocket connected for session:', this.sessionId);
    };

    this.ws.onmessage = (e) => {
      try {
        const data: WSEvent = JSON.parse(e.data);
        this.onEventCallback(data);
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    this.ws.onclose = () => {
      console.log('Station WebSocket disconnected. Reconnecting in 3s...');
      this.reconnectTimer = setTimeout(() => this.connect(), 3000);
    };

    this.ws.onerror = (e) => {
      console.warn('Station WebSocket error:', e);
    };
  }

  public disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
