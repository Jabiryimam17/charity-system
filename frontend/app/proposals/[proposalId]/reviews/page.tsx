'use client';

import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { getAccessToken } from '@/lib/auth';

type RoleScore = {
  role: string | number;
  avg_weighted_score: string | number;
  review_count: number;
};

type ProposalReviewInfo = {
  proposal_id: number;
  proposal_level: string;
  questions_criteria: string[];
  role_scores: RoleScore[];
};

type ProposalComment = {
  id: number;
  proposal: number;
  user_id: number;
  comment: string;
  likes: number;
  dislikes: number;
  user_score: number;
  created_at: string;
};

export default function SubmitReviewPage() {
  const params = useParams<{ proposalId: string }>();
  const proposalId = params?.proposalId;

  const [info, setInfo] = useState<ProposalReviewInfo | null>(null);
  const [scores, setScores] = useState<number[]>([]);
  const [role, setRole] = useState('');
  const [outcome, setOutcome] = useState('support');
  const [justification, setJustification] = useState('');
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [comments, setComments] = useState<ProposalComment[]>([]);
  const [commentText, setCommentText] = useState('');
  const [commentLoading, setCommentLoading] = useState(false);

  useEffect(() => {
    if (!proposalId) {
      return;
    }

    const run = async () => {
      setFetching(true);
      setError('');
      try {
        const token = getAccessToken();
        const res = await fetch(`http://localhost:8000/proposals/${proposalId}/reviews/`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data?.message || 'Failed to load proposal review data');
        }
        setInfo(data as ProposalReviewInfo);
        setScores(new Array((data?.questions_criteria || []).length).fill(1));
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Unexpected error');
      } finally {
        setFetching(false);
      }
    };

    run();
  }, [proposalId]);

  useEffect(() => {
    if (!proposalId) {
      return;
    }

    const run = async () => {
      try {
        const token = getAccessToken();
        const res = await fetch(`http://localhost:8000/proposals/${proposalId}/comments/`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data?.message || 'Failed to load comments');
        }
        setComments((data?.results || []) as ProposalComment[]);
      } catch {
        setComments([]);
      }
    };

    run();
  }, [proposalId]);

  const canSubmit = useMemo(() => {
    return role.trim() && justification.trim() && info && scores.length === info.questions_criteria.length;
  }, [role, justification, info, scores]);

  const submitReview = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!info || !canSubmit) {
      setError('Please complete all required fields.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const token = getAccessToken();
      const res = await fetch(`http://localhost:8000/proposals/${info.proposal_id}/reviews/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          role,
          question_scores: scores,
          outcome,
          justification,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.message || 'Failed to submit review');
      }
      setSuccess('Review submitted successfully.');
      if (data?.proposal_level) {
        setInfo((prev) => (prev ? { ...prev, proposal_level: data.proposal_level } : prev));
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unexpected error');
    } finally {
      setLoading(false);
    }
  };

  const submitComment = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!proposalId || !commentText.trim()) {
      return;
    }

    setCommentLoading(true);
    setError('');
    try {
      const token = getAccessToken();
      const res = await fetch(`http://localhost:8000/proposals/${proposalId}/comments/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ comment: commentText }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.message || 'Failed to submit comment');
      }
      setComments((prev) => [data as ProposalComment, ...prev]);
      setCommentText('');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unexpected error');
    } finally {
      setCommentLoading(false);
    }
  };

  if (fetching) {
    return <main className="p-8 text-center">Loading...</main>;
  }

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-10">
      <div className="mx-auto w-full max-w-3xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:p-8">
        <h1 className="mb-4 text-2xl font-semibold text-slate-900">Submit Review</h1>

        {info && (
          <>
            <div className="mb-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
              <p><span className="font-medium">Proposal ID:</span> {info.proposal_id}</p>
              <p><span className="font-medium">Current Level:</span> {info.proposal_level}</p>
            </div>

            <div className="mb-4 rounded-xl border border-slate-200 p-4">
              <h2 className="mb-2 text-sm font-semibold text-slate-900">Scores by role</h2>
              {info.role_scores.length === 0 ? (
                <p className="text-sm text-slate-600">No role scores yet.</p>
              ) : (
                <ul className="space-y-1 text-sm text-slate-700">
                  {info.role_scores.map((roleScore, index) => (
                    <li key={`${roleScore.role}-${index}`}>
                      Role {roleScore.role}: avg {String(roleScore.avg_weighted_score)} ({roleScore.review_count} reviews)
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <form className="space-y-4" onSubmit={submitReview}>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Role</label>
                <input
                  className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  placeholder="beneficiary"
                  value={role}
                  onChange={(event) => setRole(event.target.value)}
                />
              </div>

              <div className="space-y-3">
                <h2 className="text-sm font-semibold text-slate-900">Questions</h2>
                <ol className="list-decimal space-y-2 pl-6 text-sm text-slate-800">
                  {info.questions_criteria.map((question, index) => (
                    <li key={`${index}-${question}`}>
                      <p className="mb-1">{question}</p>
                      <input
                        type="number"
                        min={1}
                        max={10}
                        className="w-24 rounded-lg border border-slate-300 px-2 py-1"
                        value={scores[index] ?? 1}
                        onChange={(event) => {
                          const value = Number(event.target.value);
                          setScores((prev) => {
                            const next = [...prev];
                            next[index] = Number.isNaN(value) ? 1 : Math.min(10, Math.max(1, value));
                            return next;
                          });
                        }}
                      />
                    </li>
                  ))}
                </ol>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Outcome</label>
                <select
                  className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  value={outcome}
                  onChange={(event) => setOutcome(event.target.value)}
                >
                  <option value="support">support</option>
                  <option value="concern">concern</option>
                  <option value="reject">reject</option>
                  <option value="escalate">escalate</option>
                </select>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">Justification</label>
                <textarea
                  className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  rows={4}
                  value={justification}
                  onChange={(event) => setJustification(event.target.value)}
                />
              </div>

              {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
              {success && <p className="rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">{success}</p>}

              <button
                type="submit"
                disabled={loading || !canSubmit}
                className="w-full rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {loading ? 'Submitting...' : 'Submit Review'}
              </button>
            </form>

            <section className="mt-8 rounded-xl border border-slate-200 p-4">
              <h2 className="mb-3 text-sm font-semibold text-slate-900">Comments</h2>

              <form className="mb-4 space-y-2" onSubmit={submitComment}>
                <textarea
                  className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  rows={3}
                  placeholder="Write your comment"
                  value={commentText}
                  onChange={(event) => setCommentText(event.target.value)}
                />
                <button
                  type="submit"
                  disabled={commentLoading || !commentText.trim()}
                  className="rounded-lg bg-slate-900 px-3 py-2 text-xs font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {commentLoading ? 'Posting...' : 'Post Comment'}
                </button>
              </form>

              {comments.length === 0 ? (
                <p className="text-sm text-slate-600">No comments yet.</p>
              ) : (
                <ul className="space-y-3">
                  {comments.map((comment) => (
                    <li key={comment.id} className="rounded-lg border border-slate-200 p-3 text-sm text-slate-700">
                      <p className="mb-2 text-xs text-slate-500">
                        User #{comment.user_id} • Score: {comment.user_score}
                      </p>
                      <p className="mb-2 whitespace-pre-wrap">{comment.comment}</p>
                      <p className="text-xs text-slate-500">Likes: {comment.likes} • Dislikes: {comment.dislikes}</p>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </>
        )}
      </div>
    </main>
  );
}
