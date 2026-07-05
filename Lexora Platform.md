
## Product Requirements Document (PRD)

Version: 1.0

Author: Jamshid Mahkamov

---

# Chapter 1

# Vision & Product Philosophy

---

# 1.1 Product Vision

Lexora is a modern educational ecosystem designed to help independent teachers, educational centers, and students manage every stage of the learning process from a single platform.

The platform is not intended to become another Learning Management System (LMS). Instead, it aims to combine education management, classroom administration, AI-powered assessment, and realistic computer-based examinations into one unified ecosystem.

The primary objective is to eliminate the need for teachers and students to use multiple disconnected services.

Every educational activity—from attendance tracking to IELTS mock examinations—should be performed inside Lexora.

The platform must feel professional, reliable, scalable, and intuitive.

Every feature added to the platform must contribute to this vision.

---

# 1.2 Core Mission

The mission of Lexora is to provide teachers with complete control over their educational business while giving students a seamless digital learning experience that closely resembles modern international educational platforms.

The platform should reduce administrative work, improve learning quality, automate repetitive processes using Artificial Intelligence, and increase trust between teachers and students.

---

# 1.3 Long-Term Vision

Lexora is designed as a long-term educational ecosystem.

The initial release focuses on:

• Teacher Management
• Student Management
• Attendance
• Homework
• IELTS Mock Tests

Future versions may include:

• Online School
• Live Lessons
• Video Courses
• Marketplace for Teachers
• AI Tutors
• Digital Certificates
• Mobile Applications
• Corporate Learning
• University Modules

Every architectural decision made today must allow these future modules to be integrated without rebuilding the platform.

---

# 1.4 Product Philosophy

Lexora follows six fundamental principles.

---

## Principle 1

The platform is built for teachers first.

Every workflow should minimize the amount of manual administrative work.

Teachers should spend more time teaching and less time managing spreadsheets, documents, and messaging applications.

---

## Principle 2

Students should feel like they are using a professional educational platform.

Every interaction should increase confidence.

Nothing should appear experimental, unfinished, or confusing.

---

## Principle 3

Artificial Intelligence assists people.

Artificial Intelligence never replaces human control.

Every AI-generated result must be editable by the platform owner before publication.

Every AI evaluation must remain transparent.

Whenever possible, users should understand why a particular result was produced.

---

## Principle 4

Professionalism over decoration.

Visual simplicity is preferred over unnecessary animations.

Every interface element must have a purpose.

No component should exist only because it looks attractive.

---

## Principle 5

Scalability from the beginning.

Although the first version targets independent teachers, every module should be designed as if thousands of users may eventually use the platform simultaneously.

No architectural decision should prevent future scaling.

---

## Principle 6

Consistency.

Every module inside Lexora must follow the same interaction patterns.

Buttons.

Forms.

Navigation.

Dialogs.

Notifications.

Search.

Filtering.

Tables.

Everything should behave consistently throughout the entire platform.

Users should never need to "learn" a different interface inside another module.

---

# 1.5 Product Objectives

The platform must achieve the following objectives.

1.
Become the primary management system for independent English teachers.

2.
Provide one of the most realistic IELTS Computer-Based Mock Test experiences available.

3.
Reduce teacher administration time by automating repetitive tasks.

4.
Allow students to track their own learning progress independently.

5.
Provide AI-assisted assessment while preserving the possibility of professional teacher review.

6.
Support gradual expansion into a complete online educational ecosystem.

---

# 1.6 Success Indicators

The platform should be considered successful when:

• Teachers can manage all students without external spreadsheets.

• Students can complete realistic mock examinations without technical difficulties.

• AI can accurately convert printed IELTS materials into editable digital examinations.

• Teachers can publish complete mock examinations in minutes rather than hours.

• Students trust AI feedback and teacher feedback equally.

• The platform is stable enough to support continuous daily educational operations.

---

# 1.7 Design Philosophy

The platform should never feel like an academic project.

It should feel like commercial educational software.

Every page should communicate professionalism.

Every action should require the minimum number of clicks.

Every important action should provide immediate feedback.

Every potentially destructive action must require confirmation.

The interface should remain clean regardless of future feature expansion.

Complexity should exist inside the system architecture—not inside the user experience.

---

# 1.8 AI-First Development Principles

Every future AI implementation inside Lexora must follow these rules.

AI generates.

Humans approve.

AI assists.

Humans control.

AI recommends.

Humans decide.

AI accelerates.

Humans remain responsible.

These principles apply to:

• OCR
• Mock Generation
• Writing Assessment
• Speaking Assessment
• Analytics
• Recommendations
• Reports

without exception.

---

# End of Chapter 1

# Chapter 2

# System Architecture

---

# 2.1 Architecture Philosophy

Lexora shall be designed as a modular platform.

Every major feature must exist as an independent module that communicates with the rest of the platform through clearly defined services.

No module should directly depend on the internal implementation of another module.

Every module must be replaceable, expandable, or temporarily disabled without affecting the stability of the entire platform.

The architecture must prioritize maintainability, scalability, and long-term development rather than short-term implementation speed.

---

# 2.2 Platform Structure

The platform consists of multiple Core Modules.

These modules together form one unified ecosystem.

Core Modules:

• Authentication
• User Management
• Student Management
• Teacher Management
• Class Management
• Attendance
• Homework
• Learning Materials
• Payments
• Mock Examination System
• AI Services
• Notifications
• Analytics
• Settings
• File Storage

Future modules shall be integrated without changing the existing architecture.

---

# 2.3 System Hierarchy

Lexora Platform

│

├── Authentication

├── User Profiles

├── Dashboard

│

├── Teacher Management

├── Student Management

├── Classes

├── Attendance

├── Homework

├── Materials

│

├── Mock Examination System

│       ├── Mock Builder
│       ├── Mock Library
│       ├── Test Engine
│       ├── Submission Engine
│       ├── Assessment Engine
│       ├── Results
│

├── AI Engine

│       ├── OCR
│       ├── PDF Parser
│       ├── Mock Generator
│       ├── Writing Evaluation
│       ├── Speaking Evaluation
│

├── Analytics

├── Notifications

├── Settings

└── Storage

---

# 2.4 Independent Modules

Every module shall own:

its own pages

its own services

its own API

its own database models

its own permissions

its own validation

Modules must communicate through shared platform services rather than direct coupling.

---

# 2.5 Single Source of Truth

Every important entity must exist only once.

Examples:

One Student Profile

One Teacher Profile

One Mock Object

One Submission

One Result

One Review

Duplicate records are prohibited unless explicitly versioned.

---

# 2.6 Platform Layers

The platform shall follow a layered architecture.

Presentation Layer

↓

Application Layer

↓

Business Logic Layer

↓

AI Services Layer

↓

Database Layer

↓

Storage Layer

No user interface component shall directly access the database.

Every operation must pass through business logic.

---

# 2.7 Platform Services

Core services include:

Authentication Service

Authorization Service

Notification Service

Storage Service

AI Service

Assessment Service

Search Service

Logging Service

Analytics Service

Audit Service

Every service must be reusable across modules.

---

# 2.8 Global Objects

The following objects are considered platform-wide entities.

User

Teacher

Student

Class

Lesson

Homework

Attendance Record

Material

Mock Test

Section

Question

Answer

Submission

Review

Result

Notification

Media File

Each object shall have:

Unique Identifier

Creation Date

Last Update Date

Owner

Status

Version

Audit History

---

# 2.9 Platform States

Every object must have a lifecycle.

Example:

Draft

↓

Ready

↓

Published

↓

Active

↓

Completed

↓

Archived

↓

Deleted

Objects shall never skip required lifecycle stages.

---

# 2.10 Version Control

Every critical educational resource must support versioning.

Including:

Mock Tests

Reading Passages

Listening Scripts

Writing Tasks

Speaking Questions

Assessment Rubrics

AI Prompts

Published versions cannot be modified directly.

Any modification creates a new version.

---

# 2.11 Global Search

The platform shall include one centralized search engine.

Users should be able to search:

Students

Teachers

Classes

Mocks

Homework

Files

Results

Messages

Search must support:

Partial matching

Filtering

Sorting

Pagination

Future semantic AI search

---

# 2.12 File Storage

The storage system shall support:

PDF

Audio

Video

Images

Documents

Generated Reports

Student Recordings

OCR Files

Temporary Files

Every uploaded file shall receive:

Unique ID

Owner

Upload Date

Security Permissions

Storage Location

Usage Reference

Unused files shall be automatically detected.

---

# 2.13 Background Jobs

Certain operations shall never execute directly inside the user interface.

Examples:

OCR

AI Evaluation

Large PDF Processing

Report Generation

Email Sending

Backup

Analytics Calculation

These operations shall execute asynchronously.

Users shall receive progress indicators.

---

# 2.14 Logging

Every critical action shall generate a system log.

Examples:

