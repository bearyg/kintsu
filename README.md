# Kintsu | Recovery OS

Kintsu is a forensic data recovery platform designed specifically for survivors of catastrophic property loss. It transforms fragmented digital debris into undeniable proof of ownership for insurance claims.

## 🏗 Architecture (BYOS Model)

- **Thin Client (Frontend):** React (Vite) + Tailwind CSS + Lucide Icons. Hosted on **Firebase Hosting**.
- **Middle Server (Orchestrator):** Python (FastAPI) on **Cloud Run**. Handles Google Drive communication and coordination.
- **The Hopper (Storage):** User's personal **Google Drive**. The app only requests access to its own files/folders (`drive.file` scope).
- **The Refinery (AI):** **Gemini 2.5 Pro** integration for structured data extraction from images, PDFs, and CSVs.
- **Golden Record (Database):** **Firestore (NoSQL)**. Real-time sync of refined shards. (BYOS Mode: Data stored in user's Drive).

## 🔄 The Recovery Process

1.  **Sign In:** User connects their Google Drive.
2.  **Collect (Phase 2):** User uploads digital debris (Receipts, Bank Statements, Amazon Data Dumps) into the "Hopper" folders via the app.
3.  **Refine:** The backend unzips archives, chunks large CSVs, and uses Gemini to extract line-item data.
4.  **Review:** Extracted shards appear in the Refinery Stream with "High Confidence" indicators from source data.

## 🚀 CI/CD Pipeline

The project is configured with **Google Cloud Build**.
- **Triggers:** Automatically on push to the `main` branch.
- **Workflow:**
    1. Build Backend Docker image.
    2. Deploy Backend to Cloud Run.
    3. Build Frontend React app.
    4. Deploy Frontend to Firebase Hosting.

## 🛠 Tech Stack

- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Lucide React, Firebase JS SDK.
- **Backend:** Python 3.11, FastAPI, Pandas, Google Generative AI (Gemini), Firestore Admin SDK.
- **Infrastructure:** Google Cloud Platform (Cloud Build, Cloud Run, Secret Manager, Artifact Registry).

## 📁 Project Structure

- `kintsu-app/`: Frontend React application.
- `backend/`: FastAPI refinery service.
- `backend/processors/`: Specialized logic for data sources (e.g., `amazon.py`).
- `functions/`: Cloud Functions for event-driven tasks.
- `cloudbuild.yaml`: CI/CD pipeline definition.

---
*Developed for Homestead Inventory & Forensic Recovery.*