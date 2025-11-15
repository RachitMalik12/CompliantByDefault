import Head from 'next/head';
import Link from 'next/link';
import Navbar from '@/components/Navbar';

export default function Home() {
  return (
    <>
      <Head>
        <title>CompliantByDefault - SOC 2 Readiness Agent</title>
        <meta name="description" content="AI-powered SOC 2 compliance analysis for your codebase" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <Navbar />

      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          {/* Hero Section */}
          <div className="text-center mb-16">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              🛡️ CompliantByDefault
            </h1>
            <p className="text-2xl text-gray-600 mb-4">
              AI-Powered SOC 2 Readiness Agent
            </p>
            <p className="text-lg text-gray-500 max-w-3xl mx-auto mb-8">
              Automatically scan your codebase for security vulnerabilities and SOC 2 compliance gaps.
              Get instant insights powered by Gemini AI.
            </p>
            <Link
              href="/scan"
              className="inline-block bg-primary-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary-700 transition-colors shadow-lg"
            >
              Start Scanning →
            </Link>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-4xl mb-4">🔍</div>
              <h3 className="text-xl font-bold mb-2">Comprehensive Scanning</h3>
              <p className="text-gray-600">
                Multi-layered analysis including secret detection, static code analysis, dependency scanning, and infrastructure review.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-bold mb-2">AI-Powered Analysis</h3>
              <p className="text-gray-600">
                Gemini LLM intelligently maps findings to SOC 2 controls and provides actionable recommendations.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-bold mb-2">Readiness Scoring</h3>
              <p className="text-gray-600">
                Get a compliance score (0-100) with detailed control-by-control breakdown and remediation priorities.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-4xl mb-4">📁</div>
              <h3 className="text-xl font-bold mb-2">Multiple Sources</h3>
              <p className="text-gray-600">
                Scan both local directories and GitHub repositories with ease.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-4xl mb-4">📄</div>
              <h3 className="text-xl font-bold mb-2">Rich Reports</h3>
              <p className="text-gray-600">
                Export findings as JSON or Markdown with detailed recommendations for each issue.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-bold mb-2">Fast & Efficient</h3>
              <p className="text-gray-600">
                Optimized scanning algorithms provide results in minutes, not hours.
              </p>
            </div>
          </div>

          {/* SOC 2 Controls */}
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-3xl font-bold text-center mb-8">SOC 2 Controls Covered</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="border-l-4 border-primary-500 pl-4">
                <h4 className="font-bold text-lg mb-1">CC1: Control Environment</h4>
                <p className="text-sm text-gray-600">Organizational integrity and ethics</p>
              </div>
              <div className="border-l-4 border-primary-500 pl-4">
                <h4 className="font-bold text-lg mb-1">CC2: Communication</h4>
                <p className="text-sm text-gray-600">Security information flow</p>
              </div>
              <div className="border-l-4 border-primary-500 pl-4">
                <h4 className="font-bold text-lg mb-1">CC3: Risk Assessment</h4>
                <p className="text-sm text-gray-600">Vulnerability management</p>
              </div>
              <div className="border-l-4 border-primary-500 pl-4">
                <h4 className="font-bold text-lg mb-1">CC4: Monitoring</h4>
                <p className="text-sm text-gray-600">Continuous oversight</p>
              </div>
              <div className="border-l-4 border-primary-500 pl-4">
                <h4 className="font-bold text-lg mb-1">CC5: Control Activities</h4>
                <p className="text-sm text-gray-600">Security implementation</p>
              </div>
              <div className="border-l-4 border-primary-500 pl-4">
                <h4 className="font-bold text-lg mb-1">CC6: Access Controls</h4>
                <p className="text-sm text-gray-600">Authentication & authorization</p>
              </div>
              <div className="border-l-4 border-primary-500 pl-4">
                <h4 className="font-bold text-lg mb-1">CC7: System Operations</h4>
                <p className="text-sm text-gray-600">Operational management</p>
              </div>
              <div className="border-l-4 border-primary-500 pl-4">
                <h4 className="font-bold text-lg mb-1">CC8: Change Management</h4>
                <p className="text-sm text-gray-600">Version control & reviews</p>
              </div>
              <div className="border-l-4 border-primary-500 pl-4">
                <h4 className="font-bold text-lg mb-1">CC9: Risk Mitigation</h4>
                <p className="text-sm text-gray-600">Secrets & encryption</p>
              </div>
            </div>
          </div>

          {/* CTA */}
          <div className="text-center mt-16">
            <Link
              href="/scan"
              className="inline-block bg-primary-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary-700 transition-colors shadow-lg"
            >
              Get Started Now →
            </Link>
          </div>
        </div>
      </main>
    </>
  );
}
