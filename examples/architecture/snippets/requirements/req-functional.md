---
id: REQ-FUNC
title: Functional Requirements
version: 1.2
last_updated: 2025-12-15
status: approved
tags: [requirements, functional]
---
## User Management

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-001 | Users can register with email and password | Must | Implemented |
| FR-002 | Users can authenticate via SSO (SAML/OIDC) | Must | Implemented |
| FR-003 | Administrators can manage user roles | Must | Implemented |
| FR-004 | Users can enable MFA (TOTP/WebAuthn) | Must | Implemented |
| FR-005 | Password reset via email verification | Must | Implemented |

## Data Management

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-010 | Users can import data via CSV/JSON | Must | Implemented |
| FR-011 | Users can export their data (GDPR) | Must | Implemented |
| FR-012 | Data is automatically backed up daily | Must | Implemented |
| FR-013 | Users can request data deletion | Must | In Progress |

## Reporting

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-020 | Generate PDF reports from templates | Should | Implemented |
| FR-021 | Schedule automated report delivery | Should | Planned |
| FR-022 | Real-time dashboard with key metrics | Must | Implemented |
