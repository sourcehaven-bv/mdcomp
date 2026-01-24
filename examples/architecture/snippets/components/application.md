---
id: COMP-APP
title: Application Architecture
version: 2.1.0
framework: FastAPI
language: Python 3.12
tags: [application, backend, api]
---
## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| API Framework | FastAPI 0.109 | REST API, OpenAPI docs |
| ORM | SQLAlchemy 2.0 | Database abstraction |
| Validation | Pydantic 2.5 | Request/response validation |
| Task Queue | Celery 5.3 | Background jobs |
| Message Broker | Redis 7.0 | Task queue backend |

## Service Architecture

```
┌──────────────────────────────────────────────────────┐
│                    API Gateway                        │
└─────────────────────────┬────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Auth Service │ │  Core Service │ │Report Service │
│   (Keycloak)  │ │   (FastAPI)   │ │   (FastAPI)   │
└───────────────┘ └───────────────┘ └───────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Worker Service│
                  │   (Celery)    │
                  └───────────────┘
```

## API Design

- RESTful with OpenAPI 3.1 specification
- Versioned endpoints: `/api/v1/`, `/api/v2/`
- Authentication: Bearer tokens (JWT)
- Rate limiting: 1000 req/min per user
- Pagination: Cursor-based for large collections

## Deployment

- Container images built with multi-stage Dockerfile
- Deployed via GitHub Actions to ECS Fargate
- Blue-green deployment strategy
- Rollback capability within 5 minutes
