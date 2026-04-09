---
description: "Workflow to resume a session — paste it in the chat when starting a new conversation."
---

# ⚡ Slash Command: /restart-session

## Instructions for the user
Paste the block below in the chat to kick off any session:

```
INIT TURBOQUANT FOR: [PROJECT_NAME]
CONTEXT: [WHAT YOU WERE WORKING ON]
OBJECTIVE: [WHAT YOU WANT TO DO TODAY]
PREVIOUS_MEMORY: [DESCRIBE CHECKPOINT OR "check 00-cortex.mdc"]
MODE: single_agent
```

## What the AI will do automatically

1. Run **STEP 0** (Regression Buffer check)
2. Read the **Current State** from the cortex
3. Report current checkpoint + next steps
4. Await confirmation before starting