User Login

Logout

Student Creation

Mock Publication

Mock Deletion

Result Publication

Teacher Review

AI Assessment

Permission Change

Logs must never be editable.

---

# 2.15 Audit Trail

Every educational action must be traceable.

The platform shall always know:

Who created it.

Who modified it.

When it was modified.

What changed.

Why it changed (optional comment).

Audit history must be available only to authorized users.

---

# 2.16 Notifications

Notifications shall be event-driven.

Examples:

Homework Assigned

Mock Published

Writing Checked

Teacher Accepted Review

AI Finished Evaluation

Payment Received

Class Rescheduled

Notifications shall support:

In-App

Email

Future Push Notifications

---

# 2.17 Platform Scalability

The architecture shall support:

10 users

100 users

1,000 users

10,000 users

without requiring redesign.

Scaling shall occur through infrastructure improvements rather than architectural changes.

---

# 2.18 AI Integration Principles

Artificial Intelligence shall never modify permanent educational data without confirmation.

AI may:

Generate

Recommend

Evaluate

Analyze

Summarize

Extract

Convert

AI shall never:

Delete educational records.

Publish examinations automatically.

Overwrite manual teacher work.

Change grades without authorization.

---

# 2.19 Error Recovery

Every critical operation must support recovery.

Examples:

Internet disconnected

Browser closed

Power outage

Server restart

Timeout

OCR failure

AI failure

Database interruption

Users should lose as little progress as possible.

---

# 2.20 Future Expansion

The architecture must allow future integration of:

Online School

Video Lessons

Course Marketplace

Teacher Marketplace

Payment Gateway

Certificates

Mobile Applications

Public API

Corporate Portal

University Portal

without changing existing modules.

---

# End of Chapter 2

# Chapter 3

# User Roles & Permission System

---

# 3.1 Purpose

The User Role & Permission System defines every type of user that can access the Lexora platform.

Its purpose is to ensure that every user only has access to the information and functionality required for their responsibilities.

The permission system must be secure, scalable, and flexible enough to support future expansion without requiring architectural changes.

The platform shall implement Role-Based Access Control (RBAC) with optional Permission Policies for advanced customization.

---

# 3.2 Core Principles

The permission system follows these principles:

• Least Privilege Principle
Every user receives only the permissions required to perform their role.

• Separation of Responsibilities
Administrative actions must remain separated from educational actions.

• Owner Control
The Owner always has complete authority over the platform.

• Explicit Permissions
Every action must be allowed intentionally rather than implicitly.

• Secure by Default
New users receive the minimum required permissions.

---

# 3.3 Platform Roles

The platform currently defines the following roles.

Owner (Developer)

Platform Administrator (Future)

Teacher

Public Teacher

Student

Future Roles

Parent

Moderator

Support Agent

AI Service Account

---

# 3.4 Owner

The Owner is the creator and ultimate controller of the platform.

There can only be one Owner account.

The Owner account cannot be deleted.

The Owner account cannot lose Owner permissions.

The Owner account always has unrestricted access to every module.

---

## Owner Permissions

The Owner can:

Create any user

Delete any user

Suspend accounts

Reset passwords

View every student's information

View every teacher's information

View every class

View every mock examination

Create mock tests

Edit mock tests

Delete mock tests

Publish mock tests

Archive mock tests

Restore mock tests

Configure AI

Modify OCR settings

Modify platform settings

Manage storage

Manage announcements

Manage notifications

Access audit logs

View analytics

Manage subscriptions

Manage payment settings

Manage teacher verification

Manage public teacher directory

Manage feature flags

Manage future modules

Manage API keys

Manage backups

Restore backups

Export data

Import data

View system health

View background jobs

Restart failed AI tasks

Access developer tools

Access hidden experimental features

---

## Owner Restrictions

None.

The Owner is the highest authority inside the platform.

---

# 3.5 Platform Administrator (Future)

The Platform Administrator is a trusted employee who helps manage the platform.

Unlike the Owner, administrators do not own the platform.

Administrators can only access permissions granted by the Owner.

Administrators cannot:

Delete the Owner

Transfer ownership

Access developer-only configuration

Modify billing ownership

Manage deployment settings

Delete audit logs

---

# 3.6 Teacher

Teachers represent educational professionals using the platform.

Teachers may be independent or connected to the platform owner.

Each teacher owns their own educational workspace.

---

## Teacher Permissions

Teachers may:

Create classes

Invite students

Manage students

Take attendance

Assign homework

Upload learning materials

Create private mock sessions

Review student work

Evaluate Writing

Evaluate Speaking

Publish grades

Send announcements

View student progress

Generate reports

Manage class settings

Communicate with students

---

## Teacher Restrictions

Teachers cannot:

Modify platform configuration

Delete platform data

View private classes owned by other teachers

Modify AI settings

Modify OCR

Publish public examinations without permission

Delete audit history

Access developer tools

---

# 3.7 Public Teacher

A Public Teacher is a verified teacher who has voluntarily enabled public review services.

Public Teachers may receive Writing and Speaking submissions from students who are not enrolled in their classes.

---

## Additional Public Teacher Permissions

Receive public review requests

Accept or reject review requests

Set availability schedule

Set review prices (future)

Define expected completion time

Pause public availability

Manage review queue

---

# 3.8 Student

Students are the primary users of the educational platform.

Students may belong to one or multiple teachers.

Students never receive administrative permissions.

---

## Student Permissions

Students may:

Join classes

View homework

Submit homework

Take mock examinations

View learning materials

Receive notifications

Track progress

View results

Book reviews

Choose AI assessment

Choose Teacher assessment

Upload assignments

Record Speaking answers

Write essays

View certificates (future)

Manage profile

---

## Student Restrictions

Students cannot:

Edit published examinations

Access other students

Modify grades

View teacher analytics

Delete educational records

Modify AI settings

Publish educational content

Manage platform settings

---

# 3.9 Parent (Future)

Parents may monitor their children's educational progress.

Parents cannot modify educational content.

Parents have read-only access.

---

# 3.10 AI Service Account

Artificial Intelligence operates as an internal system account.

The AI account never logs into the platform through the normal login system.

Its actions are always recorded.

Every AI-generated action is traceable.

---

## AI Permissions

Read OCR documents

Generate digital examinations

Evaluate essays

Evaluate speaking recordings

Generate feedback

Generate analytics

Recommend improvements

Never publish automatically.

Never delete educational content.

Never overwrite teacher feedback.

---

# 3.11 Permission Categories

Permissions are grouped into categories.

User Management

Student Management

Teacher Management

Class Management

Attendance

Homework

Materials

Mock Builder

Mock Library

Assessment

Analytics

Notifications

Storage

AI

Administration

Developer

Billing

Security

---

# 3.12 Sensitive Operations

Certain operations always require confirmation.

Delete Mock

Delete Student

Delete Teacher

Delete Class

Reset Password

Publish Mock

Archive Mock

Restore Mock

Transfer Ownership

Delete Storage Files

Mass Import

Mass Export

AI Bulk Processing

---

# 3.13 Ownership Rules

Every educational object must have an owner.

Examples:

Teacher owns Class

Teacher owns Homework

Teacher owns Materials

Owner owns Platform Settings

Student owns Submission

AI owns AI Evaluation

No object shall exist without ownership.

---

# 3.14 Future Permission Policies

The system should support custom permissions.

Example:

Teacher A

✓ Can publish mocks

✗ Cannot delete mocks

Teacher B

✓ Can review essays

✓ Can review speaking

✗ Cannot create classes

This should be configurable without modifying source code.

---

# 3.15 Security Rules

Permissions are validated on both:

Frontend

Backend

Frontend validation improves user experience.

Backend validation guarantees security.

Backend validation is always the source of truth.

---

# 3.16 Permission Inheritance

Higher roles inherit permissions from lower roles unless explicitly restricted.

Owner

↓

Administrator

↓

Teacher

↓

Student

Permission inheritance must remain predictable and documented.

---

# 3.17 Role Expansion

Future platform versions must support additional educational roles without modifying existing permission architecture.

New roles should be created through configuration whenever possible.

---

# End of Chapter 3
# Chapter 4

# Owner Workspace

---

# 4.1 Purpose

The Owner Workspace is the primary control center of the entire Lexora platform.

Unlike a traditional dashboard that only displays statistics, the Owner Workspace functions as an operational command center.

Every important activity occurring inside the platform should either be directly manageable from this workspace or be accessible within one click.

The Owner should never need to search for important information.

The system should proactively surface critical events, pending tasks, AI operations, platform health, and educational insights.

The Owner Workspace is designed to answer one question immediately after login:

> "What requires my attention right now?"

---

# 4.2 Design Philosophy

The Owner Workspace should feel like a modern operating system rather than an admin panel.

Information must be organized by priority.

The interface should remain clean while displaying a large amount of information.

The workspace should support both beginner and power users.

