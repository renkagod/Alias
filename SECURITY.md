# Security Policy

## Supported versions

Security fixes are applied to the latest release on the `main` branch.

## Reporting a vulnerability

If you find a security issue, please **do not** open a public GitHub issue with exploit details.

Instead, use [GitHub private vulnerability reporting](https://github.com/renkagod/Alias/security/advisories/new) or contact the repository owner via GitHub.

Include:

- Description of the issue and impact
- Steps to reproduce
- Suggested fix (if you have one)

We aim to acknowledge reports within a few days.

## Deployment notes

- Never commit `.env` or bot tokens.
- Set `ADMIN_IDS` to your Telegram user ID(s). An empty value disables admin commands for everyone (safe default).
- Run the bot only with secrets loaded from environment variables or a private `.env` file.
