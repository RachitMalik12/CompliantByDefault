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
                <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" title={finding.file}>
                  {finding.file.split('/').pop()}
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
