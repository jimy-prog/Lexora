# ADS: Lexora Platform

## 1. Purpose

This document defines the architectural direction for transforming the current local teacher platform into `Lexora`:

- `Lexora Core`: the main online school platform for teacher operations and student access
- `Lexora Mock`: a child platform focused on IELTS-style mock tests

The goal is to move from a single-user local admin tool to a secure, always-available web platform with clear role separation, scalable content management, and phased delivery.

## 2. Current State Assessment

### Current technical stack

- Backend: FastAPI
- Rendering: Jinja2 templates
- Database: SQLite
- Auth: single shared password stored in local file
- Storage: local filesystem for uploads
- Deployment style: local machine / tunnel-oriented usage

### Current functional modules already present

- Dashboard
- Students
- Groups
- Lessons / timetable
- Attendance
- Payments / finance
- Courses
- Homework
- Performance
- Waitlist
- Online lesson settings
- Reports / exports
- Archive
- Profile / settings

### Current architectural limitations

- Single-user authentication only
- No user roles
- No persistent multi-user session model
- SQLite is acceptable for local use but weak for concurrent production traffic
- Local file storage is not suitable for reliable 24/7 public usage
- Brand naming is still tied to `Teacher Admin`
- No separation between internal admin flows and future student portal flows
- No dedicated exam engine for IELTS-style digital mocks
- No ingestion pipeline for converting printed test materials into structured online tests

## 3. Business Direction

### Phase priorities requested

Priority now:

1. Convert the platform into a proper website available 24/7
2. Build the foundations of a separate mock-test platform

Later:

3. Expand into a full online school ecosystem for students

### New product naming

Primary brand:

- `Lexora`

Recommended product split:

- `Lexora Core` for school/admin/student platform
- `Lexora Mock` for IELTS mock exams

This split keeps one brand family while allowing separate product focus.

## 4. Product Vision

### Lexora Core

The central web platform for:

- owner/developer administration
- teacher operations
- student access
- learning materials
- scheduling
- attendance
- homework
- performance tracking
- payments and reporting

### Lexora Mock

A dedicated examination environment for:

- IELTS-style mock exams
- digital test publishing
- time-limited student attempts
- answer capture
- scoring workflows
- review and analytics
- content ingestion from printed materials by admin only

## 5. Target User Roles

### 5.1 Super Admin / Developer

You. Full control over:

- platform settings
- branding
- users and roles
- content publishing
- test ingestion
- storage and moderation
- analytics

### 5.2 Teachers

Future role for:

- groups and students
- attendance
- homework
- performance notes
- course progress
- selected mock review permissions

### 5.3 Students

For:

- personal dashboard
- timetable
- homework and materials
- results and feedback
- mock-test participation

### 5.4 Parents

Optional later role for:

- progress visibility
- attendance visibility
- payment status

## 6. Target Architecture

### 6.1 Recommended platform direction

Keep FastAPI as the backend foundation for now, but evolve the project into a production-ready web application with stronger boundaries:

- `Backend API + server-rendered admin` in FastAPI
- `PostgreSQL` as production database
- `Object storage` for files and scanned materials
- `Role-based authentication`
- `Modular apps` inside one repository

### 6.2 Recommended system domains

#### Domain A: Identity & Access

- users
- roles
- sessions
- password reset
- audit logs

#### Domain B: School Operations

- groups
- students
- lessons
- attendance
- payments
- reports
- waitlist

#### Domain C: Learning Content

- courses
- modules
- lessons
- homework
- downloadable materials

#### Domain D: Student Portal

- dashboard
- progress
- schedule
- homework
- course access

#### Domain E: Mock Test Platform

- test library
- sections
- question blocks
- answers
- attempts
- timers
- scoring
- publication workflow

#### Domain F: Document Ingestion

- upload printed test PDFs/images
- OCR extraction
- AI-assisted structuring
- admin verification
- publish to mock platform

## 7. Proposed Technical Stack

### Backend

- FastAPI
- SQLAlchemy / Alembic
- Pydantic

### Database

- Development: SQLite can remain temporarily
- Production: PostgreSQL required

### Frontend

Recommended staged approach:

- Stage 1: continue with Jinja admin to move faster
- Stage 2: add dedicated student-facing frontend, likely React/Next.js or a modern SPA/SSR frontend

Reason:

- fastest path to launch is to keep the existing admin UI alive
- student portal and mock exam experience will benefit from a more dynamic frontend later

### Storage

- local in development
- S3-compatible storage in production for uploads, scans, and test assets

### Authentication

- email/phone + password accounts
- secure password hashing
- database-backed sessions or JWT + refresh model
- role-based access control

### Deployment

- app server on VPS or managed platform
- reverse proxy + HTTPS
- background jobs for OCR / ingestion / backups
- monitoring, error logging, and daily backups

## 8. Data Architecture Evolution

### Current data reality

Current schema is centered around:

- groups
- students
- lessons
- attendance
- payments
- tests
- performance
- settings

### New entities required

#### Identity

- users
- roles
- user_roles
- sessions
- audit_logs

#### Student access

- student_accounts
- parent_accounts
- invitations

#### Mock platform

- exam_collections
- exams
- exam_sections
- question_groups
- questions
- answer_options
- passages
- media_assets
- exam_publications
- exam_attempts
- attempt_answers
- attempt_events
- scores

#### Content ingestion

- source_documents
- document_pages
- OCR_blocks
- extracted_exam_drafts
- publication_reviews

## 9. Security Requirements

- remove single shared password model
- remove in-memory-only session model
- hashed passwords with strong algorithm
- CSRF protection for forms
- role-checked routes
- audit trail for admin actions
- private file access control
- signed URLs or protected downloads for sensitive files
- environment-based secrets management

