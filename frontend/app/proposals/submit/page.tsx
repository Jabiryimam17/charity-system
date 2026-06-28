'use client';

import { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';

type SubmitResponse = {
  id: number;
  title: string;
  proposal_level: string;
  proposal_score: string | number;
  proposed_at: string;
  proposal_status: string;
  questions_criteria: string[];
};

type ProposalForm = {
  title: string;
  description: string;
  region_level: string;
  region_name: string;
  budget_estimate: string;
  beneficiaries_estimate: string;
  category: string;
  proposal_file: File | null;
};

const initialForm: ProposalForm = {
  title: '',
  description: '',
  region_level: '',
  region_name: '',
  budget_estimate: '',
  beneficiaries_estimate: '',
  category: '',
  proposal_file: null,
};

export default function SubmitProposalPage() {
  const router = useRouter();
  const [form, setForm] = useState<ProposalForm>(initialForm);
  const [invalidFields, setInvalidFields] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<SubmitResponse | null>(null);
  const [doneMessage, setDoneMessage] = useState('');

  const budgetInvalid = useMemo(() => {
    if (!form.budget_estimate.trim()) {
      return false;
    }
    return !/^\d+$/.test(form.budget_estimate.trim()) || Number(form.budget_estimate) <= 0;
  }, [form.budget_estimate]);

  const handleInput = (field: keyof ProposalForm, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setInvalidFields((prev) => {
      const next = new Set(prev);
      next.delete(field);
      return next;
    });
  };

  const getCsrfToken = () => {
    const token = document.cookie
      .split(';')
      .map((entry) => entry.trim())
      .find((entry) => entry.startsWith('csrftoken='));
    return token ? decodeURIComponent(token.split('=')[1]) : '';
  };

  const validateBeforeSubmit = () => {
    const required: Array<keyof ProposalForm> = [
      'title',
      'description',
      'region_level',
      'region_name',
      'budget_estimate',
      'beneficiaries_estimate',
      'category',
    ];
    const nextInvalid = new Set<string>();

    for (const field of required) {
      if (!String(form[field]).trim()) {
        nextInvalid.add(field);
      }
    }
    if (budgetInvalid) {
      nextInvalid.add('budget_estimate');
    }

    setInvalidFields(nextInvalid);
    return nextInvalid.size === 0;
  };

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');

    if (!validateBeforeSubmit()) {
      setError('Please fill all required fields correctly.');
      return;
    }

    setLoading(true);
    try {
      const payload = new FormData();
      payload.append('title', form.title.trim());
      payload.append('description', form.description.trim());
      payload.append('region_level', form.region_level.trim());
      payload.append('region_name', form.region_name.trim());
      payload.append('budget_estimate', form.budget_estimate.trim());
      payload.append('beneficiaries_estimate', form.beneficiaries_estimate.trim());
      payload.append('category', form.category.trim());
      if (form.proposal_file) {
        payload.append('proposal_file', form.proposal_file);
      }

      const response = await fetch('/proposals/submit/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCsrfToken(),
        },
        body: payload,
      });

      const data = await response.json();
      if (!response.ok) {
        if (response.status === 400 || response.status === 503) {
          throw new Error(data?.message || data?.detail || 'Submission failed.');
        }
        throw new Error(data?.message || 'Unexpected server error.');
      }

      setResult(data as SubmitResponse);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unexpected error happened.');
    } finally {
      setLoading(false);
    }
  };

  const handleDone = () => {
    if (!result) {
      return;
    }
    router.push(`/proposals/${result.id}/`);
    setTimeout(() => {
      setDoneMessage('Proposal submitted successfully.');
    }, 300);
  };

  const inputClass = (name: string) =>
    `w-full rounded-xl border px-3 py-2 text-sm outline-none transition ${
      invalidFields.has(name)
        ? 'border-red-500 bg-red-50 focus:border-red-500 focus:ring-2 focus:ring-red-200'
        : 'border-slate-300 bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-200'
    }`;

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-10">
      <div className="mx-auto w-full max-w-2xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:p-8">
        {!result ? (
          <>
            <h1 className="mb-6 text-2xl font-semibold text-slate-900">Submit Proposal</h1>
            <form className="space-y-4" onSubmit={submit}>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="title">Title</label>
                <input id="title" className={inputClass('title')} placeholder="Community clean water initiative" value={form.title} onChange={(e) => handleInput('title', e.target.value)} />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="description">Description</label>
                <textarea id="description" className={inputClass('description')} placeholder="Describe the project scope and expected outcomes" rows={4} value={form.description} onChange={(e) => handleInput('description', e.target.value)} />
              </div>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="region_level">Region Level</label>
                  <input id="region_level" className={inputClass('region_level')} placeholder="district" value={form.region_level} onChange={(e) => handleInput('region_level', e.target.value)} />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="region_name">Region Name</label>
                  <input id="region_name" className={inputClass('region_name')} placeholder="Khulna" value={form.region_name} onChange={(e) => handleInput('region_name', e.target.value)} />
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="budget_estimate">Budget Estimate</label>
                <input id="budget_estimate" type="number" className={inputClass('budget_estimate')} placeholder="50000" value={form.budget_estimate} onChange={(e) => handleInput('budget_estimate', e.target.value)} />
                <p className="mt-1 text-xs text-slate-500">Positive integers only.</p>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="beneficiaries_estimate">Beneficiaries Estimate</label>
                <textarea id="beneficiaries_estimate" className={inputClass('beneficiaries_estimate')} placeholder="Who benefits and approximate count" rows={3} value={form.beneficiaries_estimate} onChange={(e) => handleInput('beneficiaries_estimate', e.target.value)} />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="category">Category</label>
                <input id="category" className={inputClass('category')} placeholder="water, health, education" value={form.category} onChange={(e) => handleInput('category', e.target.value)} />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="proposal_file">Proposal File (optional)</label>
                <input id="proposal_file" type="file" className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm" onChange={(e) => setForm((prev) => ({ ...prev, proposal_file: e.target.files?.[0] || null }))} />
              </div>

              {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

              <button type="submit" disabled={loading} className="w-full rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70">
                {loading ? 'Submitting…' : 'Submit Proposal'}
              </button>
            </form>
          </>
        ) : (
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold text-slate-900">Proposal Submitted</h2>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
              <p><span className="font-medium">Title:</span> {result.title}</p>
              <p><span className="font-medium">Level:</span> {result.proposal_level}</p>
              <p><span className="font-medium">Score:</span> {result.proposal_score}</p>
              <p><span className="font-medium">Status:</span> {result.proposal_status}</p>
              <p><span className="font-medium">Proposed At:</span> {result.proposed_at}</p>
            </div>

            <p className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-700">
              These questions will be answered by reviewers, not by you.
            </p>

            <ol className="list-decimal space-y-2 pl-6 text-sm text-slate-800">
              {result.questions_criteria.map((question, index) => (
                <li key={`${index}-${question}`}>{question}</li>
              ))}
            </ol>

            <button type="button" onClick={handleDone} className="w-full rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700">
              Done
            </button>

            {doneMessage && <p className="text-center text-sm text-green-700">{doneMessage}</p>}
          </section>
        )}
      </div>
    </main>
  );
}