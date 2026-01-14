# Unified CMTG Platform

> **AI-Native Mortgage Platform** | Next.js + Django + Wagtail

A headless, AI-first mortgage platform that combines content management, loan pricing, and automated rate sheet ingestion.

---

## 🎯 What This Is

This project unifies two legacy systems:
- **custommortgageinc.com** (WordPress) - Content and marketing
- **cmtgdirect** (Django) - Loan pricing engine

Into a modern, scalable platform with AI-powered workflows.

---

## 🏗️ Architecture

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│   Next.js 14   │────▶│     Django     │────▶│    Wagtail     │
│   Frontend     │     │   Pricing API  │     │   Headless CMS │
└────────────────┘     └────────────────┘     └────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   AI Agent Layer  │
                    │  (Rate Sheets,    │
                    │   Content, Quotes)│
                    └───────────────────┘
```

---

## 📂 Project Structure

```
unified-cmtg/
├── unified-platform/           # Main application
│   ├── backend/               # Django + Wagtail
│   ├── frontend/              # Next.js
│   └── conductor/             # Workflow definitions
├── knowledge-base/            # Documentation & SOPs
├── FLOIFY-API/               # Floify integration docs
└── Ratesheet-samples/        # Sample rate sheets
```

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Quick Start

```bash
# Clone and enter directory
git clone git@github.com:samtheloanman/unified-cmtg.git
cd unified-cmtg/unified-platform

# Start all services
docker compose up -d

# Backend will be at: http://localhost:8001
# Frontend will be at: http://localhost:3001
```

### Current Status (2026-01-13)

✅ **Phase 3.5 Complete** - Browser-testable MVP
- Backend API functional with pricing engine
- Frontend Quote Wizard operational
- Brand colors corrected (#1daed4, #636363)
- CMS content migration tools implemented

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [GEMINI.md](./GEMINI.md) | AI agent context (read this first) |
| [PRD.md](./PRD.md) | Product Requirements Document |
| [knowledge-base/](./knowledge-base/) | Rate sheet SOPs and field mappings |

---

## 🧪 Development

### Backend (Django)
```bash
cd unified-platform/backend
python manage.py runserver
python manage.py migrate
pytest
```

### Frontend (Next.js)
```bash
cd unified-platform/frontend
npm install
npm run dev
```

---

## 🔗 Related Repositories

- [samtheloanman/unified-cmtg](https://github.com/samtheloanman/unified-cmtg) - This repo

---

## 📞 External Integrations

| Service | Purpose |
|---------|---------|
| **Floify** | Loan application processing |
| **WPEngine** | Legacy WordPress (cutover planned) |
| **Tailscale** | VPN for development server |

---

## 📋 License

Proprietary - Custom Mortgage Inc.

---

*Last Updated: 2026-01-13*
