---
finding: If db_url contains password and connection fails, that password may end up in log files, error reports, stack traces, user-facing error messages. SQLAlchemy exceptions often include the connection URL.
id: RR-YYXA
resolution: Added _sanitize_url() function that strips passwords from URLs before including them in error messages. All error messages now use sanitized URLs. Added comprehensive tests for URL sanitization.
severity: critical
status: addressed
title: Credentials exposed in error messages
type: review-response
---
