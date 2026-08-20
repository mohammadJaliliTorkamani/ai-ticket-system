# Security model

- No authentication or registration exists because the application owns no user data.
- The API key is a Pydantic `SecretStr`, exists only for one browser/backend/OpenAI request, is cleared from the form on submission, and is never persisted or logged.
- Every displayed transcript replaces authorization with `[REDACTED]`; the backend constructs the transcript rather than reflecting raw headers.
- The API accepts only allowlisted models, messages up to 10,000 characters, bounded output tokens, a bounded timeout, and one SDK retry.
- Per-client hourly limiting runs in the single API worker. Host Nginx/upstream protection should be added for higher traffic or multi-instance deployments.
- API errors are mapped to safe messages without stack traces. Logs include request IDs and event names, not prompts or credentials.
- Production containers are non-root, capability-dropped, read-only, resource-limited, health-checked, and exposed only through a loopback gateway behind host Nginx/TLS.
- OpenAI receives the submitted message and key. Ticketifier sets `store=false`, but users remain responsible for understanding their OpenAI account's data controls, access, quota, and charges.

Residual risk: host-root, Docker-daemon, malicious browser-extension, or in-process compromise can observe transient secrets. Patch the VPS and browser, restrict Docker access, use project-scoped OpenAI keys with appropriate limits, and revoke any key suspected of exposure.
