import { mutation, query } from './_generated/server'
import { v } from 'convex/values'

export const getByPage = query({
  args: { page: v.string() },
  handler: async (ctx, { page }) => {
    return ctx.db
      .query('comments')
      .withIndex('by_page', (q) => q.eq('page', page))
      .order('desc')
      .collect()
  },
})

export const add = mutation({
  args: {
    page: v.string(),
    author: v.string(),
    body: v.string(),
  },
  handler: async (ctx, args) => {
    return ctx.db.insert('comments', args)
  },
})
