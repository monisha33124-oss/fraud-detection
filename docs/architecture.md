# FraudShield AI - System Architecture

## 1. System Overview

FraudShield AI is an enterprise-level, AI-powered financial fraud detection and investigation platform. 

### Current State Audit
- **What already works**: 
  - Basic FastAPI backend with SQLAlchemy models.
  - React + Vite + TypeScript frontend with role-based routing (Admin/Investigator).
  - Pre-trained XGBoost model (`fraud_model_xgb.joblib`) and data pipelines.
  - Several core API routes (`/auth`, `/transactions`, `/investigations`, `/customers`, etc.) and frontend pages (Dashboard, Transactions, Case Management).
- **What is incomplete**: 
  - Several API endpoints are missing (`/users`, `/accounts`, `/predictions`, `/risk`, `/explanations`).
  - Frontend routing needs to strictly follow the `/admin/*` and `/employee/*` structure.
- **What is broken**: 
  - The system appears to currently be using SQLite (`fraud_detection.db`) instead of the planned PostgreSQL architecture.
- **What should be preserved**: 
  - Existing DB models (they match the requirements).
  - Working ML models and pipeline logic.
  - Working frontend components (UI design/styling).
- **What must be modified**: 
  - API router needs to include missing endpoints.
  - Frontend `App.tsx` routing needs to be updated.
  - Database connection should be standardized for PostgreSQL.
- **What is missing**: 
  - Specific frontend pages for reports, analytics, settings, and profile.
  - Granular API routes for ML predictions, risk scoring, and SHAP explanations.

---

## 2. System Architecture

The architecture follows a modern decoupled approach:

**Frontend**: React + TypeScript + Vite
↓
**API Client**: Axios (configured with interceptors for JWT)
↓
**Backend**: FastAPI
↓
**Security**: Authentication & Authorization (Role-Based Access Control)
↓
**Business Logic**: Services Layer
↓
**Data Access**: Repositories Layer
↓
**Database**: PostgreSQL

---

## 3. Machine Learning Architecture

The ML pipeline is responsible for evaluating transactions in real-time.

**Flow:**
Transaction
↓
Validation
↓
Preprocessing (Scaling/Encoding)
↓
Feature Engineering
↓
Model (XGBoost)
↓
Prediction (Legitimate / Fraudulent)
↓
Risk Score (0 - 100)
↓
SHAP (Explainability)
↓
Fraud Alert (If risk threshold exceeded)
↓
Investigation (Case creation)

---

## 4. Modules

The system is logically divided into the following modules:
* **Authentication**: Login, token generation, and validation.
* **Users**: System access management and RBAC.
* **Customers**: Bank customer profiles and risk history.
* **Accounts**: Customer financial accounts.
* **Transactions**: Core financial events.
* **Predictions**: ML model outputs.
* **Risk**: Risk scoring logic and thresholds.
* **SHAP explanations**: Feature importance for explainability.
* **Fraud alerts**: Notifications for suspicious activities.
* **Investigations**: Case management for flagged transactions.
* **Reports**: System and compliance reporting.
* **Analytics**: Business intelligence and dashboards.
* **ML models**: Model metadata and versioning.
* **Audit logs**: System activity tracking for compliance.
* **Settings**: Global system configurations.

---

## 5. Database Architecture

**Entities & Relationships:**

* **users**: System users (Admins, Investigators).
* **roles**: RBAC roles (Admin, Investigator).
* **customers**: End-users of the bank.
* **accounts**: Linked to customers.
* **transactions**: Linked to accounts and customers.
* **fraud_predictions**: 1-to-1 with transactions.
* **risk_scores**: Associated with predictions/transactions.
* **shap_explanations**: 1-to-Many with fraud_predictions.
* **fraud_alerts**: Linked to transactions and customers.
* **investigation_cases**: 1-to-1 with flagged transactions, assigned to users.
* **investigation_notes**: 1-to-Many with investigation_cases.
* **case_history**: Audit trail for cases.
* **ml_models**: Active and historical models.
* **model_metrics**: Performance tracking (Accuracy, F1, etc.).
* **audit_logs**: Immutable system logs.

---

## 6. API Structure

The API is structured around RESTful resources under the `/api` prefix:

* `/api/auth`
* `/api/users`
* `/api/customers`
* `/api/accounts`
* `/api/transactions`
* `/api/predictions`
* `/api/risk`
* `/api/explanations`
* `/api/alerts`
* `/api/investigations`
* `/api/reports`
* `/api/analytics`
* `/api/models`
* `/api/audit`

---

## 7. Frontend Routes

**Public:**
* `/` (Landing Page)
* `/login`
* `/unauthorized`

**Admin:**
* `/admin/dashboard`
* `/admin/users`
* `/admin/customers`
* `/admin/transactions`
* `/admin/alerts`
* `/admin/investigations`
* `/admin/analytics`
* `/admin/models`
* `/admin/audit`
* `/admin/reports`
* `/admin/settings`
* `/admin/profile`

**Employee (Investigator):**
* `/employee/dashboard`
* `/employee/cases`
* `/employee/transactions`
* `/employee/alerts`
* `/employee/investigations/:id`
* `/employee/customers/:id`
* `/employee/reports`
* `/employee/profile`
