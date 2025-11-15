import { useState } from 'react';

interface RepoSelectorProps {
  onScan: (type: 'local' | 'github', value: string, token?: string) => void;
  isLoading: boolean;
}

export default function RepoSelector({ onScan, isLoading }: RepoSelectorProps) {
  const [scanType, setScanType] = useState<'local' | 'github'>('github');
  const [repoUrl, setRepoUrl] = useState('');
  const [localPath, setLocalPath] = useState('');
  const [githubToken, setGithubToken] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (scanType === 'github') {
      if (!repoUrl.trim()) {
        alert('Please enter a GitHub repository URL');
        return;
      }
      onScan('github', repoUrl, githubToken || undefined);
    } else {
      if (!localPath.trim()) {
        alert('Please enter a local directory path');
        return;
      }
      onScan('local', localPath);
    }
  };

  return (
    <div className="bg-white shadow-lg rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Select Repository to Scan</h2>
      
      {/* Scan Type Selector */}
      <div className="mb-6">
        <div className="flex space-x-4">
          <button
            type="button"
            onClick={() => setScanType('github')}
            className={`flex-1 py-2 px-4 rounded-md font-medium ${
              scanType === 'github'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            GitHub Repository
          </button>
          <button
            type="button"
            onClick={() => setScanType('local')}
            className={`flex-1 py-2 px-4 rounded-md font-medium ${
              scanType === 'local'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Local Directory
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        {scanType === 'github' ? (
          <>
            <div className="mb-4">
              <label htmlFor="repoUrl" className="block text-sm font-medium text-gray-700 mb-2">
                GitHub Repository URL
              </label>
              <input
                type="text"
                id="repoUrl"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/username/repository"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                disabled={isLoading}
              />
              <p className="mt-1 text-sm text-gray-500">
                Enter the full URL of the GitHub repository
              </p>
            </div>

            <div className="mb-6">
              <label htmlFor="githubToken" className="block text-sm font-medium text-gray-700 mb-2">
                GitHub Token (Optional)
              </label>
              <input
                type="password"
                id="githubToken"
                value={githubToken}
                onChange={(e) => setGithubToken(e.target.value)}
                placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                disabled={isLoading}
              />
              <p className="mt-1 text-sm text-gray-500">
                Required for private repositories
              </p>
            </div>
          </>
        ) : (
          <div className="mb-6">
            <label htmlFor="localPath" className="block text-sm font-medium text-gray-700 mb-2">
              Local Directory Path
            </label>
            <input
              type="text"
              id="localPath"
              value={localPath}
              onChange={(e) => setLocalPath(e.target.value)}
              placeholder="/absolute/path/to/project"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              disabled={isLoading}
            />
            <p className="mt-1 text-sm text-gray-500">
              Enter the absolute path to the directory to scan
            </p>
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className={`w-full py-3 px-6 rounded-md font-medium text-white ${
            isLoading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-primary-600 hover:bg-primary-700'
          }`}
        >
          {isLoading ? 'Starting Scan...' : 'Start Scan'}
        </button>
      </form>
    </div>
  );
}
