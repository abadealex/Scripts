# SaaS Architecture Overview

## Overview

This document provides a high-level view of the SmartScripts SaaS platform architecture. The system is designed to be modular, scalable, and secure to support multi-tenant environments with billing, compliance, analytics, and AI-assisted grading.

---

## Components

### 1. Backend

- **Flask API**: Core REST API with modular blueprints for authentication, submissions, grading, billing, and organization management.
- **Database**: PostgreSQL (or other relational DB) with SQLAlchemy ORM.
- **Migrations**: Alembic for schema version control.
- **AI Modules**: Grading, OCR, scoring, and text matching.

### 2. Frontend

- **React**: SPA with routes for login, dashboard, organization management, billing, and admin audit logs.
- **Contexts & Hooks**: For managing auth, organizations, billing, and audit trails.
- **Styling**: Tailwind CSS.

### 3. Billing

- **Stripe Integration**: Handles subscriptions, webhooks, and invoice generation.
- **Subscription Plans**: Different tiers with role-based feature access.

### 4. Compliance & Security

- **GDPR Tools**: Data download & deletion handlers.
- **Audit Logging**: Centralized logging of user actions for traceability.
- **Role-Based Access Control (RBAC)**: Middleware to restrict API access.

### 5. Analytics & Monitoring

- **Usage Metrics**: Engagement tracking and teacher reports.
- **Health Checks**: API status endpoints and error tracking with Sentry.
- **Rate Limiting**: Protects endpoints from abuse.

### 6. Multi-Tenancy

- Supports organizations/teams with user invites and role management.

---

## Deployment & CI/CD

- Docker containers for consistent environments.
- GitHub Actions workflows for automated tests, audit log backups, and production deployment.
- Railway or Heroku for cloud hosting.

---

## File Storage Structure

Uploaded files are organized by type for better structure, access control, and processing.

```plaintext
uploads/
├── answers/
│   ├── sample_q1.jpg
│   └── sample_q2.jpg
├── rubrics/
│   └── rubric_math_2025.pdf
├── guides/
│   └── teacher_guide_geometry.pdf
├── feedback/
│   ├── stu123_feedback.json
│   └── annotated_stu123_q2.png
