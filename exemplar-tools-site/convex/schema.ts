import { defineSchema, defineTable } from 'convex/server'
import { v } from 'convex/values'

export default defineSchema({
  comments: defineTable({
    page: v.string(),
    author: v.string(),
    body: v.string(),
  }).index('by_page', ['page']),
})
