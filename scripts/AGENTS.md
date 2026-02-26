# Scripts rules

- Scripts are thin CLIs only.
- Scripts must import ONLY from bidcvc.api.* (never from bidcvc.models.* directly).
- Provide --help for each script.
- Scripts may raise NotImplementedError for encoding until models are wired, but must fail cleanly.

Tip: After you create these, you can ask Codex to confirm it sees them (nested precedence, active files).
