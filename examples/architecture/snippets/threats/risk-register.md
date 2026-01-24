---
id: RISK-REGISTER
title: Risk Register
last_updated: 2026-01-20
review_frequency: quarterly
owner: Security Officer
tags: [security, risk, compliance]
---
## Active Risks

| ID | Risk | Likelihood | Impact | Score | Owner | Status |
|----|------|------------|--------|-------|-------|--------|
| R-001 | Cloud provider outage | Low | High | 6 | Platform | Accepted |
| R-002 | Zero-day vulnerability | Medium | High | 9 | Security | Monitoring |
| R-003 | Key personnel departure | Medium | Medium | 6 | HR | Mitigating |
| R-004 | Supply chain attack | Low | Critical | 8 | Security | Monitoring |
| R-005 | Regulatory changes | Medium | Medium | 6 | Legal | Monitoring |

## Risk Matrix

```
           │ Low (1)  │ Medium (2) │ High (3)  │ Critical (4)
───────────┼──────────┼────────────┼───────────┼─────────────
High (3)   │    3     │     6      │     9     │     12
Medium (2) │    2     │     4      │     6     │      8
Low (1)    │    1     │     2      │     3     │      4
```

## Mitigations

### R-001: Cloud Provider Outage

- Multi-AZ deployment for high availability
- Daily backups with cross-region replication
- Documented disaster recovery procedure
- RTO: 1 hour, RPO: 15 minutes

### R-002: Zero-Day Vulnerability

- Security monitoring subscriptions (CVE, vendor advisories)
- Rapid patching process (critical: 48h)
- WAF with virtual patching capability
- Incident response plan ready

### R-004: Supply Chain Attack

- Dependency scanning (Snyk, Dependabot)
- Signed commits required
- Container image scanning
- SBOM generation for all releases
