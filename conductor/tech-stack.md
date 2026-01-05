# Technology Stack

## Frontend (Thin Client)
*   **Current Implementation:** React 19 (Vite) + TypeScript + Tailwind CSS.
*   **Note:** Vision document mentions Flutter/React Native for mobile capabilities (Camera/Voice). Current codebase is React-based web app.
*   **UI Library:** Lucide React (Icons).
*   **Testing:** Vitest + React Testing Library.
*   **Hosting:** Firebase Hosting.

## Backend (The Refinery)
*   **Core Logic:** Python 3.11 + FastAPI.
*   **Data Processing:** Pandas (CSV/Excel manipulation).
*   **Compute:** Google Cloud Run (Containerized) & Cloud Functions (Event-driven).

## AI & Data
*   **LLM:** Google Vertex AI / Gemini Pro & Flash (Multimodal: Text + Vision).
*   **Database:** Google Firestore (Metadata & Sync) + Google Drive (Blob Storage/Source of Truth).
*   **Auth:** Firebase Auth / Google OAuth (Scopes: `drive.file`).

## Infrastructure
*   **CI/CD:** Google Cloud Build.
*   **Containerization:** Docker.
