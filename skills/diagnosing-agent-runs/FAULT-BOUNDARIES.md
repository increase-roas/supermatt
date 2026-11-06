# Fault boundaries for agent runs

Each boundary names where an agent run commonly breaks, what to inspect, and the trap that leads to a wrong diagnosis. Confirm the actual host and version before applying a contract: these describe the versions named, and newer releases may differ.

## Tool choice and arguments

Inspect the tool definition the agent actually saw (its `inputSchema`), the call it made, and the data that came back. Choosing the tool, extracting its arguments, and using its response are three separate failure points. Compare required properties, types, enums, and nesting. An `outputSchema` or `structuredContent` does not define the call's arguments. Discovery, host exposure, permission, and execution are distinct stages: a tool can be defined but not exposed, or exposed but denied.

## Protocol errors versus tool errors (MCP, revision 2025-11-25)

A top-level JSON-RPC `error` is a protocol failure. `result.isError: true` is a tool execution failure even when the transport succeeded. Read the returned `content` before treating a call as successful; a `CallToolResult` needs a `content` array even when `structuredContent` is present, so flag a missing array on its own. Input validation can come back as a tool execution error. Report transport success next to a tool error neutrally: do not claim the agent confused the two unless the trace shows it acted on the wrong one.

## Wrong answers and retrieval

Compare each disputed claim with the source passage the generation step actually received, keeping the source's qualifiers. Separate an absent source, a wrong filter, an excluded chunk, a stale snapshot, and unsupported synthesis. Vector-store ingestion can be asynchronous and removals eventually consistent, so an upload or deletion receipt does not prove what search returns now. Chunking can strip the context a passage needs, and retrieval and reranking fail separately. Inspect the retrieved chunks and filters before proposing a corpus change. If generation received only a stale passage, name stale retrieval as the fault; do not claim the selection cause is established.

## Instruction loading

Confirm which instructions the run actually loaded before alleging the agent ignored them. Codex reads guidance from the project root down to the launch directory, later (nearer) files winning, within its document-size cap. In each directory it takes the first nonempty file of `AGENTS.override.md`, `AGENTS.md`, then configured fallback names. Without a discovered project root, it checks only the current directory, so an `AGENTS.md` in a parent folder outside a git repository is not loaded. Claude Code's `/memory` lists instruction locations and `/context` shows what loaded at launch. `CLAUDE.md` and memory are context, not an enforced barrier. A file created mid-run is not proof it was loaded.

## Permissions

In the Claude Agent SDK, `allowedTools` adds auto-approval rules; tools it does not list can still be available. A bare `disallowedTools` entry removes a tool; a scoped deny pattern keeps the tool and denies matching calls. `canUseTool` runs only when earlier permission steps leave a call unresolved, and a `PreToolUse` hook is the documented gate before every call. Identify which step decided the call; do not assume a callback saw every action. In Codex, a hook runs only when it is both enabled and trusted.

## Runtime limits and state

In the OpenAI Agents SDK, exceeding `max_turns` raises `MaxTurnsExceeded` by default, but a configured error handler can return controlled final output that looks like success. Inspect the handler and the actual artifact, and read the turns before the limit before raising it. A handoff changes the current agent: match its inputs and output to the intended recipient. Missing trace payloads can follow `trace_include_sensitive_data=False`, and export queues delay dashboards, so a missing span is not proof nothing ran. In LangGraph, resuming an interrupt needs its checkpoint and the same thread ID, and it restarts the interrupted node, repeating any code that ran before the interrupt. Stop replay advice when earlier effects are uncertain.

## Claimed completion

Separate the transcript from the outcome in the environment. Verify the file contents, record, receipt, or resulting state the task required. "Done", a successful tool envelope, a handoff return, or a process exit alone does not prove the task finished.

## Attribution

Adapted from Sergey Skripko's [agent-debugging](https://github.com/grayskripko/marketing-skills) plugin (MIT, version 0.1.1). See [THIRD-PARTY-NOTICES.md](../../THIRD-PARTY-NOTICES.md).