Frequently used actions must always remain visible.

Rarely used administrative settings should remain hidden until needed.

---

# 4.3 Workspace Layout

The Owner Workspace consists of six primary zones.

Zone A

Global Navigation

Zone B

Quick Actions

Zone C

Platform Overview

Zone D

Today's Activity

Zone E

Pending Tasks

Zone F

System Monitoring

Each zone should remain independently configurable in future versions.

---

# 4.4 Global Navigation

The navigation menu must provide access to every major module.

Dashboard

Students

Teachers

Classes

Attendance

Homework

Materials

Mock Builder

Mock Library

Results

AI Processing

Storage

Analytics

Notifications

Platform Settings

System Logs

Developer Tools

Future Modules

Navigation should support:

Collapsible mode

Search

Favorites

Recent Pages

Pinned Modules

---

# 4.5 Dashboard Overview

Immediately after login the Owner should see:

Total Students

Active Students Today

Teachers

Today's Classes

Upcoming Lessons

Homework Pending

Active Mock Tests

Draft Mock Tests

Published Mock Tests

AI Jobs Running

Pending Reviews

Unread Notifications

Platform Status

Storage Usage

Weekly Growth

Monthly Activity

Server Health

Latest Backups

No scrolling should be required to view the most important platform information.

---

# 4.6 Quick Actions

Quick Actions allow the Owner to perform common operations instantly.

Create Student

Create Teacher

Create Class

Upload Materials

Create Homework

Create Mock

Upload PDF

Publish Mock

Open AI Processing

Review Writing

Review Speaking

Export Reports

Open Analytics

Restart Failed AI Jobs

Each action should require no more than two clicks.

---

# 4.7 Live Activity Feed

The workspace must include a real-time activity feed.

Examples:

Student joined class

Homework submitted

Mock completed

Essay submitted

Speaking uploaded

Teacher accepted review

AI finished OCR

AI generated mock

Mock published

Teacher created lesson

Student completed reading section

Student abandoned mock

Payment received (future)

Every event should include:

Timestamp

User

Action

Related Object

Quick View

---

# 4.8 Platform Health

The Owner should always know whether the platform is operating correctly.

Display:

API Status

Database Status

AI Service Status

OCR Status

Storage Status

Authentication Status

Email Status

Notification Status

Background Jobs

Queue Length

Average AI Processing Time

Average Response Time

System Uptime

Any failures should immediately appear as alerts.

---

# 4.9 AI Processing Center

One of the most important widgets.

Displays:

Running OCR

Pending OCR

Failed OCR

Writing Evaluations

Speaking Evaluations

Queued AI Jobs

Average Processing Time

Estimated Completion Time

Owner should be able to:

Retry

Cancel

Restart

Approve

Reject

View Details

---

# 4.10 Pending Tasks

The platform should automatically detect unfinished work.

Examples:

Mocks waiting publication

OCR waiting correction

Writing waiting review

Speaking waiting review

Teachers waiting approval

Students waiting verification

Storage cleanup recommended

Expired mock tests

Failed AI jobs

Backup required

The Owner should never manually search for unfinished work.

---

# 4.11 Smart Recommendations

Lexora should actively assist the Owner.

Examples:

12 students have not completed homework.

3 mock tests are still unpublished.

5 essays have waited more than 24 hours.

Storage usage exceeded 80%.

Speaking reviews are delayed.

Teacher response time decreased.

Weekly attendance dropped.

Student engagement decreased.

Recommendations should be generated automatically.

---

# 4.12 Calendar Widget

The workspace includes an educational calendar.

Display:

Today's Classes

Upcoming Lessons

Mock Sessions

Teacher Reviews

Deadlines

Events

Future Meetings

The calendar should support:

Day

Week

Month

Agenda

---

# 4.13 Notification Center

Notifications should be categorized.

Educational

System

AI

Security

Payments

Updates

Announcements

Critical alerts must remain pinned until acknowledged.

---

# 4.14 Global Search

The Owner can search everything from one place.

Search includes:

Students

Teachers

Classes

Mocks

Questions

Writing

Speaking

Files

Notifications

Logs

AI Jobs

Typing should immediately display suggestions.

---

# 4.15 Developer Tools

Only visible to the Owner.

Includes:

Feature Flags

Debug Console

AI Prompt Manager

OCR Configuration

Queue Management

Background Jobs

Database Inspector

API Monitor

Cache Manager

Experimental Features

These tools must never be accessible to Teachers or Students.

---

# 4.16 Workspace Personalization

The Owner may customize:

Dashboard Layout

Widget Order

Pinned Widgets

Favorite Pages

Color Theme

Language

Notification Preferences

Sidebar Position

Compact Mode

---

# 4.17 Performance Requirements

Dashboard should load in under 2 seconds.

Statistics should update automatically.

Heavy analytics should load asynchronously.

Widgets should continue working independently if another widget fails.

---

# 4.18 Error Handling

If any widget fails:

Display clear error message.

Allow retry.

Do not crash the entire dashboard.

Every widget must be isolated.

---

# 4.19 Future Expansion

The Owner Workspace should support future widgets without redesign.

Examples:

Financial Dashboard

Marketplace Statistics

Certificate Generation

Teacher Rankings

AI Tutor Monitoring

Course Sales

Franchise Management

Corporate Clients

---

# 4.20 Success Criteria

The Owner should be able to understand the entire state of the business within 30 seconds of opening the dashboard.

Every important action should be reachable within three clicks.

No critical information should ever remain hidden.

The Owner Workspace must become the operational brain of the Lexora ecosystem.

---

# End of Chapter 4
# Chapter 5

# Mock Examination System Overview

---

# 5.1 Purpose

The Mock Examination System is the core feature of the Lexora platform.

Its purpose is to allow the platform owner to convert printed IELTS examination materials into professional computer-delivered mock examinations that closely replicate the real IELTS testing experience.

The system must support the complete lifecycle of every examination—from PDF upload to student performance analytics.

Unlike traditional LMS systems that simply upload PDF files, Lexora transforms examination materials into structured, interactive digital assessments.

---

# 5.2 Core Philosophy

A Mock Test is not a PDF.

A Mock Test is not a list of questions.

A Mock Test is not a webpage.

A Mock Test is a structured educational object.

Every examination contains:

Metadata

Sections

Instructions

Questions

Answer Rules

Time Limits

Evaluation Logic

Media

Scoring Rules

Version History

Analytics

Review History

Publication Status

Every component must exist independently while remaining connected to the parent Mock Test.

---

# 5.3 Examination Lifecycle

Every Mock Test shall follow the same lifecycle.

STEP 1

Material Acquisition

↓

STEP 2

Owner Upload

↓

STEP 3

AI OCR Processing

↓

STEP 4

AI Structure Recognition

↓

STEP 5

Question Extraction

↓

STEP 6

Digital Mock Generation

↓

STEP 7

Owner Validation

↓

STEP 8

Manual Editing

↓

STEP 9

Preview

↓

STEP 10

Publication

↓

STEP 11

Student Assignment

↓

STEP 12

Mock Session

↓

STEP 13

Submission

↓

STEP 14

Evaluation

↓

STEP 15

Result Publication

↓

STEP 16

Analytics

↓

STEP 17

Archive

No examination shall skip any mandatory stage.

---

# 5.4 Examination Types

The platform shall support multiple examination types.

Initially:

IELTS Academic

IELTS General Training

Future:

TOEFL

CEFR Placement

SAT English

Cambridge Exams

University Entrance Exams

Custom Teacher Exams

The architecture must not depend on IELTS-specific logic.

IELTS is the first implementation, not the only implementation.

---

# 5.5 Mock Object Structure

Each Mock Test consists of:

General Information

Listening Section

Reading Section

Writing Section

Speaking Section

Answer Key

Assessment Rules

Band Descriptors

Audio Files

Images

PDF Source

Generated Assets

Publication Settings

Version Information

Analytics

History

Every component shall remain independently editable.

---

# 5.6 Examination Metadata

Every Mock Test shall include:

Unique ID

Title

Official Test Name

Exam Type

Academic / General

Difficulty

Estimated Band Level

Publication Status

Author

Creation Date

Last Modification Date

Version Number

Language

Description

Estimated Completion Time

Estimated AI Processing Time

Source Files

---

# 5.7 Publication States

Each Mock Test may exist in one of the following states.

Draft

↓

AI Processing

↓

Requires Review

↓

Ready for Preview

↓

Approved

↓

Published

↓

Hidden

↓

Archived

↓

Deleted

Students may only access Published examinations.

---

# 5.8 Examination Components

The examination consists of four independent modules.

Listening

Reading

Writing

Speaking

Each module may be published independently.

Each module maintains its own validation rules.

Each module has its own timer.

Each module stores its own submissions.

---

# 5.9 Question Objects

Every question is stored independently.

Question Object contains:

Question Number

Question Type

