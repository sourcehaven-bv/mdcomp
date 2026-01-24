---
id: ADR-003
title: End-to-End Encryption Strategy
status: accepted
date: 2025-12-01
deciders: [Security Officer, Tech Lead, Compliance Officer]
tags: [security, encryption, compliance, critical]
supersedes: null
---
## Context

Customer data must be protected at rest, in transit, and during processing to meet regulatory requirements and customer trust expectations.

## Decision

Implement a layered encryption strategy:

1. **In Transit:** TLS 1.3 for all network communication
2. **At Rest:** AES-256 for database and file storage
3. **Application Layer:** Field-level encryption for PII using envelope encryption

## Rationale

- Defense in depth approach
- Key management via HashiCorp Vault
- Meets insurance and compliance requirements
- Enables key rotation without data migration

## Consequences

- **Positive:** Strong security posture, regulatory compliance
- **Negative:** Performance overhead (~5-10%), increased complexity
- **Risks:** Key management is critical; loss = data loss

## Compliance

- GDPR Art. 32: Encryption as appropriate technical measure
- ISO 27001 A.10.1.1: Policy on use of cryptographic controls
- PCI-DSS Req. 3.4: Render PAN unreadable
