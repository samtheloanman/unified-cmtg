# Product Guide: Unified CMTG Platform

## 1. Vision

To create a headless, AI-native mortgage platform that unifies content, pricing, and agentic workflows, providing a seamless and intelligent experience for all users. This project builds upon the proven pricing logic of the legacy `cmtgdirect` application, migrating it to a modern, scalable, and AI-enhanced architecture.

## 2. Target Users

*   **Primary Users:**
    *   **Homebuyers/Borrowers:** The core user journey. They will use the platform to get quotes, learn about products, and apply for loans.
    *   **Mortgage Loan Officers (MLOs):** Internal users who manage applications, pricing, and content.

*   **Partner & Administrative Users:**
    *   **Realtors & Affiliates:** Refer clients via referral links (potentially from Floify or a custom solution) and track the status of their referred transactions via a simple dashboard.
    *   **Investors:** (Future) Will use a simple dashboard to view the performance of transactions they are invested in.
    *   **Banks:** (Future) Initially, their program data will be managed by an AI agent. Later, they will have a dashboard to manage their loan programs and profiles.
    *   **System Administrators:** Technical users responsible for platform maintenance and user management.

*   **Autonomous Agents:**
    *   **Rate Sheet Ingestion Agent:** The first AI agent to be built. It will automate the extraction of data from lender rate sheets.
    *   *Other agents (Customer Service, Marketing, SEO) are planned for future phases.*

## 3. Core Features

*   **Loan Pricing Engine (from `cmtgdirect`):** The core logic for matching loan qualifications with available programs and generating accurate pricing.
*   **Headless Content Management (Wagtail):** A flexible CMS for creating and managing all marketing and informational content.
*   **AI Agent Layer:** An orchestration layer (potentially like an MCP server or Zapier) to manage and run automated workflows. The first priority is the Rate Sheet Ingestion Agent.
*   **Next.js Frontend:** A modern, performant frontend for all user interactions.
*   **Partner Dashboards:** Simple, role-specific dashboards for Realtors, Affiliates, and (eventually) Investors and Banks.
*   **Investment Fund Page:** A static "Coming Soon" page outlining the vision for a future investment fund (e.g., offering 12% returns). *Note: The full feature requires significant legal and security considerations and is not part of the MVP.*

## 4. MVP Definition

The Minimum Viable Product will focus on successfully migrating the legacy `cmtgdirect` pricing engine into the new, headless architecture and proving the value of the AI agent layer.

**MVP Goal:** A Homebuyer can get an accurate loan quote through the new Next.js interface, powered by the ported Django pricing logic, with rates and programs supplied by the newly developed **Rate Sheet Ingestion Agent**.
