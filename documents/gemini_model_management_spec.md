# Gemini Model Name Management Specification

## 1. Overview
This specification details how the Google Gemini model version is defined, configured, and resolved across the `asset-guard` application ecosystem (Server, Cloud Functions, and Client). It provides the necessary blueprint for external applications to replicate the exact model management behavior.

## 2. Standard Model
The application currently standardizes on the following model version as the "Golden Source":

*   **Model Name:** `gemini-2.5-pro`
*   **Usage:** Default for all production-grade analysis, object identification, and metadata extraction.
*   **Experimental/Fallback:** `gemini-3-flash-preview` (observed in some experimental build contexts, but not the production default).

## 3. Configuration Mechanisms

The model name is managed primarily through Environment Variables and Code Defaults.

### 3.1 Environment Variables
The following environment variables control the model selection:

| Variable Name | Scope | Description | Priority |
| :--- | :--- | :--- | :--- |
| `GEMINI_MODEL` | Global / Build | The standard configuration variable for the desired model version. Injected via `cloudbuild.yaml`. | High |
| `_GEMINI_MODEL` | Internal / Functions | An internal override often used in Cloud Functions (`identify-room-objects`) to supersede the standard variable. | Very High |

### 3.2 Build Configuration (`cloudbuild.yaml`)
The CI/CD pipeline (`cloudbuild.yaml`) injects the model version into the deployment environment.
*   **Variable:** `_GEMINI_MODEL` is defined in the build substitutions (defaulting to `gemini-2.5-pro`).
*   **Injection:** This value is passed to the `--set-env-vars` flag as `GEMINI_MODEL` during the deployment of Cloud Functions (e.g., `deploy-metadata-function`).

## 4. Resolution Logic & Precedence

The application uses two distinct patterns for model resolution depending on the component (Server vs. Cloud Functions).

### 4.1 Pattern A: Dynamic Resolution (Cloud Functions)
Used in: `functions/identify-room-objects`, `functions/document-metadata-processor`, `functions/metadata-processor`

**Resolution Order (Highest to Lowest):**
1.  **Runtime Argument:** Specific `model` parameter passed to the function call (e.g., `{ model: 'gemini-1.5-flash' }`).
2.  **Internal Environment Variable:** `process.env._GEMINI_MODEL`
3.  **Standard Environment Variable:** `process.env.GEMINI_MODEL`
4.  **Hardcoded Default:** `'gemini-2.5-pro'`

**Implementation Reference:**
```javascript
const modelName = model || process.env._GEMINI_MODEL || process.env.GEMINI_MODEL || 'gemini-2.5-pro';
```

### 4.2 Pattern B: Hardcoded Resolution (Node.js Server)
Used in: `server/geminiService.js`

**Resolution Order:**
1.  **Hardcoded Value:** `gemini-2.5-pro`

**Note:** The current server implementation **ignores** environment variables for the model name in `identifyItem` and `extractPropertyDocumentMetadata`. It explicitly sets `const modelName = 'gemini-2.5-pro';`.
*Correction Required for Parity:* To fully align with the ecosystem, the server *should* adopt Pattern A, but currently, it strictly enforces `gemini-2.5-pro`.

## 5. Service-Specific Details

### 5.1 Identify Room Objects (Cloud Function)
*   **Path:** `functions/identify-room-objects/geminiService.js`
*   **Logic:** Adopts **Pattern A**.
*   **Logging:** Logs the selected model at startup: `[Gemini Phase 1] Using Model: ${modelName}`.

### 5.2 Server API
*   **Path:** `server/geminiService.js`
*   **Logic:** Adopts **Pattern B** (Hardcoded).
*   **Methods:**
    *   `identifyItem`: Hardcoded to `gemini-2.5-pro`.
    *   `extractPropertyDocumentMetadata`: Hardcoded to `gemini-2.5-pro`.

## 6. Replication Guide for External Apps

To replicate the `asset-guard` model management behavior in a new application:

1.  **Define Defaults:** Set your application's default model constant to `gemini-2.5-pro`.
2.  **Implement Dynamic Resolution:** Use the following utility function to resolve the model name:
    ```javascript
    function getModelName(overrideModel) {
        return overrideModel || 
               process.env._GEMINI_MODEL || 
               process.env.GEMINI_MODEL || 
               'gemini-2.5-pro';
    }
    ```
3.  **Configure Environment:** Ensure your deployment pipeline sets `GEMINI_MODEL`.
4.  **Vertex AI Context:** Initialize the client with the correct project context (required for Vertex AI-backed Gemini models):
    ```javascript
    const genAI = new GoogleGenAI({
        vertexai: true,
        project: process.env.GCP_PROJECT || process.env.GOOGLE_CLOUD_PROJECT,
        location: 'us-central1',
    });
    ```

## 7. Migration Strategy
To upgrade the model version (e.g., to `gemini-3.0-pro`):
1.  **Update Build Config:** Change `_GEMINI_MODEL` in `cloudbuild.yaml`.
2.  **Update Code Defaults:** Find and replace the hardcoded fallback string `'gemini-2.5-pro'` in all `geminiService.js` files.
