'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  getProblemsCountByStatus,
  getIdeasCountByStatus,
  getAllNotes,
  exportAllData,
  importAllData,
  clearAllData,
} from '@/lib/storage';

export default function Home() {
  const [stats, setStats] = useState({
    problems: 0,
    ideas: 0,
    notes: 0,
  });
  const [confirmClear, setConfirmClear] = useState('');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    loadStats();
  }, []);

  const loadStats = () => {
    const problemCounts = getProblemsCountByStatus();
    const ideaCounts = getIdeasCountByStatus();
    const notes = getAllNotes();

    setStats({
      problems: Object.values(problemCounts).reduce((a, b) => a + b, 0),
      ideas: Object.values(ideaCounts).reduce((a, b) => a + b, 0),
      notes: notes.length,
    });
  };

  const handleExport = () => {
    const data = exportAllData();
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'idea_vault_backup.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target?.result as string);
        if (importAllData(data)) {
          alert('Data imported successfully!');
          loadStats();
        } else {
          alert('Failed to import data.');
        }
      } catch {
        alert('Invalid JSON file.');
      }
    };
    reader.readAsText(file);
  };

  const handleClear = () => {
    if (confirmClear === 'DELETE') {
      clearAllData();
      setConfirmClear('');
      loadStats();
      alert('All data cleared.');
    }
  };

  if (!mounted) {
    return (
      <div className="p-8">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">🏦 Welcome to Idea Vault</h1>
      <hr className="mb-6" />

      {/* Warning Banner */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
        <div className="flex">
          <div className="flex-shrink-0">⚠️</div>
          <div className="ml-3">
            <p className="text-sm text-yellow-700">
              <strong>Local-Only Storage:</strong> Your data is stored in this
              browser&apos;s localStorage. It will not sync across devices, browsers,
              or private/incognito sessions. Use the Data Management section below
              to export backups.
            </p>
          </div>
        </div>
      </div>

      <div className="prose max-w-none mb-8">
        <h2>Your Startup Problem & Idea Tracker</h2>
        <p>
          <strong>Idea Vault</strong> helps you systematically track and manage:
        </p>
        <ul>
          <li>
            <strong>Problems</strong> - Pain points you&apos;ve observed that could be
            solved
          </li>
          <li>
            <strong>Ideas</strong> - Potential solutions and startup concepts
          </li>
          <li>
            <strong>Notes</strong> - Research, interviews, and insights
          </li>
        </ul>

        <h3>Getting Started</h3>
        <ol>
          <li>
            <Link href="/dashboard" className="text-blue-600 hover:underline">
              📊 Dashboard
            </Link>{' '}
            - View an overview of all your problems and ideas
          </li>
          <li>
            <Link href="/problems" className="text-blue-600 hover:underline">
              🔍 Problems
            </Link>{' '}
            - Add and manage problems you&apos;ve identified
          </li>
          <li>
            <Link href="/ideas" className="text-blue-600 hover:underline">
              💡 Ideas
            </Link>{' '}
            - Create and develop your solution ideas
          </li>
          <li>
            <Link href="/notes" className="text-blue-600 hover:underline">
              📝 Notes
            </Link>{' '}
            - Capture research, interviews, and insights
          </li>
        </ol>
      </div>

      {/* Quick Stats */}
      <h3 className="text-xl font-semibold mb-4">Quick Stats</h3>
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="card text-center">
          <div className="text-3xl font-bold text-blue-600">{stats.problems}</div>
          <div className="text-gray-600">Total Problems</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-green-600">{stats.ideas}</div>
          <div className="text-gray-600">Total Ideas</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-purple-600">{stats.notes}</div>
          <div className="text-gray-600">Total Notes</div>
        </div>
      </div>

      <hr className="my-8" />

      {/* Data Management */}
      <h3 className="text-xl font-semibold mb-4">Data Management</h3>
      <p className="text-gray-600 mb-4">
        Export and import your data for backups or transferring between devices.
      </p>

      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h4 className="font-semibold mb-4">Export Data</h4>
          <button onClick={handleExport} className="btn btn-primary">
            Download JSON Backup
          </button>
        </div>

        <div className="card">
          <h4 className="font-semibold mb-4">Import Data</h4>
          <input
            type="file"
            accept=".json"
            onChange={handleImport}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>
      </div>

      {/* Danger Zone */}
      <div className="card border-red-200 bg-red-50">
        <h4 className="font-semibold text-red-800 mb-4">
          Danger Zone - Clear All Data
        </h4>
        <p className="text-sm text-red-600 mb-4">
          This will permanently delete all your problems, ideas, notes, and links.
        </p>
        <div className="flex gap-4 items-center">
          <input
            type="text"
            placeholder="Type DELETE to confirm"
            value={confirmClear}
            onChange={(e) => setConfirmClear(e.target.value)}
            className="input max-w-xs"
          />
          <button
            onClick={handleClear}
            disabled={confirmClear !== 'DELETE'}
            className="btn btn-danger disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Clear All Data
          </button>
        </div>
      </div>
    </div>
  );
}