Section

Instructions

Question Text

Possible Answers (if applicable)

Correct Answers

Accepted Variations

Media References

Marks

Validation Rules

Explanation

Difficulty

AI Confidence Score

Manual Verification Status

Questions are never stored as plain text blobs.

---

# 5.10 Supported Question Types

Initially supported:

Multiple Choice

Multiple Selection

Sentence Completion

Short Answer

Summary Completion

Diagram Labelling

Table Completion

Flow Chart Completion

Map Labelling

Matching

True / False / Not Given

Yes / No / Not Given

Matching Headings

Matching Information

Matching Features

Matching Sentence Endings

Paragraph Selection

Writing Task 1

Writing Task 2

Speaking Part 1

Speaking Part 2

Speaking Part 3

Future question types shall be supported without redesigning the database.

---

# 5.11 Media Objects

Every media file is stored independently.

Supported:

Audio

Images

PDF

SVG

Illustrations

Graphs

Maps

Tables

Icons

Future Video Support

Each media object shall include:

Owner

Version

Dimensions

Alternative Text

Compression Status

Optimization Status

Reference Count

---

# 5.12 Submission Object

Every examination attempt generates one Submission.

Submission contains:

Student

Mock

Started At

Completed At

Duration

Answers

Writing

Speaking

Flags

AI Status

Teacher Review Status

Overall Status

Device Information

Browser Information

Network Recovery Events

---

# 5.13 Assessment Object

Assessment contains:

Listening Score

Reading Score

Writing Band

Speaking Band

Overall Band

AI Feedback

Teacher Feedback

Criterion Scores

Comments

Improvement Suggestions

Assessment History

Appeal Status

---

# 5.14 Mock Library

All published and unpublished examinations are stored inside the Mock Library.

Library supports:

Search

Filtering

Sorting

Folders

Tags

Difficulty Levels

Publication Status

Versions

Duplicate Detection

Import

Export

Archive

Restore

---

# 5.15 Security

Students never access draft examinations.

Students never access answer keys.

Teachers only access examinations assigned to them.

Only the Owner may permanently delete examinations.

Every examination modification generates an audit log.

---

# 5.16 Performance Requirements

Opening a published examination shall require less than two seconds.

Large PDFs must process asynchronously.

AI processing shall never block the user interface.

Preview generation should complete automatically.

The system should support hundreds of examinations without performance degradation.

---

# 5.17 Future Expansion

Future versions may include:

Shared Mock Marketplace

Teacher Marketplace

Community Examinations

Official Cambridge Collections

Exam Recommendations

Adaptive Testing

Difficulty Prediction

Personalized Mock Generation

AI-generated Practice Tests

Voice-Controlled Speaking Tests

---

# 5.18 Success Criteria

The Owner should be able to transform a printed IELTS examination into a professional digital mock examination with minimal manual work.

Students should experience an examination environment that feels authentic, reliable, and indistinguishable from a professional computer-delivered language examination.

The Mock Examination System shall become the defining feature of the Lexora platform.

---

# End of Chapter 5
# Chapter 6

# Mock Builder Workspace

---

# 6.1 Purpose

The Mock Builder is the content creation environment of the Lexora platform.

Its purpose is to transform traditional paper-based examinations into fully interactive digital examinations that replicate professional computer-delivered testing.

The Mock Builder is not a form.

It is not a PDF uploader.

It is not an editor.

It is a complete examination production environment.

Every examination published on the platform must be created, reviewed, validated, and approved through the Mock Builder.

No examination should bypass this workflow.

---

# 6.2 Design Philosophy

The Builder should feel similar to professional software such as:

Adobe Acrobat

Figma

Notion

Visual Studio Code

rather than a traditional educational website.

The interface must prioritize productivity.

The Owner should spend time reviewing content—not fighting the interface.

Every frequently used action should require the fewest possible clicks.

The Builder should support keyboard shortcuts, drag-and-drop interactions, autosave, and undo/redo.

---

# 6.3 Primary Objectives

The Builder must allow the Owner to:

• Upload printed examinations.

• Process them using AI.

• Review every AI-generated object.

• Correct AI mistakes.

• Preview the examination.

• Publish the examination.

• Maintain version history.

• Reuse existing questions.

• Manage examination assets.

---

# 6.4 Builder Workflow

Every examination follows the same creation pipeline.

Create New Mock

↓

Upload Files

↓

AI OCR

↓

AI Structure Recognition

↓

Question Extraction

↓

Media Detection

↓

Digital Object Generation

↓

Owner Review

↓

Corrections

↓

Preview

↓

Validation

↓

Publication

---

# 6.5 Workspace Layout

The Builder should consist of six permanent panels.

---------------------------------------------------

Navigation Panel

↓

Document Explorer

↓

Main Editing Area

↓

Properties Panel

↓

Validation Panel

↓

AI Assistant Panel

---------------------------------------------------

Every panel must be independently resizable.

The layout should be remembered between sessions.

---

# 6.6 Navigation Panel

Displays:

Dashboard

Mock Library

Drafts

Published Mocks

Archived Mocks

Templates

Media Library

AI Processing

Trash

Search

Recent Files

Favorites

---

# 6.7 Mock Explorer

Every examination appears as a tree structure.

Example:

IELTS Academic Test 18

▼ Listening

Section 1

Questions 1–10

Section 2

Questions 11–20

Section 3

Questions 21–30

Section 4

Questions 31–40

▼ Reading

Passage 1

Questions

Passage 2

Questions

Passage 3

Questions

▼ Writing

Task 1

Task 2

▼ Speaking

Part 1

Part 2

Part 3

The Owner should instantly navigate to any object.

---

# 6.8 Main Editing Area

This is the primary workspace.

Depending on the selected object it displays:

Question Editor

Reading Passage Editor

Writing Task Editor

Speaking Editor

Audio Timeline

Image Editor

Instructions Editor

Metadata Editor

The editing experience should remain consistent.

---

# 6.9 Properties Panel

Every selected object exposes editable properties.

Examples:

Question Number

Question Type

Marks

Accepted Answers

Time Limit

Instructions

Difficulty

Section

Band Level

Visibility

AI Confidence

Status

Media

Notes

Tags

No property should require opening a separate page.

---

# 6.10 AI Assistant Panel

The AI Assistant should remain visible throughout the editing process.

Capabilities include:

Explain OCR uncertainty

Suggest corrections

Rewrite instructions

Improve formatting

Detect numbering errors

Detect duplicated questions

Detect missing questions

Detect answer inconsistencies

Summarize imported material

Generate missing metadata

Highlight low-confidence OCR

The AI Assistant never modifies content automatically.

Every suggestion requires Owner approval.

---

# 6.11 Validation Center

Before publication every examination must pass validation.

Validation includes:

Missing Questions

Incorrect Numbering

Broken Images

Broken Audio

Missing Instructions

Missing Correct Answers

Invalid Timer

Incorrect Section Count

Duplicate IDs

OCR Errors

Unsupported Question Types

Missing Metadata

Every issue receives a severity level:

Critical

Warning

Suggestion

Publication is blocked until all Critical issues are resolved.

---

# 6.12 Draft Management

Every examination exists as a Draft until publication.

Drafts support:

Autosave

Version History

Comments

Internal Notes

Recovery

Duplicate

Restore

Archive

---

# 6.13 Version Control

Every save creates a recoverable version.

The Owner may:

Compare versions

Restore previous versions

Duplicate versions

Label milestones

Publish specific versions

View change history

No published examination may be edited directly.

Editing creates a new Draft Version.

---

# 6.14 Autosave

The Builder automatically saves changes.

Autosave triggers:

Every 10 seconds

After every structural modification

Before AI processing

Before Preview

Before Publication

Users should never lose work.

---

# 6.15 Undo / Redo

The Builder supports unlimited Undo and Redo within the current editing session.

Actions include:

Question Editing

Deletion

Movement

Formatting

Media Replacement

AI Suggestions

Metadata Changes

Section Reordering

---

# 6.16 Preview Mode

Preview displays the examination exactly as students will see it.

Preview must simulate:

Desktop

Tablet

Mobile (future)

Listening Experience

Reading Layout

Writing Editor

Speaking Recorder

Timers

Navigation

Validation

The Owner should experience the examination before publication.

---

# 6.17 Collaboration (Future)

Future versions may support multiple editors.

Capabilities:

Live Editing

Comments

Suggestions

Approval Workflow

Conflict Resolution

Review Requests

---

# 6.18 Performance Requirements

Opening a Builder project should require less than two seconds.

Editing must remain responsive regardless of examination size.

Large examinations should load progressively.

AI tasks should execute asynchronously.

Autosave must never interrupt editing.

---

# 6.19 Security

Only the Owner may publish examinations.

Teachers may receive edit permissions only if explicitly granted.

Students never access the Builder.

Every Builder action generates an Audit Log.

