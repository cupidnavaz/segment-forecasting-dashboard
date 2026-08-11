# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 1.0.x | Yes |

## Reporting a vulnerability

Do not publish sensitive vulnerability details in a public issue.

Report suspected vulnerabilities privately to the project maintainers through the repository's configured private security reporting channel.

Include:

- A clear description of the issue.
- Reproduction steps.
- Affected version or commit.
- Potential impact.
- Any suggested mitigation.

## Security practices

- Never commit API keys, passwords, tokens, or Streamlit secrets.
- Keep dependencies updated.
- Review dependency changes before release.
- Treat uploaded business data as sensitive unless explicitly classified otherwise.
- Validate external data before using it in forecasts.
- Do not represent static market fixtures as live financial information.