## 10. Rebrand Scope: Teacher Admin -> Lexora

Rebrand must cover:

- application title
- template branding
- login screen
- internal labels
- scripts and startup messages
- database filename strategy where appropriate
- backup naming
- upload/storage naming
- developer-facing documentation

Recommended rename strategy:

- product/UI brand: rename immediately to `Lexora`
- technical package paths: rename carefully in early implementation phase
- database filename: migrate from `teacher_admin.db` to `lexora.db` with safe fallback or migration copy

## 11. Delivery Strategy

### Guiding principle

Do not try to build the full online school in one jump.

Instead:

1. stabilize current platform
2. rebrand it
3. make it production-ready
4. add multi-user auth and roles
5. launch admin + student access
6. build mock platform
7. later expand the full online school experience

## 12. Phased Roadmap

### Phase 0: Architecture and cleanup

Objective:

- prepare safe migration foundation

Tasks:

- audit current routes, templates, models, settings
- create docs and target architecture
- define naming rules for `Lexora`
- identify migration-sensitive files
- create config layer for environment variables

Deliverable:

- approved ADS

### Phase 1: Lexora rebrand and production hardening

Objective:

- convert current project from local branded tool into deployable `Lexora` admin platform

Tasks:

- rename visible branding to `Lexora`
- centralize app metadata/config
- replace hardcoded secrets
- prepare `lexora.db` naming strategy
- improve startup scripts
- add production config support
- clean static and upload structure

Deliverable:

- `Lexora` branded admin platform ready for deployment preparation

### Phase 2: Real authentication and role model

Objective:

- support multiple accounts securely

Tasks:

- create `users` and `roles` tables
- migrate from shared password to per-user accounts
- create super admin account for you
- protect routes by role
- create separate login experiences if needed

Deliverable:

- secure multi-user auth with `developer/admin` and future `student` roles

### Phase 3: Production web deployment

Objective:

- make the platform available 24/7

Tasks:

- PostgreSQL support
- migration scripts
- deployment config
- HTTPS-ready hosting setup
- file storage abstraction
- backups and monitoring

Deliverable:

- public web deployment baseline

### Phase 4: Student portal foundation

Objective:

- start the online school layer

Tasks:

- student accounts
- student dashboard
- schedule visibility
- homework visibility
- performance and results visibility

Deliverable:

- first version of student-facing `Lexora Core`

### Phase 5: Lexora Mock MVP

Objective:

- launch a separate mock-test product for IELTS-style use

Tasks:

- create mock domain models
- create admin exam management
- create student exam-taking interface
- timed attempts
- answer persistence
- basic scoring and review

Deliverable:

- working `Lexora Mock` MVP

### Phase 6: Printed-to-digital ingestion workflow

Objective:

- allow developer-only upload of printed test materials and AI-assisted conversion

Tasks:

- admin-only upload page
- source document storage
- OCR pipeline
- AI structuring into exam draft
- manual review screen
- publish to live exam

Deliverable:

- developer-only ingestion and publishing pipeline

### Phase 7: Full online school expansion

Objective:

- evolve from admin system into complete online school

Tasks:

- live courses
- structured lesson content
- parent portal
- advanced analytics
- messaging/notifications
- subscriptions/payments expansion

Deliverable:

- broader `Lexora` ecosystem

## 13. Lexora Mock: Specific Functional Design

### 13.1 Product rules

- only developer/admin can upload and publish tests
- students can only access published tests assigned to them or made globally available
- exam layout should be close to IELTS digital experience
- source printed materials must remain editable before publication

### 13.2 Mock workflow

1. Admin uploads scanned test or PDF
2. System stores source document
3. OCR extracts raw text
4. AI structures content into sections/questions/options/instructions
5. Admin reviews and corrects draft
6. Admin publishes exam
7. Students take exam online
8. System stores attempt and generates review data

### 13.3 MVP exam types

Initial focus:

- Reading
- Listening
- Writing task upload / response box

Later:

- Speaking scheduling / rubric workflows

## 14. Recommended First Implementation Slice

The safest first implementation slice is:

1. create project documentation and target plan
2. rebrand the current platform to `Lexora`
3. introduce config and environment safety
4. start auth/user model refactor

Why this slice:

- it creates visible progress
- it reduces migration risk
- it prepares the system for real deployment
- it does not yet over-commit to the most complex student-side product flows

## 15. Immediate Backlog After ADS Approval

### Sprint A

- add app config module
- rename UI branding to `Lexora`
- rename startup messages/scripts
- prepare database naming migration path
- remove hardcoded secret key and default auth weakness

### Sprint B

- create users/roles schema
- create first super admin account
- migrate login to real users
- protect routes by role

### Sprint C

- add production settings
- PostgreSQL compatibility
- deployment files
- backup strategy update

### Sprint D

- design and implement `Lexora Mock` data model
- create admin exam builder and publication workflow

## 16. Decisions Proposed For Approval

These are the recommended baseline decisions unless changed:

- keep FastAPI as backend foundation
- keep Jinja temporarily for admin speed
- use PostgreSQL for production
- keep one repository with modular domains
- make `Lexora` the umbrella brand
- make `Lexora Mock` the exam-focused child product
- build developer-only ingestion workflow before opening test publishing to others

## 17. Success Criteria

The transformation is successful when:

- `Lexora` is reachable online 24/7
- you have a secure developer/admin account
- students can log in to their own area
- the platform supports real production hosting
- mock tests can be uploaded, digitized, reviewed, and published
- students can take IELTS-style mock exams online

## 18. Working Rule For Next Steps

Implementation should proceed in this exact order:

1. ADS approval
2. Rebrand + config hardening
3. Authentication redesign
4. Production deployment foundation
5. Lexora Mock MVP
6. Printed-to-digital ingestion
7. Student portal expansion
