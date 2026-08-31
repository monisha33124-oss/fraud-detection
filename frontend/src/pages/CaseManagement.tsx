import { useState, useEffect } from 'react';
import { 
  ShieldAlert, User, AlertCircle, Clock, CheckCircle, List, Brain, 
  FileText, History, ChevronRight, MessageSquare, Briefcase 
} from 'lucide-react';
import client from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import ExplainableAI from '../components/ExplainableAI';

export default function CaseManagement() {
  const { user } = useAuth();
  const [cases, setCases] = useState<any[]>([]);
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [noteText, setNoteText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [activeTab, setActiveTab] = useState('overview');
  
  // Decision Form
  const [decision, setDecision] = useState('');
  const [resolutionReason, setResolutionReason] = useState('');
  const [showDecisionForm, setShowDecisionForm] = useState(false);

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    try {
      setIsLoading(true);
      const res = await client.get('/api/v1/investigations/?page_size=50');
      const items = res.data.items || [];
      setCases(items);
      if (items.length > 0 && !selectedCase) {
        fetchCaseDetails(items[0].case_id);
      }
    } catch (err) {
      console.error('Failed to fetch cases', err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCaseDetails = async (caseId: string) => {
    try {
      setNoteText('');
      setShowDecisionForm(false);
      setDecision('');
      setResolutionReason('');
      setActiveTab('overview');
      const res = await client.get(`/api/v1/investigations/${caseId}`);
      setSelectedCase(res.data);
    } catch (err) {
      console.error('Failed to fetch case details', err);
    }
  };

  const handleSaveNote = async () => {
    if (!noteText.trim() || !selectedCase) return;
    setIsSubmitting(true);
    try {
      await client.post(`/api/v1/investigations/${selectedCase.case_id}/notes`, { note: noteText });
      setNoteText('');
      await fetchCaseDetails(selectedCase.case_id);
    } catch (err) {
      console.error('Failed to save note', err);
      alert('Failed to save note');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitDecision = async () => {
    if (!selectedCase || !decision || !resolutionReason.trim()) return;
    setIsSubmitting(true);
    try {
      await client.post(`/api/v1/investigations/${selectedCase.case_id}/decision`, { 
        decision: decision,
        reason: resolutionReason 
      });
      // Optionally auto-close if decision is final, but let's just refresh for now
      setShowDecisionForm(false);
      await fetchCaseDetails(selectedCase.case_id);
      await fetchCases();
    } catch (err) {
      console.error('Failed to submit decision', err);
      alert('Failed to submit decision');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateStatus = async (status: string) => {
    if (!selectedCase) return;
    setIsSubmitting(true);
    try {
      await client.patch(`/api/v1/investigations/${selectedCase.case_id}`, { status });
      await fetchCaseDetails(selectedCase.case_id);
      await fetchCases();
    } catch (err) {
      console.error('Failed to update status', err);
      alert('Failed to update status');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 h-full flex flex-col">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Investigation Cases</h1>
        <p className="text-gray-500 mt-1">Review alerts, analyze AI findings, and record decisions.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-[700px]">
        {/* Cases List */}
        <div className="lg:col-span-1 space-y-4 h-[750px] overflow-y-auto pr-2 custom-scrollbar">
          <div className="sticky top-0 bg-gray-50/80 backdrop-blur-md pb-2 z-10 pt-1">
            <h2 className="text-lg font-bold text-gray-900">Active Cases</h2>
          </div>
          
          {isLoading ? (
            <div className="text-gray-500 p-4 text-center">Loading cases...</div>
          ) : cases.length === 0 ? (
            <div className="text-gray-500 p-4 text-center border border-dashed border-gray-300 rounded-xl">No active cases assigned to you.</div>
          ) : cases.map((c) => (
            <div 
              key={c.id} 
              onClick={() => fetchCaseDetails(c.case_id)}
              className={`card-glass p-4 cursor-pointer hover:shadow-md transition-all ${selectedCase?.case_id === c.case_id ? 'ring-2 ring-indigo-500 bg-indigo-50/10' : ''}`}
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-bold text-gray-900 text-sm">{c.case_id}</h3>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase ${
                    c.priority === 'CRITICAL' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'
                  }`}>
                    {c.priority}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-600 mb-2">
                <User size={12} /> Cust: {c.customer_id.substring(0,8)}...
              </div>
              <div className="flex items-center justify-between mt-3">
                <span className="text-xs font-semibold text-indigo-600 truncate mr-2">{c.status.replace(/_/g, ' ')}</span>
                <span className="text-[10px] text-gray-400 whitespace-nowrap">{new Date(c.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Case Details */}
        <div className="lg:col-span-3">
          {selectedCase ? (
            <div className="card-glass flex flex-col h-[750px]">
              {/* Header */}
              <div className="border-b border-gray-100 p-6 bg-white/50 rounded-t-2xl">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-3">
                      <h2 className="text-2xl font-bold text-gray-900">Case {selectedCase.case_id}</h2>
                      <span className="px-3 py-1 bg-gray-200 text-gray-800 rounded-full text-xs font-bold uppercase tracking-wider">
                        {selectedCase.status.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">Transaction Ref: {selectedCase.transaction?.transaction_id}</p>
                  </div>
                  
                  <div className="flex gap-2">
                    {selectedCase.status !== 'CLOSED' && (
                      <button 
                        onClick={() => setShowDecisionForm(!showDecisionForm)}
                        className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${showDecisionForm ? 'bg-gray-200 text-gray-800' : 'bg-indigo-600 text-white hover:bg-indigo-700'}`}
                      >
                        {showDecisionForm ? 'Cancel Decision' : 'Submit Decision'}
                      </button>
                    )}
                    {selectedCase.status === 'CLOSED' && (
                      <div className="px-4 py-2 bg-gray-100 border border-gray-200 text-gray-700 rounded-lg font-medium text-sm flex items-center gap-2">
                        <CheckCircle size={16} className="text-emerald-500"/> Closed ({selectedCase.decision})
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Tabs Nav */}
              <div className="flex border-b border-gray-100 px-6 mt-2">
                <button 
                  className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'overview' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('overview')}
                ><List size={16} /> Overview</button>
                <button 
                  className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'intelligence' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('intelligence')}
                ><Brain size={16} /> AI Intelligence</button>
                <button 
                  className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'notes' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('notes')}
                ><MessageSquare size={16} /> Notes ({selectedCase.notes?.length || 0})</button>
                <button 
                  className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'history' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('history')}
                ><History size={16} /> History</button>
              </div>

              {/* Content Area */}
              <div className="p-6 flex-1 overflow-y-auto custom-scrollbar bg-gray-50/30">
                
                {showDecisionForm && (
                  <div className="mb-6 p-5 border border-indigo-200 bg-indigo-50/50 rounded-xl">
                    <h3 className="font-semibold text-indigo-900 mb-4">Record Case Decision</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <button onClick={() => setDecision('CONFIRMED_FRAUD')} className={`p-3 border rounded-lg text-sm font-medium transition-all ${decision === 'CONFIRMED_FRAUD' ? 'bg-red-600 border-red-700 text-white' : 'bg-white border-gray-200 text-gray-700 hover:border-red-300'}`}>Confirmed Fraud</button>
                      <button onClick={() => setDecision('LEGITIMATE_TRANSACTION')} className={`p-3 border rounded-lg text-sm font-medium transition-all ${decision === 'LEGITIMATE_TRANSACTION' ? 'bg-emerald-600 border-emerald-700 text-white' : 'bg-white border-gray-200 text-gray-700 hover:border-emerald-300'}`}>Legitimate Transaction</button>
                      <button onClick={() => setDecision('FALSE_POSITIVE')} className={`p-3 border rounded-lg text-sm font-medium transition-all ${decision === 'FALSE_POSITIVE' ? 'bg-blue-600 border-blue-700 text-white' : 'bg-white border-gray-200 text-gray-700 hover:border-blue-300'}`}>False Positive</button>
                      <button onClick={() => setDecision('NEEDS_FURTHER_REVIEW')} className={`p-3 border rounded-lg text-sm font-medium transition-all ${decision === 'NEEDS_FURTHER_REVIEW' ? 'bg-orange-500 border-orange-600 text-white' : 'bg-white border-gray-200 text-gray-700 hover:border-orange-300'}`}>Needs Review</button>
                    </div>
                    <textarea 
                      placeholder="Reason for this decision (required)..." 
                      className="w-full p-3 border border-gray-200 rounded-lg text-sm mb-4 focus:ring-2 focus:ring-indigo-500 resize-none h-24"
                      value={resolutionReason}
                      onChange={(e) => setResolutionReason(e.target.value)}
                    />
                    <div className="flex justify-end gap-3">
                      <button onClick={() => setShowDecisionForm(false)} className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900">Cancel</button>
                      <button 
                        onClick={handleSubmitDecision} 
                        disabled={isSubmitting || !decision || !resolutionReason.trim()}
                        className="px-6 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                      >Confirm Decision</button>
                    </div>
                  </div>
                )}

                {activeTab === 'overview' && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in">
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                      <h3 className="text-sm font-bold text-gray-400 mb-4 uppercase tracking-wider flex items-center gap-2"><Briefcase size={16}/> Transaction Context</h3>
                      <div className="space-y-4 text-sm">
                        <div className="flex justify-between border-b border-gray-50 pb-2"><span className="text-gray-500">Amount</span> <span className="font-bold text-gray-900 text-lg">{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(selectedCase.transaction?.amount || 0)}</span></div>
                        <div className="flex justify-between border-b border-gray-50 pb-2"><span className="text-gray-500">Merchant</span> <span className="font-medium text-gray-900">{selectedCase.transaction?.merchant}</span></div>
                        <div className="flex justify-between border-b border-gray-50 pb-2"><span className="text-gray-500">Location</span> <span className="font-medium text-gray-900">{selectedCase.transaction?.location}</span></div>
                        <div className="flex justify-between border-b border-gray-50 pb-2"><span className="text-gray-500">Time</span> <span className="font-medium text-gray-900">{selectedCase.transaction?.date_time ? new Date(selectedCase.transaction.date_time).toLocaleString() : 'N/A'}</span></div>
                        <div className="flex justify-between"><span className="text-gray-500">Device</span> <span className="font-medium text-gray-900">{selectedCase.transaction?.device_info}</span></div>
                      </div>
                    </div>
                    
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                      <h3 className="text-sm font-bold text-gray-400 mb-4 uppercase tracking-wider flex items-center gap-2"><User size={16}/> Customer Profile</h3>
                      <div className="space-y-4 text-sm">
                        <div className="flex justify-between border-b border-gray-50 pb-2"><span className="text-gray-500">Name</span> <span className="font-medium text-indigo-600">{selectedCase.customer_name || 'N/A'}</span></div>
                        <div className="flex justify-between border-b border-gray-50 pb-2"><span className="text-gray-500">Customer ID</span> <span className="font-mono text-gray-700">{selectedCase.customer_id}</span></div>
                        <div className="flex justify-between border-b border-gray-50 pb-2"><span className="text-gray-500">Investigator</span> <span className="font-medium text-gray-900">{selectedCase.investigator_name || 'Unassigned'}</span></div>
                        
                        <div className="mt-4 pt-4 flex gap-2">
                          <button 
                            onClick={() => handleUpdateStatus('UNDER_INVESTIGATION')}
                            disabled={selectedCase.status === 'UNDER_INVESTIGATION' || selectedCase.status === 'CLOSED'}
                            className="flex-1 py-2 text-xs font-semibold bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50"
                          >Set: Under Investigation</button>
                          <button 
                            onClick={() => handleUpdateStatus('PENDING_INFORMATION')}
                            disabled={selectedCase.status === 'PENDING_INFORMATION' || selectedCase.status === 'CLOSED'}
                            className="flex-1 py-2 text-xs font-semibold bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50"
                          >Set: Pending Info</button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'intelligence' && (
                  <ExplainableAI 
                    prediction={selectedCase.transaction?.prediction} 
                    transaction={selectedCase.transaction} 
                  />
                )}

                {activeTab === 'notes' && (
                  <div className="animate-in fade-in flex flex-col h-full space-y-4">
                    <div className="flex-1 space-y-4">
                      {selectedCase.notes && selectedCase.notes.length > 0 ? (
                        selectedCase.notes.map((note: any) => (
                          <div key={note.id} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                            <div className="flex justify-between items-center mb-2 border-b border-gray-50 pb-2">
                              <span className="font-semibold text-gray-800 text-sm">Investigator</span>
                              <span className="text-xs text-gray-400">{new Date(note.created_at).toLocaleString()}</span>
                            </div>
                            <p className="text-gray-700 text-sm whitespace-pre-wrap leading-relaxed">{note.note}</p>
                          </div>
                        ))
                      ) : (
                        <div className="text-center p-8 text-gray-400 bg-white rounded-xl border border-dashed border-gray-200">No notes added yet.</div>
                      )}
                    </div>
                    
                    {selectedCase.status !== 'CLOSED' && (
                      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm mt-4">
                        <textarea 
                          className="w-full p-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none h-24 mb-3" 
                          placeholder="Record your investigation findings..."
                          value={noteText}
                          onChange={(e) => setNoteText(e.target.value)}
                          disabled={isSubmitting}
                        ></textarea>
                        <div className="flex justify-end">
                          <button 
                            onClick={handleSaveNote}
                            disabled={isSubmitting || !noteText.trim()}
                            className="px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 font-medium transition-colors disabled:opacity-50 text-sm flex items-center gap-2"
                          >
                            <FileText size={16}/> Add Note
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'history' && (
                  <div className="animate-in fade-in">
                    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                      <div className="p-4 border-b border-gray-100 bg-gray-50">
                        <h3 className="font-bold text-gray-700 text-sm">Case Audit Log</h3>
                      </div>
                      <div className="p-0">
                        {selectedCase.history && selectedCase.history.length > 0 ? (
                          <ul className="divide-y divide-gray-100">
                            {[...selectedCase.history].sort((a,b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()).map((hist: any, idx: number) => (
                              <li key={idx} className="p-4 flex gap-4 hover:bg-gray-50 transition-colors">
                                <div className="mt-1">
                                  <div className="w-2 h-2 rounded-full bg-indigo-400"></div>
                                </div>
                                <div>
                                  <p className="text-sm font-medium text-gray-900">{hist.action}</p>
                                  <p className="text-xs text-gray-500 mt-1">{new Date(hist.timestamp).toLocaleString()}</p>
                                </div>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <div className="p-8 text-center text-gray-400">No history recorded yet.</div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

              </div>
            </div>
          ) : (
            <div className="card-glass h-[750px] flex flex-col items-center justify-center text-gray-400 bg-gray-50/50">
              <ShieldAlert size={48} className="mb-4 text-gray-300" />
              <p className="text-lg font-medium">Select a case to begin investigation</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
