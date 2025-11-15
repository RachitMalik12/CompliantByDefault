import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { getReport } from '@/lib/api';

interface ScanProgressProps {
  jobId: string;
}

export default function ScanProgress({ jobId }: ScanProgressProps) {
  const router = useRouter();
  const [status, setStatus] = useState('Initializing scan...');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    let timeoutId: NodeJS.Timeout;
    let attempt = 0;
    const maxAttempts = 60; // 2 minutes max (polling every 2 seconds)

    const checkStatus = async () => {
      try {
        attempt++;
        setProgress(Math.min((attempt / maxAttempts) * 100, 95));

        const report = await getReport(jobId);
        
        if (report && report.id) {
          // Report is ready
          setStatus('Scan complete! Redirecting...');
          setProgress(100);
          
          clearInterval(intervalId);
          clearTimeout(timeoutId);
          
          // Redirect to report page
          setTimeout(() => {
            router.push(`/report/${jobId}`);
          }, 1000);
        } else {
          // Still processing
          const messages = [
            'Cloning repository...',
            'Running secret scanner...',
            'Analyzing code patterns...',
            'Checking dependencies...',
            'Scanning infrastructure...',
            'Running AI analysis...',
            'Calculating scores...',
            'Generating report...',
          ];
          
          const messageIndex = Math.floor(attempt / 5) % messages.length;
          setStatus(messages[messageIndex]);
        }
      } catch (err: any) {
        // 404 means report not ready yet, continue polling
        if (err.response?.status === 404) {
          if (attempt >= maxAttempts) {
            setError('Scan is taking longer than expected. Please check back later.');
            clearInterval(intervalId);
          }
        } else {
          // Actual error
          setError(err.message || 'An error occurred during scanning');
          clearInterval(intervalId);
          clearTimeout(timeoutId);
        }
      }
    };

    // Start polling
    intervalId = setInterval(checkStatus, 2000);
    
    // Set timeout
    timeoutId = setTimeout(() => {
      clearInterval(intervalId);
      setError('Scan timed out. Please try again.');
    }, 120000); // 2 minutes

    // Initial check
    checkStatus();

    return () => {
      clearInterval(intervalId);
      clearTimeout(timeoutId);
    };
  }, [jobId, router]);

  if (error) {
    return (
      <div className="bg-white shadow-lg rounded-lg p-6">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => router.push('/scan')}
            className="bg-primary-600 text-white px-6 py-2 rounded-md hover:bg-primary-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-lg rounded-lg p-6">
      <div className="text-center">
        <div className="mb-6">
          <div className="inline-block">
            <svg
              className="animate-spin h-16 w-16 text-primary-600"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          </div>
        </div>

        <h2 className="text-2xl font-bold text-gray-800 mb-2">Scanning Repository</h2>
        <p className="text-gray-600 mb-4">{status}</p>

        <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
          <div
            className="bg-primary-600 h-2.5 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          ></div>
        </div>

        <p className="text-sm text-gray-500">Job ID: {jobId}</p>
        <p className="text-xs text-gray-400 mt-2">
          This may take a few minutes depending on repository size
        </p>
      </div>
    </div>
  );
}
