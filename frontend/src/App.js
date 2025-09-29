import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Convert from 'ansi-to-html';

// --- Helper Components ---

const Icon = ({ className }) => <i className={className}></i>;

const Card = ({ title, icon, children }) => (
  <div className="card mb-4 shadow-sm">
    <div className="card-header bg-white d-flex align-items-center">
      <Icon className={`card-header-icon ${icon}`} />
      <h5 className="mb-0">{title}</h5>
    </div>
    <div className="card-body">
      {children}
    </div>
  </div>
);

// --- Main App Component ---

function App() {
  // --- State Management ---
  const [goal, setGoal] = useState('');
  const [workflow, setWorkflow] = useState('enhanced');
  const [dataFile, setDataFile] = useState(null);

  const [status, setStatus] = useState('Idle');
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [logs, setLogs] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);

  const [result, setResult] = useState(null);
  const logViewerRef = useRef(null);
  const ws = useRef(null);
  const convert = new Convert();

  // --- Effects ---

  // Effect to scroll log viewer
  useEffect(() => {
    if (logViewerRef.current) {
      logViewerRef.current.scrollTop = logViewerRef.current.scrollHeight;
    }
  }, [logs]);

  // Effect for WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = `ws://${window.location.host}/ws`;
      console.log(`Connecting to WebSocket at ${wsUrl}`);
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setLogs(prev => [...prev, { level: 'success', message: '✓ Real-time connection established.' }]);
      };

      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'log') {
          setLogs(prev => [...prev, data]);
        } else if (data.type === 'progress') {
          setProgress(data.percentage);
          setProgressMessage(data.message);
        }
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected. Attempting to reconnect...');
        setLogs(prev => [...prev, { level: 'warning', message: '... Real-time connection lost. Retrying ...' }]);
        setTimeout(connectWebSocket, 3000);
      };

      ws.current.onerror = (err) => {
        console.error('WebSocket error:', err);
        ws.current.close();
      };
    };

    connectWebSocket();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);


  // --- Handlers ---

  const handleFileChange = (e) => {
    setDataFile(e.target.files[0]);
  };

  const handleStartResearch = async () => {
    if (isRunning) return;

    setIsRunning(true);
    setStatus('Starting...');
    setError(null);
    setResult(null);
    setLogs([]);
    setProgress(0);
    setProgressMessage('');
    let filePath = null;

    try {
      if (dataFile) {
        setStatus('Uploading data file...');
        const formData = new FormData();
        formData.append('file', dataFile);
        const uploadResponse = await axios.post('/api/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        if (uploadResponse.data.success) {
          filePath = uploadResponse.data.file_path;
          setStatus('File uploaded. Starting workflow...');
        } else {
          throw new Error('File upload failed.');
        }
      }

      setStatus('Executing workflow...');
      const requestBody = {
        workflow,
        goal,
        data_file_path: filePath,
      };

      const executeResponse = await axios.post('/api/execute', requestBody);

      if (executeResponse.data.success) {
        setStatus('Completed');
        setResult(executeResponse.data);
      } else {
        throw new Error(executeResponse.data.error || 'Workflow execution failed.');
      }

    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'An unknown error occurred.';
      setError(errorMessage);
      setStatus('Error');
      console.error('Execution failed:', errorMessage);
    } finally {
      setIsRunning(false);
      setProgress(0);
    }
  };

  // --- Render Logic ---

  return (
    <div className="container mt-4 mb-5">
      <header className="text-center mb-4">
        <h1 className="display-5">Veritas AI Researcher</h1>
        <p className="lead text-muted">Your Autonomous AI Research Team</p>
      </header>

      <main>
        <Card title="1. Configure Research" icon="bi bi-sliders">
          <form onSubmit={(e) => { e.preventDefault(); handleStartResearch(); }}>
            <div className="mb-3">
              <label htmlFor="research-goal" className="form-label fw-bold">Research Goal</label>
              <textarea
                id="research-goal"
                className="form-control"
                rows="3"
                placeholder="e.g., Analyze NVIDIA's business model evolution based on its financial reports..."
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                disabled={isRunning}
              />
            </div>
            <div className="row g-3 align-items-end">
              <div className="col-md">
                <label htmlFor="workflow-select" className="form-label fw-bold">Workflow Type</label>
                <select
                  id="workflow-select"
                  className="form-select"
                  value={workflow}
                  onChange={(e) => setWorkflow(e.target.value)}
                  disabled={isRunning}
                >
                  <option value="enhanced">Enhanced (with Review)</option>
                  <option value="simple">Simple</option>
                  <option value="domain">Domain-Adaptive</option>
                </select>
              </div>
              <div className="col-md">
                <label htmlFor="data-file" className="form-label fw-bold">Data File (Optional)</label>
                <input
                  type="file"
                  id="data-file"
                  className="form-control"
                  onChange={handleFileChange}
                  disabled={isRunning}
                />
              </div>
            </div>
            <hr className="my-4" />
            <button
              type="submit"
              className="btn btn-primary w-100 py-2"
              disabled={isRunning || !goal}
            >
              {isRunning ? (
                <>
                  <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                  <span className="ms-2">Research in Progress...</span>
                </>
              ) : (
                <><Icon className="bi bi-play-fill fs-5" /> Start Research</>
              )}
            </button>
          </form>
        </Card>

        {(isRunning || logs.length > 0 || error) && (
          <Card title="2. Live Progress" icon="bi bi-terminal">
            <div className="mb-3">
              <h6 className="mb-1">Status: <span className={`fw-normal badge bg-${status === 'Error' ? 'danger' : 'secondary'}`}>{status}</span></h6>
              {isRunning && progress > 0 && (
                <div>
                  <div className="progress" style={{ height: '20px' }}>
                    <div
                      className="progress-bar progress-bar-striped progress-bar-animated"
                      role="progressbar"
                      style={{ width: `${progress}%` }}
                      aria-valuenow={progress}
                      aria-valuemin="0"
                      aria-valuemax="100"
                    >
                      {progress}%
                    </div>
                  </div>
                  <small className="text-muted">{progressMessage}</small>
                </div>
              )}
            </div>

            {error && (
              <div className="alert alert-danger">
                <strong>Error:</strong> {error}
              </div>
            )}

            <h6>Live Logs:</h6>
            <div className="log-viewer" ref={logViewerRef}>
              {logs.map((log, index) => (
                <div key={index} className={`log-entry`}>
                  <span className="me-2">[{log.timestamp || new Date().toLocaleTimeString()}]</span>
                  <span dangerouslySetInnerHTML={{ __html: convert.toHtml(log.message) }} />
                </div>
              ))}
            </div>
          </Card>
        )}

        {result && (
          <Card title="3. Final Results" icon="bi bi-file-earmark-text">
            <div className="mb-4">
              <h5>Generated Report</h5>
              <div className="result-content">
                {result.content}
              </div>
            </div>
            {result.artifacts && result.artifacts.length > 0 && (
              <div>
                <h5>Generated Artifacts</h5>
                <ul className="list-group">
                  {result.artifacts.map((artifact, index) => (
                    <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                      {artifact}
                      <a
                        href={`/api/download/${result.metrics.session_id}/${artifact}`}
                        className="btn btn-sm btn-outline-primary"
                        download
                      >
                        <Icon className="bi bi-download" /> Download
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        )}
      </main>
    </div>
  );
}

export default App;
