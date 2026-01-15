'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  getProblemsCountByStatus,
  getIdeasCountByStatus,
  getRecentProblems,
  getRecentIdeas,
} from '@/lib/storage';
import { Problem, Idea } from '@/lib/types';

export default function Dashboard() {
  const [problemCounts, setProblemCounts] = useState<Record<string, number>>({});
  const [ideaCounts, setIdeaCounts] = useState<Record<string, number>>({});
  const [recentProblems, setRecentProblems] = useState<Problem[]>([]);
  const [recentIdeas, setRecentIdeas] = useState<Idea[]>([]);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    setProblemCounts(getProblemsCountByStatus());
    setIdeaCounts(getIdeasCountByStatus());
    setRecentProblems(getRecentProblems(5));
    setRecentIdeas(getRecentIdeas(5));
  }, []);

  if (!mounted) {
    return (
      <div className="p-8">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  const totalProblems = Object.values(problemCounts).reduce((a, b) => a + b, 0);
  const totalIdeas = Object.values(ideaCounts).reduce((a, b) => a + b, 0);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">📊 Dashboard</h1>
      <hr className="mb-6" />

      {/* Status Counts */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Problems by Status</h2>
          {Object.keys(problemCounts).length > 0 ? (
            <>
              <table className="w-full mb-4">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Status</th>
                    <th className="text-right py-2">Count</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(problemCounts).map(([status, count]) => (
                    <tr key={status} className="border-b">
                      <td className="py-2">
                        <span className={`badge badge-${status}`}>{status}</span>
                      </td>
                      <td className="text-right py-2">{count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="text-2xl font-bold text-blue-600">
                {totalProblems} Total
              </div>
            </>
          ) : (
            <p className="text-gray-500">No problems recorded yet.</p>
          )}
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Ideas by Status</h2>
          {Object.keys(ideaCounts).length > 0 ? (
            <>
              <table className="w-full mb-4">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Status</th>
                    <th className="text-right py-2">Count</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(ideaCounts).map(([status, count]) => (
                    <tr key={status} className="border-b">
                      <td className="py-2">
                        <span className={`badge badge-${status}`}>{status}</span>
                      </td>
                      <td className="text-right py-2">{count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="text-2xl font-bold text-green-600">
                {totalIdeas} Total
              </div>
            </>
          ) : (
            <p className="text-gray-500">No ideas recorded yet.</p>
          )}
        </div>
      </div>

      <hr className="my-8" />

      {/* Recent Items */}
      <div className="grid grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Recently Added Problems</h2>
          {recentProblems.length > 0 ? (
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Title</th>
                  <th className="text-left py-2">Status</th>
                  <th className="text-right py-2">Severity</th>
                </tr>
              </thead>
              <tbody>
                {recentProblems.map((p) => (
                  <tr key={p.id} className="border-b">
                    <td className="py-2">
                      <Link
                        href={`/problems?id=${p.id}`}
                        className="text-blue-600 hover:underline"
                      >
                        {p.title}
                      </Link>
                    </td>
                    <td className="py-2">
                      <span className={`badge badge-${p.status}`}>{p.status}</span>
                    </td>
                    <td className="text-right py-2">{p.severity}/5</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-gray-500">
              No problems recorded yet.{' '}
              <Link href="/problems" className="text-blue-600 hover:underline">
                Add one!
              </Link>
            </p>
          )}
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Recently Added Ideas</h2>
          {recentIdeas.length > 0 ? (
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Title</th>
                  <th className="text-left py-2">Status</th>
                  <th className="text-right py-2">Score</th>
                </tr>
              </thead>
              <tbody>
                {recentIdeas.map((i) => (
                  <tr key={i.id} className="border-b">
                    <td className="py-2">
                      <Link
                        href={`/ideas?id=${i.id}`}
                        className="text-blue-600 hover:underline"
                      >
                        {i.title}
                      </Link>
                    </td>
                    <td className="py-2">
                      <span className={`badge badge-${i.status}`}>{i.status}</span>
                    </td>
                    <td className="text-right py-2">
                      {i.score !== null ? i.score : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-gray-500">
              No ideas recorded yet.{' '}
              <Link href="/ideas" className="text-blue-600 hover:underline">
                Add one!
              </Link>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
