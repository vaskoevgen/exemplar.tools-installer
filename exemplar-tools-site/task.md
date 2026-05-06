# Task

Build a multi-page documentation website for the exemplar.tools suite of AI-assisted software engineering tools.

## What to Build

A React single-page application that documents how to use these tools in workflow order: Constrain, Ledger, Pact, Advocate, Arbiter, Baton, Sentinel, Chronicler, Stigmergy, Apprentice, and Kindex.

## Pages Required

- Home page: overview of the exemplar.tools workflow, quick-start table, and the closed loop diagram
- One page per tool (11 pages total): constrain, ledger, pact, advocate, arbiter, baton, sentinel, chronicler, stigmergy, apprentice, kindex

## Features Per Page

Each tool page must include:
- Tool name and one-line description
- Step number badge matching howto.md step order
- Version badge showing the tool version
- Step-by-step instructions with bash code blocks
- YouTube video embed where a video URL exists
- Comments section at the bottom backed by Convex real-time database

## Data Model (Convex)

The Convex backend stores user comments. Each comment has: page (string for tool name), author (string), body (string), createdAt (number timestamp). Convex query function listComments takes page argument. Convex mutation function addComment takes page, author, body arguments.

## Navigation

A fixed left sidebar showing all tool pages in step order with step numbers. Active page is highlighted. Logo at the top of sidebar links to home.

## Design

Dark industrial terminal aesthetic with near-black background. Primary accent is electric cyan. Each tool gets its own accent color. Heading font is Instrument Serif from Google Fonts. Code font is JetBrains Mono from Google Fonts. Body font is Inter. Subtle grid lines in background. Animated fade-in on page content load.

## Tech Stack

- Vite with React and TypeScript template, initialized with bun create vite
- Tailwind CSS for all styling
- Bun as package manager, never npm or yarn
- React Router v6 for client-side routing with BrowserRouter
- Convex npm package for real-time comments database
- Dev server configured to run on port 4000 in vite.config.ts

## YouTube Video URLs Per Tool

- constrain page: https://www.youtube.com/embed/wkQeCPhlQD0
- ledger page: https://www.youtube.com/embed/yZn64yO87VM
- pact page: https://www.youtube.com/embed/vwHyrU13Cds
- advocate page: https://www.youtube.com/embed/sKOM3NvW7lY
- arbiter page: https://www.youtube.com/embed/4f5uqWGs2ws
- baton page: https://www.youtube.com/embed/XGu3XTfvG1c
- sentinel page: https://www.youtube.com/embed/k8RVrSnEw6I
- chronicler page: https://www.youtube.com/embed/a94Kpf0bYVg
- stigmergy page: https://www.youtube.com/embed/4z7--TKIvQ4
- apprentice page: https://www.youtube.com/embed/BhltpaigLTo
