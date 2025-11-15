import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import ReportCard from '@/components/ReportCard';
import FindingsTable from '@/components/FindingsTable';
import { getReport } from '@/lib/api';
import type { Report } from '@/types';

export default function ReportPage() {
  const router = useRouter();
  const { id } = router.query;
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <>
      <Head>
        <title>Report {report.id} - CompliantByDefault</title>
        <meta name="description" content={`SOC 2 compliance report - Score: ${summary.readiness_score}/100`} />
      </Head>

      <Navbar />

      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <h1 className="text-4xl font-bold text-gray-900">Compliance Report</h1>
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
              <p>Repository: {report.metadata.repository}</p>
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
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${
                        rec.priority === 'critical' ? 'bg-red-100 text-red-800' :
                        rec.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {rec.priority.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">{rec.control}</span>
                    </div>
                    <h4 className="font-semibold text-gray-900">{rec.issue}</h4>
                    <p className="text-sm text-gray-600 mt-1">{rec.action}</p>
                    <p className="text-xs text-gray-400 mt-1">📁 {rec.file}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Control Coverage */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-bold mb-4">SOC 2 Control Coverage</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(controls).map(([controlId, control]) => (
                <div key={controlId} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-bold text-lg">{controlId}</h4>
                    <span className={`text-2xl ${
                      control.status === 'compliant' ? '✅' :
                      control.status === 'partial' ? '⚠️' : '❌'
                    }`}></span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{control.name}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">
                      {control.findings_count} finding(s)
                    </span>
                    <span className="font-bold text-primary-600">
                      {control.score}/100
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Findings Table */}
          <FindingsTable findings={findings} />
        </div>
      </main>
    </>
  );
}
