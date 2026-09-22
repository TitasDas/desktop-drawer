# Desktop Drawer product review

Date: 2026-09-22. Scope: the standalone Cinnamon applet and its release materials.
The audience is a Cinnamon user who wants a chosen folder within reach from the
panel. The review is an inspection backed by tests, not a user study.

## Review method

Applied the local Codebase Design, Humanizer, and Documentation and ADRs skills.
Installed and applied [Humbleteam Design Review](https://github.com/humbleteam/design-review)
at commit `70a3bfda1e079af1880cc2b41a088ae3340ccf1f`, after reading the skill and
its rubric. It was selected because its concrete usability review applies to
native desktop menus. Broader frontend generation skills were less relevant.
The skill is a development aid and is not bundled into Desktop Drawer.

The review also used the [Cinnamon Spices code-review guidance](https://github.com/linuxmint/cinnamon-spices-applets/blob/master/.github/copilot-instructions.md)
and the installed Cinnamon source for settings, menus and lifecycle behaviour.

## Original drawer: score 2 of 4

The native menu structure was sound. Folder context, recovery and presentation
needed a focused refinement. The score is a reviewer judgment, not a measured
usability result.

### 1. Show the active folder

Before: the heading said Desktop Drawer and the open action said Open selected folder, without naming it.
After: the heading shows the folder name above Open folder.
Why: [Nielsen heuristic 1, Visibility of system status](https://www.nngroup.com/articles/ten-usability-heuristics/). The user can identify the location being browsed.

### 2. Make folder selection visible

Before: changing folders required remembering the applet's right-click Configure menu.
After: Choose folder is available in the drawer, including empty and unavailable states.
Why: [Nielsen heuristic 6, Recognition rather than recall](https://www.nngroup.com/articles/ten-usability-heuristics/). A visible action reduces reliance on remembered instructions.

### 3. Report an opening failure

Before: a failed default-application launch only wrote to the Cinnamon log.
After: a notification explains that the item could not open and points to its default application.
Why: [Nielsen heuristic 9, Help users recognize, diagnose, and recover from errors](https://www.nngroup.com/articles/ten-usability-heuristics/). The failure has a visible recovery suggestion.

### 4. Make hover settings consistent

Before: turning hover off stopped the panel menu opening, but submenus still opened on hover.
After: Open menus on hover controls both. Click and keyboard navigation remain available.
Why: [Nielsen heuristic 4, Consistency and standards](https://www.nngroup.com/articles/ten-usability-heuristics/). The setting does what its label promises.

### 5. Use a recognisable small icon

Before: the panel icon combined a hexagon, folder, glow and diamond at panel size.
After: a folder and drawer handle remain legible without small decorative details.
Why: [Nielsen heuristic 2, Match between system and the real world](https://www.nngroup.com/articles/ten-usability-heuristics/). The icon represents the thing the applet opens.

Fix this first: folder selection and the active folder heading. These are the
first things a new user needs to understand before browsing. Both are implemented.

## Engineering changes

The applet retains one native menu and one settings object. Directory reading
stays behind the existing asynchronous method; no extra framework or speculative
abstraction was introduced. Closing the menu invalidates pending reads. The
file limit, depth limit and hidden-entry scan budget remain explicit.

Folder paths now retain whitespace. Async results do not update removed or
replaced menus. Tests cover the filesystem results and native Cinnamon behaviour,
including keyboard activation and default-application dispatch through an
isolated test handler. A real failed launch also produced the expected notification.

## Refreshed candidate: score 3 of 4

The specific findings above are addressed. The remaining work is user validation:
try it with normal desktop applications, assistive technology, other supported
themes and display scales. No measured accessibility compliance or broad version
compatibility is claimed. See BETA-CHECKLIST.md and VALIDATION.md for the evidence
and limits. Cinnamon Spices acceptance is still pending.
