import { useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Navbar from '@/components/Navbar';
import RepoSelector from '@/components/RepoSelector';
import ScanProgress from '@/components/ScanProgress';
import { scanLocal, scanGithub } from '@/lib/api';

export default function ScanPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async (type: 'local' | 'github', value: string, token?: string) => {
    setIsLoading(true);
    setError(null);

    try {
      let response;
      
      if (type === 'local') {
        response = await scanLocal(value);
      } else {
        response = await scanGithub(value, token);
      }

      setJobId(response.job_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to start scan');
      setIsLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>Scan Repository - CompliantByDefault</title>
        <meta name="description" content="Scan your repository for SOC 2 compliance" />
      </Head>

      <Navbar />

      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8 text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Scan Repository
            </h1>
            <p className="text-lg text-gray-600">
              Analyze your code for SOC 2 compliance gaps and security vulnerabilities
            </p>
          </div>

          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">
                <strong>Error:</strong> {error}
              </p>
            </div>
          )}

          {jobId ? (
            <ScanProgress jobId={jobId} />
          ) : (
            <RepoSelector onScan={handleScan} isLoading={isLoading} />
          )}
        </div>
      </main>
    </>
  );
}
