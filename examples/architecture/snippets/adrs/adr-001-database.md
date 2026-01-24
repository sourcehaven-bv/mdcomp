---
id: ADR-001
title: Use PostgreSQL as Primary Database
status: accepted
date: 2025-11-15
deciders: [Tech Lead, DBA, Security Officer]
tags: [database, infrastructure, critical]
supersedes: null
---
## Context

We need a relational database for storing customer data, transactions, and audit logs. The system must handle ~10,000 concurrent users and comply with GDPR requirements.

## Decision

We will use **PostgreSQL 16** as our primary database.

## Rationale

- Mature, battle-tested RDBMS with excellent reliability
- Native support for JSON columns (flexibility for semi-structured data)
- Row-level security for multi-tenant isolation
- Strong encryption at rest (pgcrypto) and in transit (TLS)
- Active community and long-term support

## Consequences

- **Positive:** ACID compliance, strong ecosystem, team familiarity
- **Negative:** Requires dedicated DBA expertise for optimization
- **Risks:** Vertical scaling limits; may need read replicas for growth

## Compliance

- GDPR Art. 32: Encryption at rest and in transit supported
- ISO 27001 A.10.1: Cryptographic controls available
