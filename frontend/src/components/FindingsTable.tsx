import { useState, useMemo } from 'react';
import type { Finding } from '@/types';

interface FindingsTableProps {
  findings: Finding[];
}

export default function FindingsTable({ findings }: FindingsTableProps) {
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [controlFilter, setControlFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'severity' | 'file' | 'control'>('severity');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  // Get unique controls
  const controls = useMemo(() => {
    const uniqueControls = new Set(findings.map((f) => f.control));
    return Array.from(uniqueControls).sort();
  }, [findings]);

  // Filter and sort findings
  const filteredAndSortedFindings = useMemo(() => {
    let filtered = findings;

    if (severityFilter !== 'all') {
      filtered = filtered.filter((f) => f.severity === severityFilter);
    }

    if (controlFilter !== 'all') {
      filtered = filtered.filter((f) => f.control === controlFilter);
    }

    // Sort
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
    return filtered.sort((a, b) => {
      if (sortBy === 'severity') {
        return severityOrder[a.severity] - severityOrder[b.severity];
      } else if (sortBy === 'file') {
        return a.file.localeCompare(b.file);
      } else {
        return a.control.localeCompare(b.control);
      }
    });
  }, [findings, severityFilter, controlFilter, sortBy]);

  // Pagination
  const totalPages = Math.ceil(filteredAndSortedFindings.length / itemsPerPage);
  const paginatedFindings = filteredAndSortedFindings.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const getSeverityBadge = (severity: string) => {
    const colors = {
      critical: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-blue-100 text-blue-800',
      info: 'bg-gray-100 text-gray-800',
    };
    return colors[severity as keyof typeof colors] || colors.info;
  };

  const isGitHubUrl = (file: string) => {
    return file.startsWith('https://github.com/');
  };

  const getFileName = (file: string) => {
    if (isGitHubUrl(file)) {
      // Extract filename from GitHub URL
      const match = file.match(/\/blob\/[^\/]+\/(.+?)(?:#|$)/);
      return match ? match[1].split('/').pop() : file.split('/').pop();
    }
    return file.split('/').pop();
  };

  const GitHubIcon = () => (
    <svg className="w-4 h-4 inline-block mr-1" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
    </svg>
  );

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Findings</h2>
        <span className="text-sm text-gray-500">
          {filteredAndSortedFindings.length} findings
        </span>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
          <select
            value={severityFilter}
            onChange={(e) => {
              setSeverityFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="all">All</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
            <option value="info">Info</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Control</label>
          <select
            value={controlFilter}
            onChange={(e) => {
              setControlFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="all">All Controls</option>
            {controls.map((control) => (
              <option key={control} value={control}>
                {control}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'severity' | 'file' | 'control')}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="severity">Severity</option>
            <option value="file">File</option>
            <option value="control">Control</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Severity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                File
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Line
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Control
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Message
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedFindings.map((finding, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 py-1 text-xs font-semibold rounded-full ${getSeverityBadge(
                      finding.severity
                    )}`}
                  >
                    {finding.severity.toUpperCase()}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {finding.type.replace(/_/g, ' ')}
                </td>
                <td className="px-6 py-4 text-sm max-w-xs">
                  {isGitHubUrl(finding.file) ? (
                    <a
                      href={finding.file}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 hover:underline flex items-center"
                      title={finding.file}
                    >
                      <GitHubIcon />
                      <span className="truncate">{getFileName(finding.file)}</span>
                    </a>
                  ) : (
                    <span className="text-gray-500 truncate block" title={finding.file}>
                      {getFileName(finding.file)}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {finding.line}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {finding.control}
                </td>
                <td className="px-6 py-4 text-sm text-gray-700">
                  <div className="max-w-md">
                    <p className="mb-1">{finding.message}</p>
                    {finding.recommendation && (
                      <p className="text-xs text-blue-600 mt-1">
                        💡 {finding.recommendation}
                      </p>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-between items-center mt-6">
          <div className="text-sm text-gray-500">
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
