# TurboQuant API Demo

This example demonstrates a standard Node.js Express API using **TurboQuant v4.2-Cortex**.

## Structure
By looking at the `.agents/rules` directory, you can see how the cortex is implemented:
- `00-cortex.mdc`: The main set of instructions that governs the AI agent in this project.
- `memory_turboquant_api_demo.json`: The state ledger that tracking the development stages and the regression buffer.

## Before vs After TurboQuant

### Before (Standard Agent)
- The agent randomly wanders searching for files (`index.js`, `app.js`, `server.js`).
- Frequently breaks existing endpoints because it didn't do read-only exploration first.
- Context amnesia means if you return the next day and say "add validation", it will ask you what libraries are installed and where the routes are.

### After (TurboQuant)
- The agent knows exactly that your entrypoint is `src/server.js` (`$server` alias).
- It performs `STEP 0` to check the regression buffer in the JSON file.
- It writes a detailed plan inside a `<thinking>` block before emitting changes.
- Leaves a clear checkpoint when you type `wrap up` so tomorrow's session starts exactly where you left off.
