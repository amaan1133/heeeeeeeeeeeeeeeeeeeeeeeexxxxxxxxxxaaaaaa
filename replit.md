# Hexamed Asset Management System

## Overview

Hexamed is a Flask-based web application for managing asset and procurement requests within an organization. The system provides a workflow-based approval process with role-based access control, allowing users to submit requests that flow through different approval levels based on organizational hierarchy.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Session Management**: Flask sessions with server-side storage
- **File Handling**: Local file system storage in uploads directory
- **Authentication**: Username/password with hashed passwords using Werkzeug security

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **UI Framework**: Bootstrap 5 with dark theme
- **Icons**: Font Awesome 6.4.0
- **Styling**: Custom CSS with CSS variables for theming

### Security Model
- **Authentication**: Session-based with password hashing
- **Authorization**: Role-based access control (User, Concern Manager, Admin, MD)
- **File Upload Security**: Restricted file types and size limits (16MB max)
- **Audit Trail**: Activity logging for all user actions

## Key Components

### User Management
- **User Model**: Stores user credentials, roles, and profile information
- **Role Hierarchy**: Four-tier system (User → Concern Manager → Admin → MD)
- **Authentication System**: Login/logout with session management

### Request Management
- **AssetRequest Model**: Core entity for tracking procurement/asset requests
- **Workflow System**: Multi-level approval process based on user roles
- **File Attachments**: Support for document uploads with requests
- **Status Tracking**: Pending, Approved, Rejected, Hold states

### Approval Workflow
- **Multi-level Approval**: Requests flow through different approval levels
- **Approval Model**: Tracks approval decisions and comments
- **Role-based Routing**: Different approval paths based on request type and cost

### Activity Logging
- **ActivityLog Model**: Comprehensive audit trail
- **Action Tracking**: Login, logout, request creation, approvals, etc.
- **IP Address Logging**: Security monitoring capability

## Data Flow

### Request Submission Flow
1. User creates asset/procurement request via web form
2. System validates input and saves to database
3. Request enters approval workflow at level 1 (Concern Manager)
4. Email notifications sent to appropriate approvers
5. Approvers review and make decisions
6. Request progresses through approval levels until final decision
7. All actions logged for audit purposes

### User Authentication Flow
1. User submits login credentials
2. System validates against hashed passwords in database
3. Session created and user redirected to dashboard
4. Role-based menu and permissions applied
5. Activity logged for security monitoring

### File Upload Flow
1. User selects files during request creation
2. System validates file type and size
3. Files saved to uploads directory with unique names
4. File metadata stored in UploadedFile model
5. Files linked to specific requests

## External Dependencies

### Frontend Dependencies
- **Bootstrap 5**: UI framework loaded from CDN
- **Font Awesome 6.4.0**: Icon library from CDN
- **Custom CSS**: Local styling for branding and customization

### Python Dependencies
- **Flask**: Core web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Werkzeug**: Security utilities for password hashing
- **SQLite**: Embedded database (no external server required)

### File System Dependencies
- **Uploads Directory**: Local storage for file attachments
- **SQLite Database File**: Single file database storage

## Deployment Strategy

### Current Configuration
- **Development Mode**: Flask debug mode enabled
- **Database**: SQLite file-based (hexamed.db)
- **File Storage**: Local filesystem uploads directory
- **Port Configuration**: Runs on port 5000, accessible from all interfaces (0.0.0.0)

### Environment Variables
- **SESSION_SECRET**: Configurable session encryption key
- **Upload Configuration**: File size limits and allowed extensions in app config

### Database Initialization
- **Auto-creation**: Tables created automatically on startup
- **Admin User**: Default admin account created if not exists
  - Username: admin
  - Password: hexamed123
  - Role: MD (highest level)
- **Security Update**: Demo credentials removed from login screen for production security

### Security Considerations
- **Secret Key**: Session encryption using environment variable or default
- **File Upload Restrictions**: Limited file types and 16MB size limit
- **SQL Injection Protection**: SQLAlchemy ORM provides protection
- **Password Security**: Werkzeug password hashing implementation

### Scalability Notes
- **Database**: Currently uses SQLite (single-user, file-based)
- **File Storage**: Local filesystem storage
- **Session Storage**: Server-side sessions (memory-based)
- **No External Services**: Self-contained application with minimal dependencies