Deleted content remains recoverable until permanently removed.

---

# 6.20 Success Criteria

The Owner should be capable of creating a complete professional IELTS examination from a printed source with minimal manual effort.

The Builder should become the single production environment for every future examination published on Lexora.

Every interaction should reduce workload while maintaining complete human control over educational quality.

---

# End of Chapter 6
# Chapter 7

# Intelligent PDF Processing Pipeline

---

# 7.1 Purpose

The PDF Processing Pipeline is responsible for transforming printed examination materials into structured digital examination objects.

Unlike conventional OCR systems that only extract text, Lexora performs semantic document understanding.

The system must recognize:

• Examination structure

• Section hierarchy

• Question relationships

• Visual components

• Answer logic

• Timing rules

• Assessment metadata

The goal is not to digitize pages.

The goal is to reconstruct an interactive examination.

---

# 7.2 Design Philosophy

The uploaded PDF is treated as raw educational material.

It is NOT the final examination.

The digital examination is a completely new object created from understanding the source document.

Every extracted object must become editable.

Nothing should remain permanently locked inside the PDF.

---

# 7.3 Supported Input Formats

Initially supported:

PDF

High Resolution Images

Scanned Documents

ZIP Collections

PNG

JPEG

TIFF

Future Support:

DOCX

HTML

XML

Cambridge Digital Resources

---

# 7.4 Upload Workflow

Step 1

Owner clicks "Create Mock"

↓

Step 2

Owner chooses examination type.

Academic

General Training

Custom

↓

Step 3

Owner uploads files.

Listening PDF

Reading PDF

Writing PDF

Speaking PDF

Audio Files

Images

Answer Keys

Optional Metadata

↓

Step 4

Platform validates files.

↓

Step 5

Upload completes.

↓

AI Processing begins automatically.

---

# 7.5 File Validation

Immediately after upload the platform validates:

File integrity

Supported format

Page count

Encryption

Corruption

Resolution

Missing pages

Duplicate uploads

Maximum size

Unsupported objects

Invalid files must never enter the AI pipeline.

---

# 7.6 AI Processing Stages

The AI processes every uploaded document through multiple independent stages.

Stage 1

Document Classification

↓

Stage 2

Page Segmentation

↓

Stage 3

Layout Detection

↓

Stage 4

Text Recognition

↓

Stage 5

Visual Object Detection

↓

Stage 6

Question Detection

↓

Stage 7

Answer Extraction

↓

Stage 8

Relationship Mapping

↓

Stage 9

Digital Object Creation

↓

Stage 10

Confidence Analysis

↓

Stage 11

Owner Review Preparation

Each stage produces its own output.

Each stage can be independently rerun.

---

# 7.7 Document Classification

The AI determines:

Listening

Reading

Writing

Speaking

Answer Key

Instructions

Supplementary Material

Unknown

Incorrect classifications require manual confirmation.

---

# 7.8 Page Segmentation

Every page becomes an independent processing unit.

The AI identifies:

Margins

Columns

Headers

Footers

Page Numbers

Question Regions

Images

Tables

Maps

Diagrams

Answer Boxes

No page should remain a single image.

---

# 7.9 Layout Analysis

The AI reconstructs the document hierarchy.

Examples:

Title

↓

Instructions

↓

Section

↓

Question Group

↓

Question

↓

Answer Space

↓

Image

↓

Table

↓

Footnote

Every detected object receives coordinates.

---

# 7.10 Text Recognition

OCR extracts:

Instructions

Questions

Passages

Tables

Captions

Options

Labels

Headers

Footnotes

The AI should preserve formatting whenever possible.

Bold

Italic

Underline

Lists

Indentation

Special symbols

---

# 7.11 Visual Object Detection

The AI identifies:

Maps

Flowcharts

Diagrams

Tables

Graphs

Images

Icons

Boxes

Arrows

Highlight Areas

Every object becomes editable.

---

# 7.12 Question Detection

The AI identifies:

Question Numbers

Question Types

Question Boundaries

Instructions

Relationships

Subquestions

Answer Limits

Marks

Question numbering should never rely solely on OCR text.

The AI must understand logical structure.

---

# 7.13 Question Type Recognition

Supported types include:

Multiple Choice

Matching

Sentence Completion

Table Completion

Flowchart Completion

Map Labelling

Diagram Labelling

Summary Completion

True False Not Given

Yes No Not Given

Paragraph Matching

Heading Matching

Writing Tasks

Speaking Prompts

Unknown Types

Every detected type receives a confidence score.

---

# 7.14 Media Association

The AI links media with related questions.

Example:

Map

↓

Questions 14–19

Diagram

↓

Questions 27–30

Audio

↓

Listening Section 2

Images should never exist without references.

---

# 7.15 Answer Key Recognition

If answer keys exist,

the AI extracts:

Correct Answers

Alternative Answers

Accepted Variations

Capitalization Rules

Word Limits

Special Validation Rules

Answer Keys remain hidden from students.

---

# 7.16 Relationship Mapping

The AI reconstructs logical relationships.

Examples:

Section

contains

Question Groups

Question Group

contains

Questions

Question

references

Image

Question

references

Table

Question

references

Audio

These relationships form the digital examination.

---

# 7.17 Confidence Scoring

Every generated object receives a confidence score.

95–100%

Verified

90–95%

Very Reliable

80–90%

Needs Review

Below 80%

Manual Verification Required

Confidence is calculated independently for:

Text

Layout

Question Numbers

Question Types

Images

Answer Keys

Relationships

---

# 7.18 AI Warnings

The AI should automatically detect:

Missing Questions

Broken Numbering

Skipped Pages

Duplicated Questions

Unclear Images

Unreadable Text

Possible OCR Errors

Low Resolution

Missing Answer Keys

Incorrect Section Count

Warnings should be grouped by severity.

---

# 7.19 Manual Review Queue

Only uncertain objects should require manual review.

The Owner should not verify the entire examination.

Instead,

the Builder displays only:

Low Confidence Questions

Missing Objects

Potential Errors

Conflicts

This minimizes manual work.

---

# 7.20 Recovery

If AI processing fails,

the system should:

Save completed stages

Resume processing

Retry failed stages

Allow manual restart

Display meaningful diagnostics

The Owner should never restart from the beginning unless explicitly requested.

---

# 7.21 Success Criteria

After AI processing completes,

the Owner should receive a structured digital examination requiring only minimal manual corrections.

The objective is not perfect OCR.

The objective is near-zero manual reconstruction effort.

---

# End of Chapter 7
# Chapter 8

# Listening Engine

---

# 8.1 Purpose

The Listening Engine is responsible for delivering a professional computer-based IELTS Listening examination.

The objective is to recreate the experience of an official IELTS Computer Delivered Test while maintaining platform stability, fairness, accessibility, and accurate answer collection.

The Listening Engine is not an audio player.

It is a synchronized examination environment.

Audio playback, timer, navigation, answer recording, autosave, validation, and submission must function as one integrated system.

---

# 8.2 Design Philosophy

The Listening experience should immediately feel professional.

Students should forget they are using a learning platform.

They should feel like they are sitting inside an official examination center.

The interface should remain calm.

Minimal.

Distraction-free.

Fast.

No unnecessary animations.

No decorative elements.

Every UI component exists only because it helps complete the examination.

---

# 8.3 Examination Structure

Listening consists of:

Section 1

Questions 1–10

↓

Section 2

Questions 11–20

↓

Section 3

Questions 21–30

↓

Section 4

Questions 31–40

Each section is synchronized with a corresponding audio recording.

The platform must support future variations in the number of sections or questions.

---

# 8.4 Student Entry Flow

Student selects a Listening examination.

↓

Platform validates permissions.

↓

System checks browser compatibility.

↓

System verifies audio output.

↓

Student completes a short audio test.

↓

Instructions page is displayed.

↓

Student confirms readiness.

↓

Countdown begins.

↓

Listening session starts.

No audio should begin automatically before the student explicitly starts the examination.

---

# 8.5 Audio Verification

Before entering the examination the system performs an audio check.

The student must confirm:

Audio device works correctly.

Volume is appropriate.

Playback is clear.

If audio cannot be played,

the examination must not start.

---

# 8.6 Examination Interface

The screen is divided into functional regions.

Header

Timer

Audio Progress

Candidate Information

↓

Main Content Area

Instructions

Questions

Images

Tables

Maps

↓

Answer Panel

Input Fields

↓

Question Navigator

↓

Footer

Save Status

Connection Status

Submit Button

The layout should remain consistent throughout the examination.

---

# 8.7 Audio Player Rules

The audio player is controlled entirely by the examination engine.

Students cannot:

Pause

Restart

Rewind

Fast-forward

Download

Change playback speed

Mute the recording permanently

The platform controls playback automatically.

---

# 8.8 Audio Synchronization

Questions should become active as the recording progresses.

The current question group should be highlighted.

