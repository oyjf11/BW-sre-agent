# Run Detail Realtime Refresh Design

## Goal

Make the incident run detail page update without manual browser refreshes. The page
must keep events, run status, evidence, diagnosis, remediation, and trace metadata
current while preserving readable content during refreshes.

SSE is the primary realtime channel. REST incremental polling is the fallback when
SSE is unavailable. The UI uses progressive updates with explicit loading and
waiting states.

## Current Problems

The existing implementation intends to support automatic updates but has protocol
and fallback defects:

- The backend sends named SSE events while the frontend only handles default
  `message` events.
- The frontend fallback polls `/incidents/runs/{run_id}/stream`, which is a
  streaming endpoint, instead of the JSON `/incidents/runs/{run_id}/events`
  endpoint.
- The fallback cursor is never updated and is passed as `last_event_ts` even though
  it is intended to identify an event.
- The in-memory backend event bus publishes from graph execution code that may run
  outside the SSE request event loop. Cross-thread queue delivery must be verified
  and made thread-safe if required.
- The page refreshes artifacts in scattered callbacks rather than through one
  synchronization policy.

## Chosen Approach

Use SSE as the realtime primary channel and REST incremental polling as a complete
fallback channel.

Do not expand SSE into a general artifact delivery protocol in this iteration.
Events remain the SSE payload. Status and generated artifacts are fetched through
existing REST endpoints after relevant events and while fallback polling is
active.

## Architecture

### Frontend Synchronization Controller

Introduce one run-detail synchronization controller. It owns:

- SSE connection lifecycle.
- Connection state: `connecting`, `live`, `polling`, `reconnecting`, `stopped`.
- The last observed `event_id`.
- Event deduplication by `event_id`.
- REST fallback polling.
- SSE reconnection attempts while fallback polling is active.
- A throttled artifact refresh policy.
- Cleanup of EventSource instances, timers, callbacks, and in-flight refresh work.

The page consumes controller state and data. UI components do not independently
create realtime connections or duplicate polling logic.

Use one controller instance per mounted run-detail page. When the run ID changes
or the page unmounts, dispose of the instance and fully clear callbacks, cursor
state, timers, and connection status. Do not reuse the existing process-wide SSE
singleton for run-detail synchronization.

### Backend SSE Protocol

`GET /incidents/runs/{run_id}/stream` emits serialized `RunEvent` payloads as
default SSE `message` events so the frontend can use `EventSource.onmessage`
consistently.

The persisted event record remains the source of truth. SSE is a low-latency
notification path, not the only delivery mechanism.

Verify that graph execution can safely notify SSE subscribers when publishing
occurs outside the SSE request event loop. If the current `asyncio.Queue`
interaction is not thread-safe, capture the subscriber loop and enqueue with a
thread-safe loop handoff such as `loop.call_soon_threadsafe`.

### Data Flow

1. On initial page load, request run status, the complete event list, evidence,
   diagnosis, remediation, and trace metadata in parallel where possible.
2. Establish the SSE connection after initial data loading starts. Events received
   during initialization are merged by `event_id`, preventing loss and duplicates.
3. On each SSE event, append the event immediately and schedule a throttled refresh
   for run status, evidence, diagnosis, remediation, and trace metadata.
4. If SSE disconnects, switch to REST fallback polling immediately and show the
   fallback notice.
5. During fallback, request incremental events from
   `/incidents/runs/{run_id}/events?last_event_id={event_id}` and refresh status and
   artifacts.
6. While polling, periodically attempt to re-establish SSE.
7. After SSE reconnects, perform one REST incremental compensation fetch, merge
   events by `event_id`, stop fallback polling, and hide the fallback notice.
8. When the run reaches `COMPLETED`, `FAILED`, or `WAITING_HUMAN`, perform one
   final synchronization pass and stop continuous polling.
9. When an approval resumes a `WAITING_HUMAN` run while the detail page remains
   open, the page must detect the resumed non-terminal status and restart live
   synchronization. A lightweight status check may remain active for this purpose.

## Refresh Policy

Event delivery and artifact refresh have different latency requirements:

- Append events immediately.
- Refresh run status promptly after event receipt.
- Throttle artifact refreshes so a burst of SSE events does not create a burst of
  duplicate REST requests.
- Prevent older overlapping requests from overwriting newer data. Use request
  sequencing, cancellation, or an equivalent latest-result rule.
- Preserve existing artifact content while refreshing. Do not replace populated
  cards with loading placeholders.

Exact timer values are implementation details, but defaults should favor a
responsive local experience without excessive requests:

