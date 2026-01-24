---
id: LEGAL-GDPR
title: GDPR Compliance Summary
regulation: GDPR
jurisdiction: EU
last_review: 2025-12-01
status: compliant
tags: [legal, gdpr, privacy, compliance]
---
## Applicable Articles

### Article 5 - Principles

- **Lawfulness, fairness, transparency:** Privacy policy published, consent collected
- **Purpose limitation:** Data used only for stated purposes
- **Data minimization:** Only necessary data collected
- **Accuracy:** Users can update their data
- **Storage limitation:** Retention policy implemented (see below)
- **Integrity and confidentiality:** Encryption at rest and in transit

### Article 17 - Right to Erasure

Users can request deletion of their personal data through:
1. Self-service in account settings
2. Support ticket with identity verification
3. Automated process completes within 30 days

### Article 32 - Security of Processing

| Measure | Implementation |
|---------|----------------|
| Encryption | AES-256 at rest, TLS 1.3 in transit |
| Access Control | RBAC with principle of least privilege |
| Monitoring | 24/7 security monitoring, SIEM integration |
| Testing | Annual penetration tests, continuous scanning |

### Article 33/34 - Breach Notification

- Automated breach detection via anomaly monitoring
- Incident response plan with 72-hour notification SLA
- Data Protection Officer: dpo@example.com

## Data Retention

| Data Type | Retention Period | Legal Basis |
|-----------|------------------|-------------|
| User accounts | Until deletion requested | Contract |
| Transaction logs | 7 years | Legal obligation |
| Audit logs | 2 years | Legitimate interest |
| Marketing data | Until consent withdrawn | Consent |