The current section should remain visible.

The system should automatically scroll only when necessary.

Students may manually navigate without interrupting audio playback.

---

# 8.9 Question Navigation

Students may freely navigate between answered and unanswered questions during the Listening session.

Navigation options:

Question Navigator

Previous

Next

Jump to Question

Flag for Review

Unanswered Filter

Navigation must never interrupt audio playback.

---

# 8.10 Answer Input

Supported input types include:

Text Input

Single Choice

Multiple Choice

Dropdown

Table Input

Map Labels

Diagram Labels

Each answer field must save automatically.

Students never manually save answers.

---

# 8.11 Autosave

Every answer must be saved automatically.

Triggers:

Typing

Selection Change

Every five seconds

Question Change

Audio Section Change

Network Recovery

The interface should continuously display:

Saved

Saving...

Offline

Syncing...

Students should never worry about losing work.

---

# 8.12 Timer

The timer is synchronized with examination rules.

The timer remains visible throughout the examination.

Visual behavior:

Normal

↓

Warning (10 minutes)

↓

Critical (5 minutes)

↓

Final Minute

↓

Automatic Submission

The timer cannot be hidden.

---

# 8.13 Review Screen

After audio finishes,

students receive a review period.

The system displays:

Answered Questions

Unanswered Questions

Flagged Questions

Question Summary

Navigation remains available.

Students may edit answers until time expires.

---

# 8.14 Submission

Submission occurs:

Automatically when time expires.

Or manually after confirmation.

Submission requires confirmation.

Once submitted,

the examination becomes read-only.

No further modifications are allowed.

---

# 8.15 Anti-Cheating

The Listening Engine should detect:

Multiple tabs

Window switching

Fullscreen exit (optional)

Clipboard usage

Developer Tools

Abnormal inactivity

Network interruptions

Suspicious rapid answering

Events should be logged.

The platform should not immediately terminate the examination unless configured by the Owner.

---

# 8.16 Network Recovery

If connection is lost:

Answers remain locally cached.

Timer continues.

Synchronization resumes automatically.

Students receive a notification.

If reconnection succeeds,

no work should be lost.

---

# 8.17 Accessibility

The Listening Engine should support:

Keyboard navigation

Screen scaling

High contrast mode

Accessible labels

Focus indicators

Color-independent notifications

Future screen-reader compatibility where appropriate.

---

# 8.18 AI Monitoring

The AI system may analyze:

Question difficulty

Average response time

Frequently skipped questions

Most incorrect answers

Common spelling mistakes

Student hesitation

These analytics are for teachers and the Owner only.

---

# 8.19 Performance Requirements

Initial loading:

<2 seconds

Question switching:

Instant

Autosave:

<300 ms

Audio synchronization:

No noticeable delay

The examination must remain responsive even on average internet connections.

---

# 8.20 Success Criteria

Students should complete the Listening examination without thinking about the platform itself.

The interface should disappear psychologically.

The only thing occupying the student's attention should be the examination.

The Listening Engine should faithfully reproduce the feeling of a professional computer-delivered language examination while ensuring reliability, fairness, and data integrity.

---

# Implementation Notes for AI Agents

The Listening Engine MUST be implemented as an independent module.

Audio playback, timer, answer storage, navigation, autosave, and submission MUST be separate services communicating through the examination engine.

Never couple UI components directly to the audio controller.

Every answer MUST exist independently from the user interface.

The system MUST support recovery after unexpected interruption.

Future examination types must be able to reuse this engine with different timing and navigation rules.

---

# End of Chapter 8
# Chapter 9

# Reading Engine

---

## Goal

The Reading Engine must accurately reproduce the official IELTS Computer Delivered Reading examination.

---

## Examination Structure

Academic

Passage 1

↓

Questions

↓

Passage 2

↓

Questions

↓

Passage 3

↓

Questions

General Training

Section 1

↓

Section 2

↓

Section 3

Platform must support both formats.

---

## Interface Layout

The screen is permanently divided into two panels.

LEFT PANEL

Reading Passage

Scrollable independently.

RIGHT PANEL

Questions

Answer fields

Navigator

Question Palette

Timer

Submit Button

Both panels must scroll independently.

The reading passage must never disappear while answering.

---

## Supported Question Types

Multiple Choice

Matching Headings

Matching Information

Matching Features

Sentence Completion

Summary Completion

Table Completion

Flow Chart Completion

Diagram Labelling

True False Not Given

Yes No Not Given

Paragraph Selection

Short Answer

Every type must be implemented separately.

---

## Navigation

Students may:

Move freely between questions.

Move freely between passages.

Flag questions.

Jump using Question Palette.

Review unanswered questions.

No restrictions until submission.

---

## Highlight Tool

Students may highlight any word or sentence inside the reading passage.

Highlights remain until submission.

Different colors should be supported in future.

---

## Notes Tool

Students may create personal notes attached to any paragraph.

Notes are private.

Notes are deleted after submission.

---

## Search Tool

NOT allowed.

The platform must never provide text search.

---

## Autosave

Every answer

Every few seconds

Every navigation event

Every browser recovery

must automatically save.

---

## Timer

One timer controls the whole Reading examination.

No section timers.

Automatic submission when time expires.

---

## Review Screen

Display:

Answered

Unanswered

Flagged

Question Summary

Students may edit answers until submission.

---

## Anti-Cheating

Log:

Window switching

Multiple tabs

Clipboard

Developer tools

Fullscreen exit

Network interruption

---

## Submission

Confirmation dialog.

Lock examination.

Generate Submission Object.

Send to Assessment Engine.

---

## AI Notes

AI may analyze:

Most difficult passages

Most skipped questions

Average completion time

Common mistakes

Average band prediction

---

# End of Chapter 9
# Chapter 10

# Writing Engine

---

# Goal

The Writing Engine must reproduce the official IELTS Computer Delivered Writing examination while providing professional AI and Teacher assessment workflows.

The environment must feel identical to a real examination rather than a simple text editor.

---

# Examination Structure

Academic

Task 1

↓

Task 2

General Training

Task 1

↓

Task 2

One global timer controls both tasks.

Students decide how to distribute their time.

---

# Entering Writing

Student completes Reading.

↓

System loads Writing.

↓

Instructions appear.

↓

Countdown (optional).

↓

Writing begins.

---

# Interface Layout

HEADER

Timer

Word Counter

Save Status

Candidate ID

-------------------------------------------------

LEFT PANEL

Task Description

Images

Charts

Graphs

Tables

Instructions

-------------------------------------------------

RIGHT PANEL

Essay Editor

-------------------------------------------------

BOTTOM

Task Switch

Review

Submit

Connection Status

---

# Essay Editor

The editor must remain intentionally minimal.

Allowed:

Typing

Copy

Paste

Cut

Undo

Redo

Select All

Cursor Navigation

Keyboard Shortcuts

Disabled:

Spell Checker

Grammar Checker

Auto Complete

AI Writing Assistance

Translation

Formatting Toolbar

Font Changes

Bold

Italic

Underline

Students must only write plain text.

---

# Word Counter

Display:

Current words

Minimum words

Recommended words

Task progress

Counter updates instantly.

---

# Autosave

Save every:

5 seconds

Paragraph completion

Task switch

Browser refresh

Connection recovery

Every save is silent.

---

# Task Switching

Students may switch freely between Task 1 and Task 2.

No restrictions.

All writing remains saved.

---

# Timer

One timer.

Visible at all times.

Warning:

10 minutes

5 minutes

1 minute

Automatic submission at zero.

---

# Review Screen

Before submission display:

Task 1 completed?

Task 2 completed?

Word count

Warnings

Flagged issues

Students may return.

---

# Submission

Confirmation dialog.

↓

Generate Submission.

↓

Store Essays.

↓

Lock editor.

↓

Start Assessment Pipeline.

---

# Assessment Selection

Immediately after submission,

students choose:

Option 1

AI Assessment

or

Option 2

Teacher Assessment

The choice must be made before results processing begins.

---

# AI Assessment Workflow

Essay

↓

Assessment Queue

↓

AI Evaluation

↓

Band Calculation

↓

Criterion Analysis

↓

Grammar Analysis

↓

Vocabulary Analysis

↓

Coherence Analysis

↓

Task Response Analysis

↓

Feedback Generation

↓

Result Publication

Average waiting time:

10–30 seconds.

---

# AI Evaluation Criteria

The AI MUST evaluate according to official IELTS Writing Band Descriptors.

Criterion 1

Task Achievement / Task Response

Criterion 2

Coherence & Cohesion

Criterion 3

Lexical Resource

Criterion 4

Grammatical Range & Accuracy

The AI must assign:

Band for each criterion

Overall Band

Confidence Score

---

# AI Feedback

The report should include:

Overall Band

Criterion Bands

Strengths

Weaknesses

Grammar Mistakes

Vocabulary Suggestions

Repeated Words

