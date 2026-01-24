---
id: THREAT-MODEL
title: Threat Model Summary
methodology: STRIDE
last_review: 2026-01-10
next_review: 2026-04-10
status: current
tags: [security, threats, stride]
---
## Assets

| Asset | Classification | Owner |
|-------|---------------|-------|
| Customer PII | Confidential | Data Protection Officer |
| Authentication credentials | Secret | Security Team |
| Financial transactions | Confidential | Finance Team |
| Application source code | Internal | Engineering |
| Infrastructure configs | Internal | Platform Team |

## STRIDE Analysis

### Spoofing

| Threat | Risk | Mitigation | Status |
|--------|------|------------|--------|
| Credential theft | High | MFA enforced, breach monitoring | ✅ Mitigated |
| Session hijacking | High | Secure cookies, short TTL | ✅ Mitigated |
| API key compromise | Medium | Key rotation, scope limits | ✅ Mitigated |

### Tampering

| Threat | Risk | Mitigation | Status |
|--------|------|------------|--------|
| SQL injection | Critical | Parameterized queries, WAF | ✅ Mitigated |
| Request manipulation | High | Input validation, HMAC signing | ✅ Mitigated |
| Log tampering | Medium | Immutable logs (CloudWatch) | ✅ Mitigated |

### Repudiation

| Threat | Risk | Mitigation | Status |
|--------|------|------------|--------|
| Denial of actions | Medium | Comprehensive audit logging | ✅ Mitigated |
| Timestamp manipulation | Low | Server-side timestamps, NTP | ✅ Mitigated |

### Information Disclosure

| Threat | Risk | Mitigation | Status |
|--------|------|------------|--------|
| Data breach | Critical | Encryption, access controls | ✅ Mitigated |
| Error message leakage | Medium | Generic errors in prod | ✅ Mitigated |
| Backup exposure | High | Encrypted backups, access logs | ✅ Mitigated |

### Denial of Service

| Threat | Risk | Mitigation | Status |
|--------|------|------------|--------|
| DDoS attack | High | CloudFront, WAF, rate limiting | ✅ Mitigated |
| Resource exhaustion | Medium | Auto-scaling, limits | ✅ Mitigated |
| Algorithmic complexity | Low | Query timeouts, pagination | ✅ Mitigated |

### Elevation of Privilege

| Threat | Risk | Mitigation | Status |
|--------|------|------------|--------|
| RBAC bypass | Critical | Centralized authz, testing | ✅ Mitigated |
| Container escape | High | Non-root, read-only FS | ✅ Mitigated |
| Dependency vulnerabilities | High | Dependabot, SCA scanning | ✅ Mitigated |
