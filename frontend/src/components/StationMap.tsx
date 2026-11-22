import React, { useState, useRef } from 'react';
import { useNavigation } from '../context/NavigationContext';

export const StationMap: React.FC = () => {
  const { graph, activeRoute, currentLocation, setCurrentLocation } = useNavigation();
  const [scale, setScale] = useState(1.0);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const dragStart = useRef({ x: 0, y: 0 });

  if (!graph) return <div className="text-white p-4">Loading Station Layout...</div>;

  const nodeMap = new Map(graph.nodes.map(n => [n.id, n]));

  const zoomIn = () => setScale(s => Math.min(3.5, Number((s * 1.25).toFixed(2))));
  const zoomOut = () => setScale(s => Math.max(0.6, Number((s * 0.8).toFixed(2))));
  const resetZoom = () => {
    setScale(1.0);
    setPosition({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    setIsDragging(true);
    dragStart.current = { x: e.clientX - position.x, y: e.clientY - position.y };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPosition({
      x: e.clientX - dragStart.current.x,
      y: e.clientY - dragStart.current.y
    });
  };

  const handleMouseUp = () => setIsDragging(false);

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.15 : 0.87;
    setScale(s => Math.min(3.5, Math.max(0.6, Number((s * factor).toFixed(2)))));
  };

  return (
    <div
      className={`flex-1 bg-slate-900 rounded-xl overflow-hidden relative border border-slate-800 flex items-center justify-center p-2 select-none ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onWheel={handleWheel}
    >
      {/* Floating Zoom & Pan Controls */}
      <div className="absolute top-3 right-3 flex flex-col items-center bg-slate-800/90 backdrop-blur rounded-xl border border-slate-700 shadow-xl p-1.5 space-y-1.5 z-20">
        <button
          onClick={(e) => { e.stopPropagation(); zoomIn(); }}
          title="Zoom In (+)"
          className="w-8 h-8 rounded-lg bg-slate-700 hover:bg-blue-600 text-white flex items-center justify-center transition text-sm font-bold"
        >
          +
        </button>
        <span className="text-[11px] font-mono font-bold text-slate-300 px-1">
          {Math.round(scale * 100)}%
        </span>
        <button
          onClick={(e) => { e.stopPropagation(); zoomOut(); }}
          title="Zoom Out (-)"
          className="w-8 h-8 rounded-lg bg-slate-700 hover:bg-blue-600 text-white flex items-center justify-center transition text-sm font-bold"
        >
          -
        </button>
        <div className="w-full h-px bg-slate-700 my-0.5"></div>
        <button
          onClick={(e) => { e.stopPropagation(); resetZoom(); }}
          title="Reset Zoom / Fit Map"
          className="w-8 h-8 rounded-lg bg-slate-700 hover:bg-amber-600 text-white flex items-center justify-center transition text-xs"
        >
          ↺
        </button>
      </div>

      <svg viewBox="0 0 950 620" className="w-full h-full max-h-[560px]">
        <g transform={`translate(${position.x}, ${position.y}) scale(${scale})`}>
          {/* Railway Tracks */}
          {[240, 360, 480].map((y, i) => (
            <g key={i}>
              <rect x="50" y={y - 12} width="850" height="24" fill="#1e293b" rx="4" />
              <line x1="50" y1={y - 6} x2="900" y2={y - 6} stroke="#64748b" strokeWidth="2" strokeDasharray="8 6" />
              <line x1="50" y1={y + 6} x2="900" y2={y + 6} stroke="#64748b" strokeWidth="2" strokeDasharray="8 6" />
            </g>
          ))}

          {/* Platforms Background */}
          {[
            { y: 200, label: 'PLATFORM 1' },
            { y: 280, label: 'PLATFORM 2' },
            { y: 320, label: 'PLATFORM 3' },
            { y: 400, label: 'PLATFORM 4' },
            { y: 440, label: 'PLATFORM 5' },
            { y: 520, label: 'PLATFORM 6' }
          ].map((p, idx) => (
            <g key={idx}>
              <rect x="80" y={p.y - 14} width="780" height="28" fill="#1e3a5f" opacity="0.6" rx="4" />
              <text x="880" y={p.y + 4} fill="#38bdf8" fontSize="11" fontWeight="bold" textAnchor="end">{p.label}</text>
            </g>
          ))}

          {/* Edges */}
          {graph.edges.map(e => {
            const u = nodeMap.get(e.from_node);
            const v = nodeMap.get(e.to_node);
            if (!u || !v) return null;
            let stroke = '#334155';
            let dash = 'none';
            if (e.has_lift) stroke = '#f59e0b';
            else if (e.has_stairs) dash = '4 4';
            return (
              <line
                key={e.id}
                x1={u.x}
                y1={u.y}
                x2={v.x}
                y2={v.y}
                stroke={stroke}
                strokeWidth="2.5"
                strokeDasharray={dash}
                opacity="0.7"
              />
            );
          })}

          {/* Active Route Polyline */}
          {activeRoute && activeRoute.nodes && activeRoute.nodes.length > 1 && (
            <g>
              <polyline
                points={activeRoute.nodes
                  .map(id => nodeMap.get(id))
                  .filter(Boolean)
                  .map(n => `${n!.x},${n!.y}`)
                  .join(' ')}
                fill="none"
                stroke="#38bdf8"
                strokeWidth="6"
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity="0.9"
              />
              <polyline
                points={activeRoute.nodes
                  .map(id => nodeMap.get(id))
                  .filter(Boolean)
                  .map(n => `${n!.x},${n!.y}`)
                  .join(' ')}
                fill="none"
                stroke="#ffffff"
                strokeWidth="2"
                strokeLinecap="round"
                strokeDasharray="6 6"
              />
            </g>
          )}

          {/* Nodes */}
          {graph.nodes.map(n => {
            if (n.is_restricted) return null;
            let fill = '#94a3b8';
            let r = 5;
            if (n.type === 'gate') { fill = '#10b981'; r = 7; }
            else if (n.type === 'platform') { fill = '#3b82f6'; r = 6; }
            else if (n.type === 'lift') { fill = '#f59e0b'; r = 6; }
            else if (n.type === 'stairs') { fill = '#ef4444'; r = 5; }
            else if (n.type === 'washroom') { fill = '#06b6d4'; r = 6; }
            else if (n.type === 'food') { fill = '#8b5cf6'; r = 6; }

            return (
              <g
                key={n.id}
                onClick={(e) => { e.stopPropagation(); setCurrentLocation(n.id); }}
                className="cursor-pointer"
              >
                <circle cx={n.x} cy={n.y} r={r} fill={fill} stroke="#ffffff" strokeWidth="1.5" />
                <text x={n.x} y={n.y - 8} fill="#e2e8f0" fontSize="9" textAnchor="middle" pointerEvents="none">
                  {n.label.split('(')[0]}
                </text>
              </g>
            );
          })}

          {/* Current Location Pin */}
          {nodeMap.get(currentLocation) && (
            <g>
              <circle cx={nodeMap.get(currentLocation)!.x} cy={nodeMap.get(currentLocation)!.y} r="14" fill="#f43f5e" opacity="0.4" />
              <circle cx={nodeMap.get(currentLocation)!.x} cy={nodeMap.get(currentLocation)!.y} r="6" fill="#f43f5e" stroke="#ffffff" strokeWidth="2" />
            </g>
          )}

          {/* Destination Pin */}
          {activeRoute && activeRoute.to_node && nodeMap.get(activeRoute.to_node) && (
            <g>
              <circle cx={nodeMap.get(activeRoute.to_node)!.x} cy={nodeMap.get(activeRoute.to_node)!.y} r="9" fill="#10b981" stroke="#ffffff" strokeWidth="2" />
              <text x={nodeMap.get(activeRoute.to_node)!.x} y={nodeMap.get(activeRoute.to_node)!.y + 4} fill="#ffffff" fontSize="9" fontWeight="bold" textAnchor="middle">★</text>
            </g>
          )}
        </g>
      </svg>
    </div>
  );
};
