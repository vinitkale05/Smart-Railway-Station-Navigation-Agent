import React from 'react';
import { useNavigation } from '../context/NavigationContext';
import { StationMap } from './StationMap';
import { advanceSessionStep } from '../services/api';

export const NavigationSplitView: React.FC = () => {
  const { sessionId, activeRoute, currentStepIndex, setCurrentStepIndex, setCurrentLocation } = useNavigation();

  const handleAdvance = async () => {
    if (!sessionId || !activeRoute) return;
    try {
      const res = await advanceSessionStep(sessionId);
      setCurrentStepIndex(res.current_step_index);
      setCurrentLocation(res.current_node_id);
    } catch (e) {
      console.error(e);
    }
  };

  const steps = activeRoute?.steps || [];
  const currStep = steps[currentStepIndex];

  return (
    <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0">
      {/* Map Column */}
      <div className="lg:col-span-7 bg-white rounded-2xl shadow border border-slate-200 p-4 flex flex-col">
        <h3 className="font-bold text-slate-800 text-base mb-2">Interactive Station Map</h3>
        <StationMap />
      </div>

      {/* Turn-by-Turn Directions Column */}
      <div className="lg:col-span-5 bg-white rounded-2xl shadow border border-slate-200 p-5 flex flex-col">
        <div className="flex items-center justify-between pb-4 border-b border-slate-200">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-blue-600">Turn-by-Turn Route</span>
            <h3 className="text-lg font-bold text-slate-800">Station Navigation</h3>
          </div>
          <div className="text-right">
            <span className="text-base font-extrabold text-slate-800">{activeRoute?.total_distance_m || 0} m</span>
            <span className="block text-xs text-slate-500">~{Math.ceil((activeRoute?.total_estimated_seconds || 0) / 60)} mins</span>
          </div>
        </div>

        {/* Active Step Highlight Card (FR-06, FR-12) */}
        {currStep && (
          <div className="my-4 p-4 rounded-xl bg-blue-50 border-2 border-blue-500 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="bg-blue-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold">
                {currStep.step_number}
              </span>
              <span className="text-xs font-semibold text-blue-700">Next Step</span>
            </div>
            <p className="text-slate-800 font-medium text-sm mt-2">{currStep.instruction}</p>
            <div className="mt-3 flex items-center justify-between text-xs text-slate-600 pt-2 border-t border-blue-200">
              <span>🚶 {currStep.distance_m}m</span>
              <span>⏱️ ~{currStep.estimated_seconds} sec</span>
            </div>
          </div>
        )}

        <button
          onClick={handleAdvance}
          disabled={!activeRoute || currentStepIndex >= steps.length}
          className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold py-2.5 rounded-xl shadow mb-4 transition text-sm"
        >
          {currentStepIndex >= steps.length ? '✓ Journey Complete' : 'Mark Step as Completed'}
        </button>

        {/* Steps List */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {steps.map((st, i) => (
            <div
              key={i}
              className={`p-3 rounded-lg border text-xs flex items-start space-x-3 ${
                i === currentStepIndex
                  ? 'border-blue-500 bg-blue-50/80 font-semibold'
                  : i < currentStepIndex
                  ? 'border-emerald-200 bg-emerald-50 text-slate-400 line-through'
                  : 'border-slate-200 bg-white'
              }`}
            >
              <span className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold bg-slate-200 text-slate-700">
                {st.step_number}
              </span>
              <div className="flex-1">
                <p>{st.instruction}</p>
                <span className="text-[10px] text-slate-500">{st.distance_m}m • ~{st.estimated_seconds}s</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
