import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import ReportCard from '@/components/ReportCard';
import FindingsTable from '@/components/FindingsTable';
import { getReport, createGitHubIssue } from '@/lib/api';
import type { Report } from '@/types';

export default function ReportPage() {
  const router = useRouter();
  const { id } = router.query;
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creatingIssueForRec, setCreatingIssueForRec] = useState<number | null>(null);
  const [issuesCreatedForRec, setIssuesCreatedForRec] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (!id) return;

    const fetchReport = async () => {
      try {
        const data = await getReport(id as string);
        setReport(data);
        setLoading(false);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to load report');
        setLoading(false);
      }
    };

    fetchReport();
  }, [id]);

  const isGitHubUrl = (file: string) => {
    return file.startsWith('https://github.com/');
  };

  const getFileName = (file: string) => {
    if (isGitHubUrl(file)) {
      const match = file.match(/\/blob\/[^\/]+\/(.+?)(?:#|$)/);
      return match ? match[1] : file.split('/').pop();
    }
    return file.split('/').pop() || file;
  };

  const GitHubIcon = () => (
    <svg className="w-3 h-3 inline-block mr-1" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
    </svg>
  );

  const handleCreateIssueForRecommendation = async (rec: any, index: number) => {
    const targetRepoUrl = report?.metadata?.repository;
    
    if (!targetRepoUrl) {
      alert('Cannot create issue: No GitHub repository URL available');
      return;
    }

    setCreatingIssueForRec(index);

    try {
      // Convert recommendation to finding format
      const finding = {
        type: rec.issue || 'compliance_issue',
        severity: rec.priority || 'medium',
        file: rec.file || '',
        line: 0,
        message: rec.issue || 'Compliance issue detected',
        control: rec.control || 'SOC2',
        recommendation: rec.action || 'Please address this issue'
      };

      const result = await createGitHubIssue(targetRepoUrl, finding);
      
      if (result.success) {
        setIssuesCreatedForRec(prev => new Set([...prev, index]));
        alert(`✅ GitHub issue #${result.issue_number} created successfully!\nAssigned to: ${result.assignee}\n\nView at: ${result.issue_url}`);
        
        if (result.issue_url) {
          window.open(result.issue_url, '_blank');
        }
      } else {
        alert(`❌ Failed to create issue: ${result.message}`);
      }
    } catch (error: any) {
      alert(`❌ Error creating issue: ${error.message}`);
    } finally {
      setCreatingIssueForRec(null);
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <div className="inline-block animate-spin h-12 w-12 border-4 border-primary-600 border-t-transparent rounded-full"></div>
              <p className="mt-4 text-gray-600">Loading report...</p>
            </div>
          </div>
        </main>
      </>
    );
  }

  if (error || !report) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <div className="text-6xl mb-4">⚠️</div>
              <h2 className="text-2xl font-bold mb-4">Report Not Found</h2>
              <p className="text-gray-600 mb-6">{error || 'The requested report could not be found.'}</p>
              <Link
                href="/scan"
                className="inline-block bg-primary-600 text-white px-6 py-3 rounded-md hover:bg-primary-700"
              >
                Start New Scan
              </Link>
            </div>
          </div>
        </main>
      </>
    );
  }

  const { summary, score, controls, findings, analysis, recommendations } = report;

  // Extract repository name from URL
  const getRepoName = (repoUrl: string) => {
    try {
      const match = repoUrl.match(/github\.com\/[^\/]+\/([^\/]+?)(?:\.git)?$/);
      return match ? match[1] : 'Repository';
    } catch {
      return 'Repository';
    }
  };

  const repoName = report.metadata?.repository ? getRepoName(report.metadata.repository) : 'Repository';

  // SOC 2 control information with links
  const getControlInfo = (controlId: string) => {
    const controlLinks: { [key: string]: { url: string; description: string } } = {
      'CC1': {
        url: 'https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2',
        description: 'Control Environment - Organization demonstrates commitment to integrity and ethical values'
      },
      'CC2': {
        url: 'https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2',
        description: 'Communication and Information - Security information flow and communication'
      },
      'CC3': {
        url: 'https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2',
        description: 'Risk Assessment - Vulnerability management and risk identification'
      },
      'CC4': {
        url: 'https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2',
        description: 'Monitoring Activities - Continuous oversight and monitoring'
      },
      'CC5': {
        url: 'https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2',
        description: 'Control Activities - Security implementation and procedures'
      },
      'CC6': {
        url: 'https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2',
        description: 'Logical and Physical Access Controls - Authentication and authorization'
      },
      'CC7': {
        url: 'https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2',
        description: 'System Operations - Operational management and maintenance'
      },
      'CC8': {
        url: 'https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2',
        description: 'Change Management - Version control and change processes'
      },
      'CC9': {
        url: 'https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2',
        description: 'Risk Mitigation - Secrets management and encryption'
      }
    };
    return controlLinks[controlId] || { url: 'https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2', description: 'SOC 2 Trust Service Criteria' };
  };

  return (
    <>
      <Head>
        <title>SOC 2 Compliance Report for {repoName} - CompliantByDefault</title>
        <meta name="description" content={`SOC 2 compliance report - Score: ${summary.readiness_score}/100`} />
      </Head>

      <Navbar />

      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h1 className="text-4xl font-bold text-gray-900">SOC 2 Compliance Report</h1>
                <p className="text-lg text-gray-600 mt-1">
                  for <GitHubIcon /><span className="font-semibold">{repoName}</span>
                </p>
              </div>
              <div className="flex gap-4">
                <Link
                  href="/scan"
                  className="bg-primary-600 text-white px-6 py-2 rounded-md hover:bg-primary-700"
                >
                  New Scan
                </Link>
              </div>
            </div>
            <div className="text-sm text-gray-600">
              <p>Report ID: {report.id}</p>
              <p>Repository: <a href={report.metadata.repository} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:text-primary-800 hover:underline">{report.metadata.repository}</a></p>
              <p>Generated: {new Date(report.generated_at).toLocaleString()}</p>
            </div>
          </div>

          {/* Score Cards */}
          <div className="mb-8">
            <ReportCard score={score} summary={summary} />
          </div>

          {/* AI Analysis */}
          {analysis?.posture && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
              <h2 className="text-2xl font-bold mb-4">🤖 AI Analysis</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700">{analysis.posture}</p>
              </div>
            </div>
          )}

          {/* Recommendations */}
          {recommendations && recommendations.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
              <h2 className="text-2xl font-bold mb-4">💡 Top Recommendations</h2>
              <div className="space-y-4">
                {recommendations.slice(0, 10).map((rec, idx) => (
                  <div key={idx} className="border-l-4 border-primary-500 pl-4 py-2">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 text-xs font-semibold rounded ${
                          rec.priority === 'critical' ? 'bg-red-100 text-red-800' :
                          rec.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {rec.priority.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500">{rec.control}</span>
                      </div>
                      {report?.metadata?.repository && (
                        <button
                          onClick={() => handleCreateIssueForRecommendation(rec, idx)}
                          disabled={creatingIssueForRec === idx || issuesCreatedForRec.has(idx)}
                          className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                            issuesCreatedForRec.has(idx)
                              ? 'bg-green-100 text-green-800 cursor-not-allowed'
                              : creatingIssueForRec === idx
                              ? 'bg-gray-100 text-gray-500 cursor-wait'
                              : 'bg-primary-600 text-white hover:bg-primary-700'
                          }`}
                        >
                          {issuesCreatedForRec.has(idx) ? (
                            <>✓ Created</>
                          ) : creatingIssueForRec === idx ? (
                            <>Creating...</>
                          ) : (
                            <>Create Issue</>
                          )}
                        </button>
                      )}
                    </div>
                    <h4 className="font-semibold text-gray-900">{rec.issue}</h4>
                    <p className="text-sm text-gray-600 mt-1">{rec.action}</p>
                    {rec.file && (
                      <div className="text-xs mt-1">
                        {isGitHubUrl(rec.file) ? (
                          <a
                            href={rec.file}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 hover:underline inline-flex items-center"
                            title={rec.file}
                          >
                            <GitHubIcon />
                            <span>{getFileName(rec.file)}</span>
                          </a>
                        ) : (
                          <span className="text-gray-400" title={rec.file}>
                            📁 {getFileName(rec.file)}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Control Coverage */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-bold mb-4">SOC 2 Control Coverage</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(controls).map(([controlId, control]) => {
                const controlInfo = getControlInfo(controlId);
                return (
                  <div key={controlId} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-2">
                      <a
                        href={controlInfo.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-bold text-lg text-primary-600 hover:text-primary-800 hover:underline"
                        title={controlInfo.description}
                      >
                        {controlId} ↗
                      </a>
                      <span className={`text-2xl ${
                        control.status === 'compliant' ? '✅' :
                        control.status === 'partial' ? '⚠️' : '❌'
                      }`}></span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{control.name}</p>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-500">
                        {control.findings_count} finding(s)
                      </span>
                      <span className="font-bold text-primary-600">
                        {control.score}/100
                      </span>
                    </div>
                    <a
                      href={controlInfo.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:text-blue-800 hover:underline"
                    >
                      Learn more about {controlId}
                    </a>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Findings Table */}
          <FindingsTable findings={findings} repoUrl={report.metadata?.repository} />
        </div>
      </main>
    </>
  );
}
