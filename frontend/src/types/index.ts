// Type definitions for the application

export interface ScanResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface Finding {
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  file: string;
  line: number;
  message: string;
  control: string;
  snippet?: string;
  recommendation?: string;
}

export interface ControlCoverage {
  name: string;
  description: string;
  findings_count: number;
  severity_score: number;
  status: 'compliant' | 'partial' | 'non_compliant' | 'unknown';
  score: number;
}

export interface SeverityImpact {
  counts: {
    critical?: number;
    high?: number;
    medium?: number;
    low?: number;
    info?: number;
  };
  total_weight: number;
  deduction: number;
}

export interface ScoreData {
  overall_score: number;
  grade: string;
  base_score: number;
  coverage_score: number;
  severity_impact: SeverityImpact;
  control_scores: Record<string, {
    score: number;
    status: string;
    name: string;
    findings: number;
  }>;
  total_issues: number;
  controls_compliant: number;
  controls_total: number;
}

export interface Recommendation {
  priority: 'critical' | 'high' | 'medium' | 'low';
  control: string;
  issue: string;
  action: string;
  file: string;
}

export interface LLMInsights {
  posture: string;
  critical_risks: string[];
  compliance_gaps: string[];
  top_actions: string[];
  long_term_improvements: string[];
}

export interface ReportSummary {
  total_findings: number;
  readiness_score: number;
  grade: string;
  risk_level: string;
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
  };
  summary: ReportSummary;
  score: ScoreData;
  controls: Record<string, ControlCoverage>;
  findings: Finding[];
  analysis: LLMInsights;
  recommendations: Recommendation[];
  report_files?: {
    json: string;
    markdown: string;
  };
}

export interface ReportListItem {
  id: string;
  generated_at: string;
  score: number;
  findings: number;
  repository: string;
}