- REST fallback polling: approximately every 3 seconds.
- SSE reconnection attempts: approximately every 5 seconds.
- Artifact refresh throttle: approximately 500-1000 milliseconds.
- Terminal or approval-wait status check: a low-frequency poll, approximately every
  5 seconds, when needed to detect resumed execution.

## Interaction Design

Use progressive updates. Do not block the page with a full-page loading overlay
after initial rendering.

### Initial Load

Show skeleton states for:

- Header and run status.
- Workflow stepper.
- Main tab content.
- Sidebar cards.

If initial loading fails, replace the skeleton with an explicit error state and a
retry action.

### Running State

- Show the current stage in the header status area.
- Keep the event stream readable while new events append.
- Show localized loading states for artifacts that do not exist yet:
  "collecting evidence", "generating diagnosis", and "generating remediation".
- When an existing artifact refreshes, keep its content visible and show a compact
  refresh indicator near the section title.
- Show the most recent update time for long-running waits.

### SSE Fallback

When SSE disconnects, show a lightweight notice at the top of the detail page:

> Realtime connection interrupted. Switched to automatic refresh and attempting
> to reconnect.

The notice disappears automatically after SSE reconnects and the compensation
fetch completes.

### Approval Wait And Terminal States

- For `WAITING_HUMAN`, show the existing approval card and navigation entry, then
  perform a final artifact refresh.
- For `COMPLETED` and `FAILED`, hide running indicators after final synchronization.
- Do not clear events or generated content when entering a terminal state.

## Responsive Layout

The page must be readable without overlapping content at `1440px`, `1024px`,
`768px`, and `375px` viewport widths.

- Use the existing two-column main-content and sidebar layout at `1440px` and
  `1024px`.
- Switch to one column at `768px` and `375px`.
- Allow header status, fallback notice, and tabs to wrap.
- Allow long run IDs, service names, event text, and external links to wrap or
  truncate with an accessible full-value affordance.
- Keep consistent card spacing and reserve enough space for refresh indicators.
- Ensure loading indicators do not overlap card text or change content width
  unexpectedly.
- Reject horizontal page overflow, clipped controls, text collisions, and
  overlapping cards during browser verification.

## Error Handling

- A transient SSE failure changes connection state to `polling`; it does not
  discard loaded content or produce a full-page error.
- Polling errors keep the fallback notice visible and retry on the next interval.
- Malformed SSE payloads are ignored and logged without stopping synchronization.
- Artifact endpoints may return `404` while data is not generated yet. Treat those
  responses as pending states, not fatal errors.
- Non-pending endpoint failures preserve the previous successful content and expose
  a retry action in the affected artifact card. If that card has no previous
  content, show a localized card-level error state instead of an empty panel.
- Page unmount cancels all timers, closes SSE, and prevents stale responses from
  updating state.

## Testing

### Frontend Unit Tests

Cover:

- Default SSE `message` handling.
- Event append and `event_id` deduplication.
- Cursor updates after SSE and REST event delivery.
- SSE disconnect fallback to JSON `/events`.
- Incremental polling with `last_event_id`.
- Automatic SSE reconnection.
- Compensation fetch after reconnection.
- Artifact refresh throttling and latest-result behavior.
- Terminal-state synchronization and timer cleanup.
- Approval resume detection.
- Full cleanup on page unmount and run ID changes.

### Page And Component Tests

Cover:

- Initial skeleton states.
- Local artifact loading states.
- Existing artifact content remaining visible while refreshing.
- Top fallback notice appearing on disconnect and disappearing after recovery.
- Approval wait presentation.
- Error state and retry action.

### Backend Tests

Cover:

- SSE stream payloads use the agreed default `message` protocol.
- Event persistence remains intact.
- Subscribers receive newly published events.
- Publishing safely wakes an SSE subscriber across thread or event-loop boundaries.
- Incremental event retrieval by `last_event_id`.

### Browser Verification

Use the local app to verify:

- Automatic updates without manual refresh.
- SSE disconnect, REST fallback, automatic SSE recovery, and compensation fetch.
- No duplicate events during fallback transitions.
- Correct loading, waiting, and final states.
- No overlap, horizontal overflow, clipped controls, or spacing regressions at
  `1440px`, `1024px`, `768px`, and `375px`.

## Scope Boundaries

This iteration does not:

- Replace REST artifact endpoints with SSE artifact payloads.
- Introduce WebSockets.
- Add a cross-process event broker.
- Redesign unrelated pages.
- Change incident graph semantics.

If deployment later uses multiple backend workers or multiple application
instances, the in-memory event bus must be replaced with a shared pub/sub backend.
That infrastructure change is intentionally outside this iteration.
