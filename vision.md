# Nubi: product vision

Nubi is a goal-oriented mobile assistant for the work that accumulates around everyday life. A user should be able to describe an outcome, let an assistant find and organize the relevant information, and follow the work in one conversation.

## The experience

- **Home surfaces the next useful action.** Contextual banners can highlight campus notices, meals, transport, or progress toward a user's goal. Opening a task leads into the conversation that handles it.
- **Nubi and friends work together.** The group conversation coordinates everyday requests and scheduled jobs. Specialist characters join when their knowledge or tools are useful; progress and results remain in the same thread.
- **Individual assistants keep goal context.** A user can talk with a dedicated assistant about fitness, relationships, academics, home buying, or another goal, and bring in other specialists when needed.
- **Work is visible and verifiable.** An in-chat browser preview and tool results help users understand what happened. An external submission, reservation, or payment is complete only when its result has actually been confirmed.
- **Connections fit the task.** Dedicated APIs and structured tools should be preferred when available; a browser session can support services whose information or workflows require it.

## Initial focus: campus life

The early focus is helping students keep up with academic announcements, scholarships, assignments, calendars, email, dining, and travel. Examples include finding a relevant campus notice, preparing a document for review, identifying a meal before the busiest period, and coordinating a campus bus with a train timetable.

These examples describe the intended experience. Actual availability depends on the institution, provider access, and the implementation and verification status of each workflow.

## Design principles

1. Keep the conversation at the center of the experience.
2. Make specialist assistance feel personal and useful over time.
3. Preserve user control over accounts and consequential actions.
4. Use the minimum necessary account and device data, and protect stored credentials.
5. Show accurate status and distinguish observed results from plans, estimates, and simulations.
6. Build for both phone and tablet layouts.

## Development priorities

Near-term work includes more reliable campus sign-in and session handling, verifiable end-to-end workflows, timely scheduled execution, transit and meal data integration, and consistent in-chat progress and browser previews. Broader scenarios such as travel, social planning, shopping, research, and family assistance build on the same conversation and execution foundations.

Nubi is an evolving prototype. The vision is broader than the currently verified functionality; see the [README](README.md) and [reports](reports/) for the present scope.
