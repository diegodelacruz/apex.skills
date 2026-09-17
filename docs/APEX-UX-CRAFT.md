# APEX UX Craft

`apex-ui-craft-safe` is the project workflow for APEX design quality, usability, responsive
behavior, accessibility, visual polish, and justified motion. It is selected by the APEX
orchestrator for natural-language requests such as “mejora el diseño”, “hazla más fácil de usar”,
“revisa responsive”, “audita la UX”, “pulir la interfaz”, or “revisa las transiciones”.

## Scope

The workflow is intentionally APEX-native: Universal Theme, page templates, theme roller, CSS,
Dynamic Actions, and declarative components remain the primary tools. It does not introduce a
React frontend or a UI library designed for another technology stack.

## Review gates

Every recommendation must pass these gates:

1. It improves a named user task, comprehension, feedback, or accessibility.
2. It works on narrow, typical, and wide viewports.
3. It preserves roles, authorization, validation, session state, keyboard flow, focus handling,
   dialog behavior, and business behavior.
4. It is usable with reduced motion and touch input.
5. It is backed by export or browser evidence and has a defined test.
6. It has explicit approval before CSS/JavaScript, template, plug-in, or production changes.

## Motion policy

Motion is optional. Avoid it on core navigation, keyboard-triggered actions, frequent data entry,
and dense enterprise data surfaces. When justified, make it short, interruptible, and limited to
properties that do not trigger layout work. `prefers-reduced-motion` is mandatory for meaningful
movement.

## Upstream reference

The approach selectively adapts the MIT-licensed repository
[`emilkowalski/skills`](https://github.com/emilkowalski/skills): its general design-engineering,
motion review, and restraint criteria. React Native, Swift, Sonner, and library-selection skills
are explicitly out of scope. See [UPSTREAMS.md](UPSTREAMS.md) and
[ACTUALIZACION-ECOSISTEMA.md](ACTUALIZACION-ECOSISTEMA.md) for provenance and update controls.
