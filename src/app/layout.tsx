import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

export const metadata: Metadata = {
  title: 'Idea Vault',
  description: 'Track startup problems and ideas - Local storage only',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen flex">
          {/* Sidebar */}
          <aside className="w-64 bg-gray-800 text-white flex-shrink-0">
            <div className="p-6">
              <h1 className="text-xl font-bold flex items-center gap-2">
                <span>🏦</span> Idea Vault
              </h1>
              <p className="text-gray-400 text-sm mt-1">
                Track problems & ideas
              </p>
            </div>

            <nav className="mt-6">
              <Link
                href="/"
                className="flex items-center gap-3 px-6 py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
              >
                <span>🏠</span> Home
              </Link>
              <Link
                href="/dashboard"
                className="flex items-center gap-3 px-6 py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
              >
                <span>📊</span> Dashboard
              </Link>
              <Link
                href="/problems"
                className="flex items-center gap-3 px-6 py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
              >
                <span>🔍</span> Problems
              </Link>
              <Link
                href="/ideas"
                className="flex items-center gap-3 px-6 py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
              >
                <span>💡</span> Ideas
              </Link>
              <Link
                href="/notes"
                className="flex items-center gap-3 px-6 py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
              >
                <span>📝</span> Notes
              </Link>
            </nav>

            <div className="mt-8 mx-4 p-4 bg-gray-700 rounded-lg">
              <p className="text-sm text-gray-300">
                <strong className="text-yellow-400">Local Storage Only</strong>
                <br />
                <span className="text-xs">
                  Data saved in this browser only. No cross-device sync.
                </span>
              </p>
            </div>
          </aside>

          {/* Main content */}
          <main className="flex-1 overflow-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
