# VedaAI Assessment Mapper

A teacher-facing workflow that extracts printed questions, reads a handwritten answer sheet, maps answers back to their questions, and highlights the exact answer regions. It follows the supplied VedaAI Figma flow and explicitly handles sub-parts, out-of-order work, unanswered questions, unmatched work, and answers spanning multiple pages.

## Architecture

- **Frontend:** React + TypeScript + Vite, responsive upload/progress/review experience.
- **Backend:** FastAPI with in-memory assessment state.
- **Document pipeline:** PyMuPDF renders PDF pages; Pillow normalizes uploaded images.
- **AI:** Gemini multimodal structured output. The first pass extracts ordered questions. The second transcribes, maps, locates, and grades answers. Bounding boxes are normalized to the full page so overlays remain accurate at any display size.
- **Storage:** Temporary local files only. No database or authentication, as requested.

## Run with Docker

1. Copy `.env.example` to `.env` and add a Gemini API key.
2. Start the application:

   ```powershell
   docker compose up --build
   ```

3. Open [http://localhost:8080](http://localhost:8080). Use **explore with a sample assessment** if you want to inspect the complete interface without an API key.

Supported inputs are PDF, PNG, JPEG, and WebP. The default limits are 20 MB and 20 pages per document; both are configurable in `.env`.

## Included sample files

Use these together to exercise the full mapping flow:

- `output/pdf/sample-biology-question-paper.pdf`
- `output/pdf/sample-handwritten-answer-sheet.pdf`

The answer sheet intentionally contains out-of-order responses, separate labelled sub-parts, a multi-page answer, an unanswered graph question, and one unmatched `Q6` response. Regenerate both files with `scripts/generate_sample_pdfs.py` using the bundled or project Python runtime.

## Local development

Backend:

```powershell
./.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt
./.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --reload --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Tests:

```powershell
./.venv/Scripts/python.exe -m pytest backend/tests -q
cd frontend
npm run build
```

## Deploy and enable CI/CD on Google Cloud Run

Choose the Google Cloud project and enable the required APIs once:

```powershell
$PROJECT_ID = "your-google-cloud-project-id"
gcloud config set project $PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
gcloud artifacts repositories create vedaai --repository-format=docker --location=asia-south1
gcloud iam service-accounts create vedaai-runtime --display-name="VedaAI Cloud Run runtime"
gcloud secrets create GEMINI_API_KEY --replication-policy=automatic
```

Add the Gemini key as a secret version in **Secret Manager** in Google Cloud Console. Do not put the real key in `.env.example` or commit it. Then grant the runtime identity access:

```powershell
$RUNTIME_SA = "vedaai-runtime@$PROJECT_ID.iam.gserviceaccount.com"
gcloud secrets add-iam-policy-binding GEMINI_API_KEY --member="serviceAccount:$RUNTIME_SA" --role="roles/secretmanager.secretAccessor"
```

Grant the Cloud Build service account permission to push images and deploy Cloud Run. You can copy the build service account from **Cloud Build > Settings** in Google Cloud Console:

```powershell
$BUILD_SA = "the-cloud-build-service-account-from-settings"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$BUILD_SA" --role="roles/artifactregistry.writer"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$BUILD_SA" --role="roles/run.admin"
gcloud iam service-accounts add-iam-policy-binding $RUNTIME_SA --member="serviceAccount:$BUILD_SA" --role="roles/iam.serviceAccountUser"
```

Run the first deployment from the repository root:

```powershell
gcloud builds submit --config cloudbuild.yaml .
```

Cloud Run prints the public `run.app` URL after deployment. The frontend and backend use that same URL because the production container serves both, and `/api/*` is handled by FastAPI.

For continuous integration and deployment, connect this GitHub repository in **Cloud Build > Repositories**, then create two triggers:

- Pull request trigger: use `cloudbuild-ci.yaml`. It runs backend tests, builds the frontend, and verifies the Docker image without deploying.
- Push-to-branch trigger: branch regex `^main$`, use `cloudbuild.yaml`. It runs the same checks, pushes the image to Artifact Registry, and deploys it.

Require the pull-request trigger's status check in the GitHub `main` branch protection rules if the repository plan supports it.

The included deployment keeps CPU available between polling requests and caps the service at one instance because processing and job state live inside the container. For a production system with higher concurrency, move jobs and files to Cloud Tasks and Cloud Storage.

For a production custom domain, put a global external Application Load Balancer with a serverless NEG in front of the service, attach a Google-managed certificate, and add its DNS record at your registrar. Google currently recommends this route; direct Cloud Run domain mapping remains preview-only and is not available in `asia-south1`.

## Assumptions and limitations

- AI transcription and grading are suggestions for teacher review, not final authority.
- In-memory jobs and temporary uploads disappear when an instance restarts or scales down.
- Very dense handwriting, poor scans, and ambiguous numbering can lower mapping accuracy; confidence and unmatched-work states make that uncertainty visible.
- No answer key is uploaded in the requested flow, so grading is based on the question and model knowledge. Scores stay empty when a defensible maximum is unavailable.
- One assessment is processed per request flow. Multi-student batch processing is intentionally out of scope.
