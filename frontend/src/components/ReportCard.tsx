import type { ScoreData } from '@/types';

interface ReportCardProps {
  score: ScoreData;
  summary: {
    total_findings: number;
    readiness_score: number;
    grade: string;
    risk_level: string;
  };
}

export default function ReportCard({ score, summary }: ReportCardProps) {
  const getScoreColor = (scoreValue: number) => {
    if (scoreValue >= 90) return 'text-green-600';
    if (scoreValue >= 80) return 'text-blue-600';
    if (scoreValue >= 70) return 'text-yellow-600';
    if (scoreValue >= 60) return 'text-orange-600';
    return 'text-red-600';
  };

  const getGradeBg = (grade: string) => {
    if (grade === 'A') return 'bg-green-100 text-green-800';
    if (grade === 'B') return 'bg-blue-100 text-blue-800';
    if (grade === 'C') return 'bg-yellow-100 text-yellow-800';
    if (grade === 'D') return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  const severityCounts = score.severity_impact?.counts || {};

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Overall Score */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-sm font-medium text-gray-500 mb-2">Overall Score</h3>
        <div className={`text-4xl font-bold ${getScoreColor(summary.readiness_score)}`}>
          {summary.readiness_score}
        </div>
        <div className="mt-2">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getGradeBg(summary.grade)}`}>
            Grade: {summary.grade}
          </span>
        </div>
        <div className="mt-4 text-xs text-gray-500">
          Based on {score.controls_total} SOC 2 controls
        </div>
      </div>

      {/* Total Findings */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-sm font-medium text-gray-500 mb-2">Total Findings</h3>
        <div className="text-4xl font-bold text-gray-800">{summary.total_findings}</div>
        <div className="mt-4 space-y-1">
          {severityCounts.critical ? (
            <div className="flex justify-between text-sm">
              <span className="text-red-600">Critical:</span>
              <span className="font-medium">{severityCounts.critical}</span>
            </div>
          ) : null}
          {severityCounts.high ? (
            <div className="flex justify-between text-sm">
              <span className="text-orange-600">High:</span>
              <span className="font-medium">{severityCounts.high}</span>
            </div>
          ) : null}
          {severityCounts.medium ? (
            <div className="flex justify-between text-sm">
              <span className="text-yellow-600">Medium:</span>
              <span className="font-medium">{severityCounts.medium}</span>
            </div>
          ) : null}
        </div>
      </div>

      {/* Control Coverage */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-sm font-medium text-gray-500 mb-2">Controls Compliant</h3>
        <div className="text-4xl font-bold text-gray-800">
          {score.controls_compliant}/{score.controls_total}
        </div>
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full"
              style={{
                width: `${(score.controls_compliant / score.controls_total) * 100}%`,
              }}
            ></div>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            {Math.round((score.controls_compliant / score.controls_total) * 100)}% coverage
          </div>
        </div>
      </div>

      {/* Risk Level */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-sm font-medium text-gray-500 mb-2">Risk Level</h3>
        <div className="text-2xl font-bold text-gray-800 mt-2">{summary.risk_level.split(' - ')[0]}</div>
        <div className="mt-4 text-sm text-gray-600">{summary.risk_level}</div>
      </div>
    </div>
  );
}
