---
id: COMP-INFRA
title: Infrastructure Overview
environment: production
cloud_provider: AWS
region: eu-west-1
last_updated: 2026-01-15
tags: [infrastructure, aws, production]
---
## Cloud Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS eu-west-1                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ CloudFront  │───▶│     ALB     │───▶│    ECS      │     │
│  │    (CDN)    │    │   (HTTPS)   │    │  (Fargate)  │     │
│  └─────────────┘    └─────────────┘    └──────┬──────┘     │
│                                               │             │
│         ┌─────────────────────────────────────┤             │
│         │                    │                │             │
│         ▼                    ▼                ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │    RDS      │    │ ElastiCache │    │     S3      │     │
│  │ (PostgreSQL)│    │   (Redis)   │    │  (Storage)  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Secrets   │    │ CloudWatch  │    │   WAF v2    │     │
│  │   Manager   │    │   (Logs)    │    │ (Firewall)  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Component Inventory

| Component | Service | Version | Purpose |
|-----------|---------|---------|---------|
| Compute | ECS Fargate | - | Application containers |
| Database | RDS PostgreSQL | 16.1 | Primary data store |
| Cache | ElastiCache Redis | 7.0 | Session & query cache |
| Storage | S3 | - | File uploads, backups |
| CDN | CloudFront | - | Static assets, DDoS protection |
| Load Balancer | ALB | - | HTTPS termination, routing |
| Secrets | Secrets Manager | - | Credentials, API keys |
| Monitoring | CloudWatch | - | Logs, metrics, alarms |
| Firewall | WAF v2 | - | OWASP rule set |

## Networking

- VPC with public/private subnets across 3 AZs
- NAT Gateway for outbound traffic from private subnets
- VPC Flow Logs enabled for network monitoring
- Private endpoints for AWS services (S3, Secrets Manager)
