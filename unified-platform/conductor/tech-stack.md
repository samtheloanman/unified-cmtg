# Tech Stack

## 1. Backend

*   **Language:** Python
*   **Framework:** Django
*   **CMS:** Wagtail (Headless)
*   **API:** Django REST Framework (DRF)
*   **Database:** PostgreSQL
*   **Asynchronous Tasks:** Celery
*   **Message Broker/Cache:** Redis

## 2. Frontend

*   **Language:** TypeScript
*   **Framework:** Next.js
*   **Library:** React
*   **Styling:** Tailwind CSS

## 3. DevOps & Containerization

*   **Containerization:** Docker

## 4. Hosting Strategy

*   **Frontend (Next.js):** Vercel
*   **Backend (Django, Celery, Redis, PostgreSQL):** Major Cloud Provider (e.g., AWS, Google Cloud, Azure)

## 5. Rationale

This stack is chosen for its modernity, scalability, and ability to support the "AI-native" vision of the platform.

*   **Django & Wagtail:** Provide a robust, feature-rich, and proven backend for both the pricing engine and content management, leveraging existing legacy logic.
*   **Next.js & React:** Deliver a high-performance, SEO-friendly, and interactive user experience for the frontend.
*   **Celery & Redis:** Form the foundational layer for all asynchronous AI agent workflows, crucial for features like rate sheet ingestion and future agentic services.
*   **Docker:** Ensures environmental consistency and simplifies the deployment of a multi-service architecture.
*   **Vercel & Cloud Provider Hybrid:** Optimizes for both frontend delivery speed and backend operational flexibility.
