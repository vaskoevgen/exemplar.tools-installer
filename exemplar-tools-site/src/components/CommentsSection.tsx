import { useState } from 'react'
import { useQuery, useMutation } from 'convex/react'
import { api } from '../../convex/_generated/api'

interface Props {
  page: string
  accent: string
}

export default function CommentsSection({ page, accent }: Props) {
  const comments = useQuery(api.comments.getByPage, { page })
  const addComment = useMutation(api.comments.add)
  const [author, setAuthor] = useState('')
  const [body, setBody] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!author.trim() || !body.trim()) return
    setSubmitting(true)
    await addComment({ page, author: author.trim(), body: body.trim() })
    setBody('')
    setSubmitting(false)
  }

  return (
    <section className="mt-16 border-t border-[#1e1e2e] pt-10">
      <h2 className="font-display text-xl text-slate-100 mb-6">Comments</h2>
      <div className="space-y-4 mb-8">
        {comments === undefined && (
          <p className="text-slate-600 font-mono text-sm animate-pulse">Loading...</p>
        )}
        {comments?.length === 0 && (
          <p className="text-slate-600 font-mono text-sm">
            No comments yet on <em>{page}</em> — be first.
          </p>
        )}
        {comments?.map((c) => (
          <div key={c._id} className="bg-[#12121a] border border-[#1e1e2e] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm font-semibold text-slate-200">{c.author}</span>
              <span className="text-xs text-slate-600 font-mono">
                {new Date(c._creationTime).toLocaleString()}
              </span>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed">{c.body}</p>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          type="text"
          placeholder="Your name"
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          className="w-full bg-[#12121a] border border-[#1e1e2e] rounded-lg px-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500/50 font-mono"
        />
        <textarea
          placeholder="Leave a comment..."
          value={body}
          onChange={(e) => setBody(e.target.value)}
          rows={3}
          className="w-full bg-[#12121a] border border-[#1e1e2e] rounded-lg px-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500/50 font-mono resize-none"
        />
        <button
          type="submit"
          disabled={submitting || !author.trim() || !body.trim()}
          className="px-5 py-2 rounded-lg text-sm font-semibold transition-all disabled:opacity-40"
          style={{ background: accent + '22', color: accent, border: `1px solid ${accent}44` }}
        >
          {submitting ? 'Posting...' : 'Post comment'}
        </button>
      </form>
    </section>
  )
}
