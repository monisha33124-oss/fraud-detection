import React from 'react';
import { AlertCircle, Brain, TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';

interface FraudExplanation {
  feature_name: string;
  feature_value: number;
  shap_value: number;
}

interface Prediction {
  prediction: string;
  risk_score: number;
  risk_level: string;
  explanations: FraudExplanation[];
}

interface ExplainableAIProps {
  prediction: Prediction;
  transaction: any;
}

// Dictionary to map technical feature names to human-readable labels and descriptions
const featureDictionary: Record<string, { label: string, explanation: string }> = {
  amount: { label: "Transaction Amount", explanation: "the amount is significantly above normal" },
  customer_average_amount: { label: "Customer Average Amount", explanation: "it diverges from the customer's typical average amount" },
  amount_deviation: { label: "Amount Deviation", explanation: "the transaction value highly deviates from standard patterns" },
  transaction_frequency: { label: "Transaction Frequency", explanation: "high transaction velocity detected" },
  new_location: { label: "New Location", explanation: "an unusual or completely new location was detected" },
  location_change: { label: "Location Change", explanation: "a sudden change in location was detected" },
  new_device: { label: "New Device", explanation: "a new device was used for this transaction" },
  device_frequency: { label: "Device Frequency", explanation: "an abnormal frequency of transactions from this device" },
  time_of_day: { label: "Time of Day", explanation: "an unusual transaction time" },
  merchant_category: { label: "Merchant Category", explanation: "an atypical merchant category for this profile" }
};

export default function ExplainableAI({ prediction, transaction }: ExplainableAIProps) {
  if (!prediction) {
    return (
      <div className="bg-white p-8 rounded-xl border border-gray-200 shadow-sm flex flex-col items-center justify-center text-gray-500 min-h-[300px]">
        <Brain size={48} className="mb-4 text-gray-300" />
        <p>No Machine Learning explanations available for this transaction.</p>
      </div>
    );
  }

  // Helper to format feature names
  const getFeatureLabel = (featureName: string) => {
    return featureDictionary[featureName]?.label || featureName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Generate dynamic human explanation
  const generateExplanation = () => {
    if (!prediction.explanations || prediction.explanations.length === 0) return "No sufficient data to explain this prediction.";
    
    // Get top positive contributors (increasing risk)
    const riskDrivers = prediction.explanations
      .filter(e => e.shap_value > 0)
      .sort((a, b) => b.shap_value - a.shap_value)
      .slice(0, 3);
      
    if (riskDrivers.length === 0) return "This transaction appears legitimate based on current parameters.";

    let base = "This transaction was flagged because ";
    
    const reasons = riskDrivers.map(d => featureDictionary[d.feature_name]?.explanation || `an anomaly in ${getFeatureLabel(d.feature_name).toLowerCase()}`);
    
    if (reasons.length === 1) {
      return base + reasons[0] + ".";
    } else if (reasons.length === 2) {
      return base + reasons[0] + ", combined with " + reasons[1] + ".";
    } else {
      return base + reasons[0] + ", " + reasons[1] + ", and " + reasons[2] + ".";
    }
  };

  // Determine Impact String
  const getImpactLevel = (shapValue: number) => {
    const absVal = Math.abs(shapValue);
    if (absVal > 0.5) return "High Impact";
    if (absVal > 0.2) return "Medium Impact";
    return "Low Impact";
  };

  return (
    <div className="animate-in fade-in space-y-6">
      
      {/* Top Banner: Score & Explanation */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-1 bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-center items-center text-center">
          <h3 className="text-sm font-bold text-gray-400 mb-2 uppercase tracking-wider">AI Risk Assessment</h3>
          <div className={`text-5xl font-black mb-1 ${prediction.risk_score > 75 ? 'text-red-600' : prediction.risk_score > 40 ? 'text-orange-500' : 'text-emerald-500'}`}>
            {prediction.risk_score.toFixed(1)} <span className="text-xl text-gray-400 font-normal">/ 100</span>
          </div>
          <div className="text-sm font-bold text-gray-500 uppercase">{prediction.risk_level} RISK</div>
          <div className={`mt-3 px-4 py-1 rounded-full text-xs font-bold uppercase tracking-widest ${prediction.prediction === 'FRAUDULENT' ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'}`}>
            {prediction.prediction}
          </div>
        </div>

        <div className="col-span-1 md:col-span-2 bg-indigo-50 p-6 rounded-xl border border-indigo-100 flex flex-col justify-center">
          <h3 className="text-sm font-bold text-indigo-900 mb-3 uppercase tracking-wider flex items-center gap-2">
            <Brain size={16} /> Human-Readable Explanation
          </h3>
          <p className="text-indigo-800 text-lg leading-relaxed font-medium">
            "{generateExplanation()}"
          </p>
        </div>
      </div>

      {/* Feature Contribution Data Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-gray-100 bg-gray-50">
          <h3 className="font-bold text-gray-700 flex items-center gap-2">
            <AlertCircle size={18} className="text-gray-500" /> Feature Contribution Analysis
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-gray-500 bg-white">
                <th className="px-6 py-4 font-semibold">Feature</th>
                <th className="px-6 py-4 font-semibold">Value</th>
                <th className="px-6 py-4 font-semibold">SHAP Contribution</th>
                <th className="px-6 py-4 font-semibold">Impact</th>
                <th className="px-6 py-4 font-semibold">Direction</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {prediction.explanations?.length > 0 ? (
                [...prediction.explanations]
                  .sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value))
                  .map((expl, idx) => (
                  <tr key={idx} className="hover:bg-gray-50/50 transition-colors bg-white">
                    <td className="px-6 py-4 font-medium text-gray-900">{getFeatureLabel(expl.feature_name)}</td>
                    <td className="px-6 py-4 font-mono text-gray-600">
                      {/* Try to format currency if it's amount, otherwise standard number */}
                      {expl.feature_name.includes('amount') ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(expl.feature_value) : expl.feature_value.toFixed(2)}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`font-mono font-bold ${expl.shap_value > 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                        {expl.shap_value > 0 ? '+' : ''}{expl.shap_value.toFixed(3)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-gray-600">{getImpactLevel(expl.shap_value)}</span>
                    </td>
                    <td className="px-6 py-4">
                      {expl.shap_value > 0 ? (
                        <span className="flex items-center gap-1 text-red-600 text-xs font-semibold uppercase"><TrendingUp size={14} /> Increases Risk</span>
                      ) : (
                        <span className="flex items-center gap-1 text-emerald-600 text-xs font-semibold uppercase"><TrendingDown size={14} /> Decreases Risk</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">No feature data available.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* SHAP Waterfall Visualization */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <h3 className="font-bold text-gray-700 flex items-center gap-2 mb-6">
          <ArrowRight size={18} className="text-gray-500" /> Model Visualization (SHAP)
        </h3>
        
        {prediction.explanations?.length > 0 ? (
          <div className="space-y-4">
            <div className="flex text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              <div className="w-1/3">Feature</div>
              <div className="w-2/3 flex justify-between">
                <span>Decreases Risk</span>
                <span>Base Value</span>
                <span>Increases Risk</span>
              </div>
            </div>
            
            {[...prediction.explanations].sort((a, b) => b.shap_value - a.shap_value).map((expl, idx) => {
              // Calculate width based on max abs value to normalize the chart
              const maxAbs = Math.max(...prediction.explanations.map(e => Math.abs(e.shap_value)));
              const widthPercentage = (Math.abs(expl.shap_value) / maxAbs) * 50; // max 50% width on either side
              
              return (
                <div key={idx} className="flex items-center text-sm">
                  <div className="w-1/3 pr-4 text-gray-700 font-medium truncate" title={getFeatureLabel(expl.feature_name)}>
                    {getFeatureLabel(expl.feature_name)}
                  </div>
                  
                  <div className="w-2/3 flex items-center relative h-6 border-l border-r border-gray-100">
                    {/* Center Line */}
                    <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-300"></div>
                    
                    {/* Bar */}
                    <div className="w-full flex h-full items-center">
                      {/* Left Side (Negative) */}
                      <div className="w-1/2 flex justify-end">
                        {expl.shap_value < 0 && (
                          <div 
                            className="h-4 bg-emerald-500 rounded-l-sm" 
                            style={{ width: `${widthPercentage * 2}%` }}
                          ></div>
                        )}
                      </div>
                      
                      {/* Right Side (Positive) */}
                      <div className="w-1/2 flex justify-start">
                        {expl.shap_value > 0 && (
                          <div 
                            className="h-4 bg-red-500 rounded-r-sm" 
                            style={{ width: `${widthPercentage * 2}%` }}
                          ></div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-sm text-gray-500 p-4">No visualizations available.</div>
        )}
      </div>

    </div>
  );
}
