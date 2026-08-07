# Security policy

## Reporting

Report suspected vulnerabilities privately to the repository owner. Do not put
API keys, personal recordings, private media, exploit payloads, or machine
configuration in a public issue.

## Secrets

- The OpenAI SDK reads `OPENAI_API_KEY` from the environment.
- `.env` files and private keys are ignored and must never be committed.
- Treat any committed credential as compromised and rotate it immediately.
- Examples and tests must use placeholders or injected fake clients.

## Privacy

Camera, microphone, and screen capture can contain personal data. Generated
audio/video and runtime logs are local artifacts and are excluded from Git.

## Supported code

Security fixes target the default branch. Historical repair scripts and old
snapshots are unsupported.
