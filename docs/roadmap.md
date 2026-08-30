# V3 Boundaries and Future Considerations

V3 provides a VS Code-first manager using GitHub Copilot Chat native subagents, a thin extension
adapter, a local engineering-mission workflow, role contracts, project evidence, explicit quality
execution, worktree isolation, optional bounded GitHub Copilot CLI role execution, and guarded
delivery.

It does not include a generic provider framework, autonomous background daemon, hosted control
plane, custom chat UI, custom model provider, MCP server, plug-in marketplace, universal framework
selector, distributed queue, analytics database, or multi-user state service.

Future work should be selected only from observed mission results: benchmark Koda against raw
Copilot use, measure maintainability and security outcomes, improve routing from evidence, and
consider another provider only when a real requirement justifies a shared boundary.
