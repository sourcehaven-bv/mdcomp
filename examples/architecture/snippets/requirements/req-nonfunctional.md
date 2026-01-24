---
id: REQ-NFR
title: Non-Functional Requirements
version: 1.1
last_updated: 2025-12-15
status: approved
tags: [requirements, nonfunctional, sla]
---
## Performance

| ID | Requirement | Target | Measured |
|----|-------------|--------|----------|
| NFR-001 | API response time (p95) | < 200ms | 145ms |
| NFR-002 | Page load time (p95) | < 2s | 1.8s |
| NFR-003 | Concurrent users supported | 10,000 | 12,500 |
| NFR-004 | Database query time (p99) | < 100ms | 78ms |

## Availability

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-010 | System uptime | 99.9% | 99.95% |
| NFR-011 | Planned maintenance window | < 4h/month | 2h/month |
| NFR-012 | Recovery Time Objective (RTO) | < 1h | 30min |
| NFR-013 | Recovery Point Objective (RPO) | < 1h | 15min |

## Security

| ID | Requirement | Target | Status |
|----|-------------|--------|--------|
| NFR-020 | Encryption at rest | AES-256 | Compliant |
| NFR-021 | Encryption in transit | TLS 1.3 | Compliant |
| NFR-022 | Password policy | NIST 800-63B | Compliant |
| NFR-023 | Session timeout | 30min idle | Compliant |
| NFR-024 | Audit log retention | 2 years | Compliant |
