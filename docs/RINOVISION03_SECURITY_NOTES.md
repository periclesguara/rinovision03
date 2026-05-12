# RINOVISION03 Security Notes

## Confirmed

- `.env` exists and was not printed or copied.
- `.env.example` was created with placeholders only.
- `.gitignore` now ignores `.env`, env variants, runtime data outputs, logs, media outputs, and virtualenvs.
- Hardcoded API key patterns found in versionable legacy files were mechanically redacted to `REDACTED_OPENAI_KEY`.

## Risks

- Hardcoded API secrets were detected in legacy scripts, logs, config experiments, and indexed assistant files. Secret values are not included in this report.
- Some legacy OpenAI clients are created at import time.
- Some RAG code uses dangerous local deserialization.
- Historical logs appear to include command history with sensitive material.

## Immediate Recommendation

- Rotate exposed provider keys.
- Replace hardcoded secrets with `os.getenv`.
- Archive sensitive historical logs outside Git after a manual owner review.
- Keep assistant/API calls explicit and provider-adapter based.
