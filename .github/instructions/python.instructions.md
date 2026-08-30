---
applyTo: "src/**/*.py"
---

Use Python 3.11+ and strict typing. Prefer pure functions and dataclasses for domain policy; introduce
classes only for real state or lifecycle. Keep side effects at named boundaries. Use argv subprocess
execution, bounded inputs/outputs, explicit timeouts, path containment, and actionable errors.