Sentence Variety

Paragraph Structure

Coherence Issues

Ideas Development

Recommended Improvements

Estimated Official Band

Study Recommendations

Model Answer Suggestions (Future)

---

# Teacher Assessment Workflow

Student selects:

Teacher Assessment

↓

Platform displays:

My Teacher

Public Teachers

Teacher Profile

Price (future)

Estimated Review Time

Rating

Languages

Specialization

↓

Student selects teacher.

↓

Submission enters Teacher Queue.

↓

Teacher receives notification.

↓

Teacher accepts.

↓

Teacher reviews.

↓

Teacher submits assessment.

↓

Student receives notification.

---

# Teacher Evaluation Panel

Teacher sees:

Essay

Band Descriptor

Comment Box

Criterion Scores

Grammar Notes

Vocabulary Notes

Overall Feedback

Suggested Improvements

Final Band

Private Notes

Publish Button

---

# Teacher Review Status

Pending

Accepted

In Review

Completed

Returned

Cancelled

---

# Revision History

Every review is stored.

Owner may compare:

Original Essay

AI Feedback

Teacher Feedback

Final Result

---

# Anti-Cheating

Record:

Copy/Paste frequency

Tab switching

Window changes

Typing speed

Idle time

Suspicious behaviour

Logs remain available for Owner.

---

# Analytics

Collect:

Average Band

Average Word Count

Most Common Grammar Errors

Most Common Vocabulary Errors

Most Difficult Task

Average Completion Time

Task Distribution

---

# Future Features

Second Opinion

AI + Teacher Comparison

Band Prediction Trends

Essay Library

Personal Vocabulary Report

Grammar Progress

Writing Heatmap

AI Personalized Exercises

---

# Success Criteria

The Writing Engine must become a complete professional writing assessment environment rather than a text submission page.

Students should receive meaningful feedback regardless of whether they choose AI or Teacher assessment.

Teachers should be able to evaluate essays efficiently while maintaining consistency with official IELTS standards.

---

# End of Chapter 10
# Chapter 11

# Speaking Examination Engine

---

# Goal

Provide a speaking experience that closely replicates the official IELTS Speaking examination while supporting both AI assessment and human examiner assessment.

---

# Examination Structure

Part 1

Introduction & Interview

4–5 minutes

↓

Part 2

Cue Card

1 minute preparation

2 minutes speaking

↓

Part 3

Discussion

4–5 minutes

---

# Examination Flow

Student starts Speaking

↓

Microphone Check

↓

Noise Detection

↓

Permission Check

↓

Recording Test

↓

Instructions

↓

Start Part 1

↓

Part 2

↓

Preparation Timer

↓

Speech Recording

↓

Part 3

↓

Final Review

↓

Submit

---

# Device Validation

Before starting:

Microphone available

Permission granted

Recording quality acceptable

Internet stable

Browser supported

If validation fails:

Block examination.

Display clear instructions.

---

# Microphone Test

Student records 5–10 seconds.

Playback available.

Student confirms quality.

Only then may the examination begin.

---

# Interface

HEADER

Timer

Recording Status

Microphone Level

Connection Status

--------------------------------

LEFT

Current Question

Instructions

Preparation Timer

--------------------------------

RIGHT

Audio Recorder

Recording Waveform

Next Button

Previous Button

Finish Button

---

# Recording Rules

Recording starts automatically.

Students cannot upload external audio.

Students cannot replace recordings after submission.

Each response is stored separately.

---

# Part 1

Questions displayed one by one.

Student records each answer.

Owner can configure:

Number of questions

Time per answer

Randomization

---

# Part 2

Display Cue Card.

Preparation timer:

60 seconds.

Student notes (optional).

Recording begins automatically.

Speaking timer visible.

Automatic stop when maximum duration reached.

---

# Part 3

Display one discussion question at a time.

Independent recording for each answer.

Navigation only after recording completes.

---

# Autosave

Save:

Each recording

Metadata

Timer

Current question

Recovery state

Nothing should be lost after refresh.

---

# Submission

Generate:

Audio Package

Metadata

Transcription Request

Assessment Request

Logs

Lock examination.

---

# AI Pipeline

Audio

↓

Noise Reduction

↓

Speech Recognition

↓

Transcript

↓

Grammar Analysis

↓

Vocabulary Analysis

↓

Pronunciation Analysis

↓

Fluency Analysis

↓

IELTS Criteria Evaluation

↓

Band Score

↓

Feedback Report

---

# IELTS Assessment Criteria

Fluency & Coherence

Lexical Resource

Grammatical Range & Accuracy

Pronunciation

Each criterion receives:

Band Score

Comments

Strengths

Weaknesses

Recommendations

Overall Band

Confidence Score

---

# Teacher Review

Teacher receives:

Audio

Transcript

Question

Band Descriptors

Comment Editor

Criterion Scores

Overall Band

Feedback

Publish

---

# Student Result

Student receives:

Overall Band

Criterion Bands

Transcript

Highlighted mistakes

Pronunciation report

Vocabulary feedback

Grammar feedback

Fluency analysis

Recommendations

Teacher comments (if applicable)

---

# Anti-Cheating

Detect:

Muted microphone

Audio interruption

Background voices

Device switching

Browser switching

Multiple people speaking

Suspicious silence

Events stored in logs.

---

# Analytics

Average Speaking Band

Average Fluency

Average Pronunciation

Speaking Duration

Most Difficult Questions

Teacher vs AI Comparison

Pronunciation Heatmap

---

# Future Features

Live Speaking Exam

Video Recording

Official Examiner Mode

Avatar Examiner

Conversation AI

Adaptive Speaking

Voice Biometrics

Accent Analysis

---

# Success Criteria

Students should feel they are completing an authentic IELTS Speaking examination.

Assessment should closely align with official IELTS Speaking Band Descriptors whether evaluated by AI or a qualified teacher.

---

# End of Chapter 11
# Chapter 12

# Teacher Workspace

---

# Goal

The Teacher Workspace is a professional dashboard where teachers manage students, classes, mock examinations, homework, assessments, communication, and analytics.

It should function as a complete teaching management system rather than a simple list of students.

---

# Dashboard

After login the teacher immediately sees:

Today's Lessons

Today's Attendance

Homework to Review

Writing Reviews

Speaking Reviews

Upcoming Mock Tests

Recent Student Activity

Notifications

Teaching Statistics

Calendar

Quick Actions

---

# Sidebar Navigation

Dashboard

Classes

Students

Homework

Materials

Attendance

Mock Tests

Writing Reviews

Speaking Reviews

Analytics

Messages

Calendar

Profile

Settings

---

# Classes

Teachers can:

Create Class

Edit Class

Archive Class

Invite Students

Generate Invite Code

Generate QR Code

Assign Materials

Assign Homework

Assign Mock Tests

View Class Statistics

---

# Student Management

Each student profile displays:

Photo

Name

Email

Phone (optional)

CEFR Level

IELTS Target Score

Current Progress

Attendance

Homework Completion

Mock History

Writing History

Speaking History

Teacher Notes

Parents (future)

---

# Attendance

Teachers can:

Mark Present

Late

Absent

Excused

Add attendance comments

Export attendance

View attendance trends

---

# Homework

Teachers may:

Create homework

Attach files

Set deadlines

Assign to one class or multiple classes

Grade submissions

Leave comments

Return for revision

Publish grades

---

# Learning Materials

Teachers may upload:

PDF

Word

PowerPoint

Images

Videos

Audio

Links

Google Drive (future)

Each material can be assigned to selected classes.

---

# Mock Tests

Teachers may:

Assign published mock tests

Schedule availability

Monitor active examinations

View completion status

View results

Filter by class

Duplicate assignments

---

# Writing Review Queue

Teacher sees:

Student

Class

Submission Time

Deadline

Status

Estimated Review Time

Priority

Open Review

Submit Feedback

---

# Speaking Review Queue

Teacher sees:

Audio Recording

Transcript

Student Information

Question Set

Band Descriptor

Evaluation Form

Publish Result

---

# Analytics

Display:

Average Class Band

Attendance Rate

Homework Completion

Writing Improvement

Speaking Improvement

Reading Scores

Listening Scores

Student Rankings

Weak Skills

Strong Skills

---

# Communication

Teachers may:

Send announcements

Private messages

Homework reminders

Mock reminders

Review notifications

Parents (future)

---

# Calendar

Shows:

Lessons

Mock Tests

Deadlines

Reviews

Meetings

Personal Events

---

# Public Teacher Profile

Teachers may enable:

Public Profile

Biography

Experience

Qualifications

Languages

Teaching Fees (future)

Availability

Rating

Students may request reviews directly from public teachers.

---

# Notifications

Receive alerts for:

New homework

Mock completed

Writing submitted

Speaking submitted

Student joined

Class invitation accepted

Platform announcements

---

# Teacher Settings

Manage:

