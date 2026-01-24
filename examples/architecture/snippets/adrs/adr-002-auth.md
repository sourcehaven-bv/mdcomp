---
id: ADR-002
title: OAuth 2.0 with OIDC for Authentication
status: accepted
date: 2025-11-20
deciders: [Tech Lead, Security Officer]
tags: [authentication, security, critical]
supersedes: null
---
## Context

The platform requires secure user authentication supporting SSO integration with enterprise customers, MFA, and session management.

## Decision

We will implement **OAuth 2.0 with OpenID Connect** using Keycloak as the identity provider.

## Rationale

- Industry standard for modern authentication
- Supports SAML and OIDC for enterprise SSO requirements
- MFA built-in (TOTP, WebAuthn, SMS)
- Self-hosted option maintains data sovereignty
- Extensive audit logging for compliance

## Consequences

- **Positive:** Standards-based, enterprise-ready, flexible MFA options
- **Negative:** Additional infrastructure component to maintain
- **Risks:** Single point of failure; requires HA deployment

## Compliance

- ISO 27001 A.9.4: Access control to systems and applications
- GDPR Art. 32: Appropriate security measures for authentication
- NIS2: Strong authentication requirements
