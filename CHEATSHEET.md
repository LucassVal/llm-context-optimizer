# TurboQuant v4.2 — Quick Cheat Sheet

## 🎯 Voice Triggers
- **"Wrap up"** / **"That's it for today"** → Saves everything + backups
- **"Resume"** / **"Where did we leave off"** → Reads checkpoint and context
- **"Create"** / **"Implement"** → Starts Explore-Plan-Act cycle
- **"Error"** / **"Bug"** → Starts Debug Workflow
- **"!token-check"** → Calculates token estimate of the JSON memory

## 📁 Essential Aliases (Common Examples)
- `$app` = `src/index.ts`
- `$cfg` = `vite.config.ts` (or equivalent config)
- `@cmp` = `src/components/`
- `!dev` = `pnpm dev` (or start command)
- `?fc` = `React functional component` (architectural pattern)

## 🔒 Atomic Locks (Never Touch Without Unlocking)
> Examples of files the AI should never alter without your explicit order:
- `$cfg` (project configurations)
- `prisma/schema.prisma` (database)
- Base dependencies (`package.json`, `Cargo.toml`, etc.)
