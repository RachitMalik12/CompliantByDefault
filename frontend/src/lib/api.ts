const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Finding {
  id: string;
  scanner: string;
  severity: string;
  category: string;
  title: string;
  description: string;
  file_path: string;
  line_number?: number;
  recommendation: string;
  control_mapping: string[];
}

export interface Scoring {
  overall_score: number;
  category_scores: {
    [key: string]: number;
  };
  control_coverage: {
    [key: string]: number;
  };
}

export interface Analysis {
  posture?: string;
  critical_risks?: string[];
  compliance_gaps?: string[];
  top_actions?: string[];
  long_term_improvements?: string[];
  error?: string;
}

export interface Report {
  id: string;
  generated_at: string;
  metadata: {
    job_id: string;
    scan_type: string;
    path: string;
    repository: string;
    timestamp: string;
    scanner_versions: {
      [key: string]: string;
    };
  };
  findings: Finding[];
  analysis: Analysis;
  scoring: Scoring;
  summary: {
    total_findings: number;
    by_severity?: {
      [key: string]: number;
    };
    by_category?: {
      [key: string]: number;
    };
    readiness_score?: number;
    grade?: string;
    risk_level?: string;
  };
  score?: any;
  controls?: any;
  recommendations?: any[];
  report_files?: {
    json: string;
    markdown: string;
  };
}

export interface ReportSummary {
  id: string;
  generated_at: string;
  score?: number;
  findings?: number;
  repository: string;
}

export interface ScanRequest {
  path?: string;
  repo_url?: string;
  token?: string;
}

export interface ScanResponse {
  job_id: string;
  status: string;
  message: string;
}

export async function scanLocal(path: string): Promise<ScanResponse> {
  const response = await fetch(`${API_BASE_URL}/scan/local`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ path }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to start scan');
  }

  return response.json();
}

export async function scanGithub(repo_url: string, token?: string): Promise<ScanResponse> {
  const response = await fetch(`${API_BASE_URL}/scan/github`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ repo_url, token }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to start scan');
  }

  return response.json();
}

export async function getReport(jobId: string): Promise<Report> {
  const response = await fetch(`${API_BASE_URL}/report/${jobId}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Report not found');
    }
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get report');
  }

  return response.json();
}

export async function listReports(): Promise<ReportSummary[]> {
  const response = await fetch(`${API_BASE_URL}/reports`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to list reports');
  }

  return response.json();
}

export async function getControls(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/controls`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get controls');
  }

  return response.json();
}

export async function healthCheck(): Promise<{ status: string; gemini_configured: boolean }> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error('Health check failed');
  }

  return response.json();
}

export async function downloadPDF(jobId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/report/${jobId}/pdf`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Report not found');
    }
    const error = await response.json();
    throw new Error(error.detail || 'Failed to download PDF');
  }

  // Create blob from response
  const blob = await response.blob();
  
  // Create download link
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `compliance_report_${jobId}.pdf`;
  document.body.appendChild(link);
  link.click();
  
  // Cleanup
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
