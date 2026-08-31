import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { Activity, Cpu, Database, RefreshCw, CheckCircle } from 'lucide-react';
import client from '../api/client';

export default function ModelPerformance() {
  const [modelMetrics, setModelMetrics] = useState<any[]>([]);
  const [radarData, setRadarData] = useState<any[]>([]);
  
  const [isRetraining, setIsRetraining] = useState(false);
  const [retrainSuccess, setRetrainSuccess] = useState(false);

  const fetchMetrics = async () => {
    try {
      const res = await client.get('/api/v1/models/metrics');
      const data = res.data;
      
      if (data && data.length > 0) {
        const formattedMetrics = data.map((m: any) => ({
          name: m.name,
          precision: m.precision,
          recall: m.recall,
          f1: m.f1,
          auc: m.auc
        }));
        setModelMetrics(formattedMetrics);
        
        // Map to radar structure
        const getMetric = (name: string, metric: string) => {
          const m = data.find((d: any) => d.name === name);
          return m ? Math.round(m[metric] * 100) : 0;
        };
        
        setRadarData([
          { subject: 'Precision', XGBoost: getMetric('XGBoost', 'precision'), RandomForest: getMetric('Random Forest', 'precision'), Logistic: getMetric('Logistic Regression', 'precision'), fullMark: 100 },
          { subject: 'Recall', XGBoost: getMetric('XGBoost', 'recall'), RandomForest: getMetric('Random Forest', 'recall'), Logistic: getMetric('Logistic Regression', 'recall'), fullMark: 100 },
          { subject: 'F1 Score', XGBoost: getMetric('XGBoost', 'f1'), RandomForest: getMetric('Random Forest', 'f1'), Logistic: getMetric('Logistic Regression', 'f1'), fullMark: 100 },
          { subject: 'ROC-AUC', XGBoost: getMetric('XGBoost', 'auc'), RandomForest: getMetric('Random Forest', 'auc'), Logistic: getMetric('Logistic Regression', 'auc'), fullMark: 100 },
        ]);
      }
    } catch (err) {
      console.error("Failed to fetch model metrics", err);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const handleRetrain = async () => {
    setIsRetraining(true);
    setRetrainSuccess(false);
    try {
      await client.post('/api/v1/models/retrain');
      setRetrainSuccess(true);
      setTimeout(fetchMetrics, 5000);
      setTimeout(() => setRetrainSuccess(false), 5000);
    } catch (err) {
      console.error("Failed to trigger retraining", err);
    } finally {
      setIsRetraining(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between gap-4 items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Model Performance</h1>
          <p className="text-gray-500 mt-1">Evaluate and compare Machine Learning model metrics.</p>
        </div>
        <div className="flex items-center gap-3">
          {retrainSuccess && (
            <span className="text-emerald-600 text-sm font-medium flex items-center gap-1 bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-100">
              <CheckCircle size={16} /> Job Queued
            </span>
          )}
          <button 
            onClick={handleRetrain}
            disabled={isRetraining}
            className="btn-primary flex items-center gap-2"
          >
            <RefreshCw size={18} className={isRetraining ? "animate-spin" : ""} />
            {isRetraining ? "Triggering..." : "Retrain Model"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card-glass p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-indigo-500/10 text-indigo-600">
              <Cpu size={24} />
            </div>
            <div>
              <h3 className="text-gray-900 font-bold">Active Model</h3>
              <p className="text-sm text-gray-500">XGBoost (Production)</p>
            </div>
          </div>
        </div>
        
        <div className="card-glass p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-emerald-500/10 text-emerald-600">
              <Activity size={24} />
            </div>
            <div>
              <h3 className="text-gray-900 font-bold">Inference Time</h3>
              <p className="text-sm text-gray-500">42ms average</p>
            </div>
          </div>
        </div>

        <div className="card-glass p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-purple-500/10 text-purple-600">
              <Database size={24} />
            </div>
            <div>
              <h3 className="text-gray-900 font-bold">Training Data</h3>
              <p className="text-sm text-gray-500">1.2M Synthetic Transactions</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-glass p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-6">Algorithm Comparison (Metrics)</h2>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={modelMetrics} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                <XAxis dataKey="name" tick={{fill: '#6b7280'}} axisLine={false} tickLine={false} />
                <YAxis tick={{fill: '#6b7280'}} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                <Legend />
                <Bar dataKey="f1" name="F1 Score" fill="#5E3BEE" radius={[4, 4, 0, 0]} />
                <Bar dataKey="auc" name="ROC-AUC" fill="#0B1120" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card-glass p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-6">Multi-Dimensional Analysis</h2>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid stroke="#e5e7eb" />
                <PolarAngleAxis dataKey="subject" tick={{fill: '#6b7280'}} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar name="XGBoost" dataKey="XGBoost" stroke="#5E3BEE" fill="#5E3BEE" fillOpacity={0.6} />
                <Radar name="Random Forest" dataKey="RandomForest" stroke="#0B1120" fill="#0B1120" fillOpacity={0.3} />
                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