Profile

Password

Notifications

Availability

Public visibility

Review preferences

Language

Theme

---

# Restrictions

Teachers cannot:

Access Owner Workspace

Delete platform data

Modify AI configuration

Access system logs

Publish platform updates

Manage billing

---

# Success Criteria

Teachers should be able to manage their entire educational workflow from a single workspace without requiring external tools.

The Teacher Workspace should minimize administrative effort and maximize time spent on teaching and student development.

---

# End of Chapter 12
# Chapter 13

# Student Workspace

---

# Goal

The Student Workspace is the personal learning hub of every student using the Lexora platform.

It should provide a clean, motivating, and organized environment where students can study, complete assignments, take mock examinations, communicate with teachers, and monitor their progress.

The Student Workspace should minimize distractions and maximize learning efficiency.

---

# Dashboard

Immediately after login, the student sees:

Welcome Message

Today's Classes

Upcoming Lessons

Homework Due

Assigned Mock Tests

Recent Results

Writing Feedback

Speaking Feedback

Notifications

Study Streak

Progress Overview

Recommended Tasks

Calendar

Quick Actions

---

# Sidebar Navigation

Dashboard

My Classes

Homework

Materials

Mock Tests

Writing

Speaking

Results

Progress

Calendar

Messages

Profile

Settings

---

# My Classes

Students can:

View enrolled classes

See teacher information

View classmates (optional)

Access class materials

View announcements

Join live lessons (future)

---

# Homework

Students can:

View assignments

Read instructions

Upload files

Submit answers

Edit submission before deadline

View teacher feedback

Track completion status

---

# Learning Materials

Students can access:

PDF Files

Videos

Audio

Presentations

Links

Worksheets

Practice Exercises

Materials can be filtered by:

Subject

Teacher

Date

Class

---

# Mock Tests

Students may:

View assigned mock tests

View available practice tests

Start examination

Resume unfinished examination

View completed attempts

Review results

Download reports (future)

Each mock displays:

Difficulty

Estimated Duration

Assigned By

Deadline

Completion Status

---

# Writing

Students may:

View Writing Tasks

Write essays

Save drafts

Submit essays

Choose:

AI Assessment

Teacher Assessment

View feedback

Compare previous submissions

Track improvement

---

# Speaking

Students may:

Record answers

Practice speaking

Submit recordings

Choose:

AI Assessment

Teacher Assessment

Review transcripts

Listen to recordings

Track pronunciation improvement

---

# Results

Display:

Listening Score

Reading Score

Writing Band

Speaking Band

Overall Band

Teacher Comments

AI Feedback

Submission Date

Review Status

Download Certificate (future)

---

# Progress

Students can monitor:

Overall IELTS Band Progress

CEFR Progress

Skill Breakdown

Weekly Activity

Monthly Activity

Completed Homework

Completed Mock Tests

Study Hours

Attendance

Learning Streak

Personal Goals

---

# Analytics

Charts include:

Band History

Listening Progress

Reading Progress

Writing Progress

Speaking Progress

Vocabulary Growth (future)

Grammar Improvement

Attendance Rate

Homework Completion

Average Mock Score

---

# Notifications

Students receive:

Homework Assigned

Homework Graded

Mock Assigned

Mock Reminder

Writing Feedback Ready

Speaking Feedback Ready

Teacher Announcement

Platform Announcement

Achievement Earned

---

# Calendar

Displays:

Lessons

Homework Deadlines

Mock Tests

Writing Reviews

Speaking Reviews

Events

Reminders

---

# Messages

Students may:

Message teachers

Receive replies

Receive review requests

Receive announcements

Future:

Group Chat

Class Discussion

AI Tutor Chat

---

# Achievements

Students earn badges for:

Homework Streak

Attendance Streak

Mock Completion

Band Improvement

Perfect Attendance

Writing Milestone

Speaking Milestone

Study Hours

Fast Improvement

Achievements should encourage consistent learning.

---

# AI Recommendations

The AI may recommend:

Homework

Vocabulary Practice

Grammar Exercises

Mock Tests

Writing Practice

Speaking Practice

Weak Skill Improvement

Daily Study Plan

Recommendations should adapt based on student performance.

---

# Profile

Students may edit:

Profile Photo

Name

Password

Language

Timezone

Notification Preferences

Learning Goals

Target IELTS Band

Preferred Teacher (optional)

---

# Restrictions

Students cannot:

Modify examinations

Access answer keys

View other students' submissions

Modify grades

Publish content

Access administrative functions

---

# Success Criteria

Students should always know:

What they need to study.

What they have completed.

What they need to improve.

How close they are to achieving their target IELTS score.

The Student Workspace should become the student's daily learning companion rather than simply an examination portal.

---

# End of Chapter 13
# Chapter 14

# Platform Services (AI, Analytics, Communication & Payments)

---

## AI Assessment Engine

Central AI service responsible for:

- Writing assessment
- Speaking assessment
- OCR processing
- PDF parsing
- Feedback generation
- Band calculation
- Grammar analysis
- Vocabulary analysis
- Pronunciation analysis
- Personalized recommendations

AI jobs run asynchronously through a processing queue.

Every AI result includes:

- Confidence Score
- Processing Time
- Version
- Model Used
- Logs

Owner can:

- Retry jobs
- Reprocess submissions
- Compare AI versions
- Disable/enable AI modules

---

## Analytics Engine

Analytics available for:

Owner

Teacher

Student

Metrics include:

Student Growth

Teacher Performance

Attendance

Homework Completion

Mock Performance

Writing Trends

Speaking Trends

Listening Statistics

Reading Statistics

Platform Usage

Retention

Active Users

Storage Usage

AI Processing Statistics

Reports support:

PDF

Excel

CSV

Future API Export

---

## Notification System

Notifications delivered via:

In-App

Email

Push Notifications (Future)

Telegram (Future)

WhatsApp (Future)

Notification types:

Homework

Reviews

Mock Assignments

Deadlines

Announcements

System Alerts

AI Completion

Payment Events

Notifications support:

Read

Unread

Archive

Delete

Priority Levels

---

## Messaging System

Private Messages

Teacher ↔ Student

Owner ↔ Teacher

Owner ↔ Student

Future:

Class Chats

Group Discussions

AI Tutor Chat

File Sharing

Voice Messages

---

## Payment System (Future)

Support:

Monthly Subscription

Yearly Subscription

Mock Purchases

Teacher Reviews

Marketplace

Invoices

Discount Codes

Coupons

Refund Requests

Payment History

Regional payment providers should be supported.

---

## Security

Authentication

JWT Sessions

Refresh Tokens

Role-Based Access

Encrypted Passwords

Encrypted Storage

Audit Logs

Rate Limiting

2FA (Future)

Session Management

Automatic Backups

Cloud Storage

---

## Success Criteria

All platform services operate independently through modular architecture.

Failure of one service must never interrupt the rest of the platform.

---

# End of Chapter 14
# Chapter 15

# Deployment, Infrastructure & Future Vision

---

## Technology Stack

Frontend

Next.js

React

TypeScript

TailwindCSS

Shadcn/UI

Backend

NestJS

Node.js

Prisma ORM

PostgreSQL

Redis

Storage

Cloudflare R2

Supabase Storage (optional)

Database

PostgreSQL

Authentication

Clerk or Auth.js

AI

OpenAI

Google Gemini

OCR

Mistral OCR

Google Vision API

Cloud Infrastructure

Cloudflare

Render

Railway

Docker

GitHub

CI/CD

GitHub Actions

Monitoring

Sentry

BetterStack

Analytics

PostHog

---

## System Architecture

Frontend

↓

API Gateway

↓

Authentication

↓

Business Services

↓

Database

↓

Storage

↓

AI Queue

↓

Notification Service

Every service must remain modular.

---

## Scalability Goals

Support:

10 teachers

↓

100 teachers

↓

1,000 teachers

↓

10,000+ students

Architecture should require minimal redesign while scaling.

---

## Product Vision

Lexora is not just an LMS.

Lexora is an AI-powered educational operating system.

The long-term vision includes:

Online School

IELTS Platform

Teacher Marketplace

Mock Marketplace

Course Platform

AI Tutor

AI Speaking Partner

AI Homework Checker

AI Lesson Generator

Certificate System

Parent Portal

Mobile Application

Public API

Franchise Management

Multi-language Support

Corporate Training

University Integration

---

## Development Principles

Every feature must be:

Modular

Reusable

Maintainable

Secure

Scalable

Responsive

Accessible

AI-Ready

No feature should require rewriting the platform architecture.

---

## Final Success Criteria

Lexora should become the central ecosystem connecting teachers, students, AI, assessments, educational management, and future online learning into a single unified platform.

Every new feature should integrate into the existing architecture without disrupting current functionality.

The platform should be production-ready, cloud-native, and capable of continuous evolution.

---

# End of Product Requirements Document