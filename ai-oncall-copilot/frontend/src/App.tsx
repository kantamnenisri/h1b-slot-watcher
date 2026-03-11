import React, { useState } from 'react';

interface Result {
  id: string;
  title: string;
  content: string;
}

function App() {
  const [formData, setFormData] = useState({
    serviceName: '',
    alertTitle: '',
    severity: 'Medium',
    alertBody: '',
    recentDeployments: ''
  });

  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // Simulated API call - would connect to FastAPI /chat or /analyze
    setTimeout(() => {
      const newResults: Result[] = [
        {
          id: '1',
          title: 'Potential Root Cause',
          content: `Based on the alert body for ${formData.serviceName}, it appears that there is a connection timeout to the downstream database. This might be related to the recent deployment of version 1.2.4 which changed the connection pool settings.`
        },
        {
          id: '2',
          title: 'Recommended Actions',
          content: '1. Check the DB connection pool metrics.\n2. Verify if the DB credentials were changed in the latest deployment.\n3. Rollback the deployment if the error rate remains above 5%.'
        }
      ];
      setResults(newResults);
      setLoading(false);
    }, 1500);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  return (
    <div className="max-w-4xl mx-auto p-8">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-bold text-indigo-400 mb-2">AI On-Call Copilot</h1>
        <p className="text-slate-400">Intelligent assistance for troubleshooting and incident response.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Form Section */}
        <section className="bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-700">
          <h2 className="text-xl font-semibold mb-6 text-indigo-300">New Alert Analysis</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Service Name</label>
              <input
                type="text"
                name="serviceName"
                value={formData.serviceName}
                onChange={handleInputChange}
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-white"
                placeholder="e.g. checkout-service"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Alert Title</label>
              <input
                type="text"
                name="alertTitle"
                value={formData.alertTitle}
                onChange={handleInputChange}
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-white"
                placeholder="e.g. High Error Rate in v1.2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Severity</label>
              <select
                name="severity"
                value={formData.severity}
                onChange={handleInputChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-white"
              >
                <option>Critical</option>
                <option>High</option>
                <option>Medium</option>
                <option>Low</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Alert Body / Logs</label>
              <textarea
                name="alertBody"
                value={formData.alertBody}
                onChange={handleInputChange}
                rows={4}
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-white text-sm"
                placeholder="Paste the alert description or log snippet here..."
              ></textarea>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Recent Deployments</label>
              <textarea
                name="recentDeployments"
                value={formData.recentDeployments}
                onChange={handleInputChange}
                rows={3}
                className="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-white text-sm"
                placeholder="e.g. version 1.2.4 deployed 30 mins ago"
              ></textarea>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 rounded-md font-bold transition-all duration-200 ${
                loading 
                  ? 'bg-indigo-800 text-indigo-400 cursor-not-allowed' 
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white active:scale-95'
              }`}
            >
              {loading ? 'Analyzing...' : 'Analyze with AI Copilot'}
            </button>
          </form>
        </section>

        {/* Results Section */}
        <section className="space-y-6">
          <h2 className="text-xl font-semibold mb-6 text-indigo-300">AI Findings</h2>
          
          {results.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-slate-700 rounded-xl text-slate-500">
              <p>Submit the form to generate AI insights</p>
            </div>
          )}

          {loading && (
            <div className="space-y-4 animate-pulse">
              <div className="bg-slate-800 h-32 rounded-xl"></div>
              <div className="bg-slate-800 h-32 rounded-xl"></div>
            </div>
          )}

          {results.map((result) => (
            <div key={result.id} className="bg-slate-800 p-5 rounded-xl border border-slate-700 shadow-md transition-all hover:border-indigo-500/50">
              <div className="flex justify-between items-center mb-3">
                <h3 className="font-bold text-indigo-200">{result.title}</h3>
                <button 
                  onClick={() => copyToClipboard(result.content)}
                  className="text-xs bg-slate-700 hover:bg-slate-600 px-2 py-1 rounded text-slate-300 border border-slate-600 transition-colors"
                >
                  Copy
                </button>
              </div>
              <div className="text-slate-300 text-sm whitespace-pre-wrap leading-relaxed">
                {result.content}
              </div>
            </div>
          ))}
        </section>
      </div>
    </div>
  );
}

export default App;
