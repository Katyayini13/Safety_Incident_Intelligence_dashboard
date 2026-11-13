# Railway deployment preparation

The project is configured for two independent Railway services. These steps prepare the app; no service has been deployed from this workspace.

## Repository layout and service settings

Publish the contents of this project directory as the Git repository root. In Railway, create two services that both use that repository and branch:

| Service | Root directory | Railway config file | Build | Start | Health check |
| --- | --- | --- | --- | --- | --- |
| Backend API | `/` (repository root) | `/railway.json` | Railpack auto-installs `requirements.txt`; no custom build command | `python -m uvicorn backend.app:app --host 0.0.0.0 --port $PORT` | `/health` |
| Frontend | `/frontend` | `/frontend/railway.json` | `npm run build` (Railpack installs from `package-lock.json`) | `npm run start` | `/health` |

Set each service's config-file path explicitly in Railway Settings. Railway config-as-code is resolved from the repository root, independently of the service root directory. The backend config binds to Railway's injected `PORT`; the frontend's small Node static server does the same. Frontend serving uses Node built-ins, so no extra runtime package was added. The Vite proxy remains development-only.

Railway currently marks config-as-code as deprecated and documents legacy support through December 1, 2026. If deploying after that date, enter the same root directories, build/start commands, and health-check paths directly in each service's Railway Settings instead of relying on the JSON files. The settings and commands in this document remain the source of truth.

## Step-by-step setup

1. Push this project directory to a GitHub repository. Confirm `.gitignore` is included and that no `.env` file or credentials were committed.
2. In Railway, create a project and add a service from the repository named **greenko-backend**. Set Root Directory to `/` (the Python requirements, `backend/`, and `data/` must remain together). Set config file path to `/railway.json` while Railway supports config-as-code; otherwise set the equivalent Build/Deploy fields manually. Leave Build Command auto-detected; the Python `requirements.txt` is at this root. Use the start/health commands in the table.
3. Add the backend's public domain under Networking. Copy the resulting HTTPS origin, for example `https://<backend-domain>.up.railway.app`.
4. In the same Railway project, add a second service from the same repository named **greenko-frontend**. Set Root Directory to `/frontend` and config file path to `/frontend/railway.json` while supported; otherwise set the equivalent Build/Deploy fields manually. Use the build/start/health commands in the table.
5. Add the frontend's public domain under Networking and copy its exact HTTPS origin (scheme and host only, no path or trailing slash).
6. Set service variables:

   **Backend — `CORS_ORIGINS`**

   ```text
   https://<frontend-domain>.up.railway.app
   ```

   Multiple trusted frontend origins can be comma-separated. Do not use `*` for a public production frontend. Railway provides `PORT`; do not assign a fixed port.

   **Frontend — `VITE_API_URL`**

   ```text
   https://<backend-domain>.up.railway.app
   ```

   This is a Vite build-time variable, so save it before building/redeploying the frontend. It must be the backend base URL, without `/api` and without a trailing slash. The production client explicitly errors if it is missing instead of sending requests to the frontend origin. No LLM/API secret is required.

7. Deploy the backend first. Verify `https://<backend-domain>.up.railway.app/health` returns `{"status":"ok"}` and that `/docs` loads. Then deploy the frontend.
8. Open the frontend domain. Verify dashboard data loads, run an incident analysis, and validate a small CSV in Data Import. Browser requests should go directly to the absolute `VITE_API_URL`, with the frontend origin accepted by backend `CORS_ORIGINS`.

## Smoke checks after deployment

From PowerShell (replace the example domains):

```powershell
$backend = 'https://<backend-domain>.up.railway.app'
$frontend = 'https://<frontend-domain>.up.railway.app'
Invoke-RestMethod "$backend/health"
Invoke-RestMethod "$backend/api/analytics"
Invoke-RestMethod "$backend/api/incidents"
Invoke-RestMethod -Method Post -Uri "$backend/api/analyze" -ContentType 'application/json' -Body '{"text":"A worker found an oil leak near a turbine gearbox; no injury reported."}'
```

For CSV validation, use the deployed UI or:

```powershell
curl.exe -X POST "$backend/api/incidents/upload" -F "file=@data/safety_esg_incidents.csv"
```

Uploads are validation-only and are not stored. The app currently uses six original incident records for live model fitting/retrieval; synthetic development data is disclosed separately and is not used as company data.

## Security and source control

- `.gitignore` excludes Python virtual environments, `node_modules`, frontend build output, caches, and `.env` files while allowing the safe `.env.example` template.
- Set `CORS_ORIGINS` to exact trusted frontend origins. The local Vite origins are only the default for development.
- Never commit local `.env` files, Railway tokens, API keys, or credentials. There is no external LLM key in this project.
- Railway health checks verify readiness at deployment time; they are not continuous monitoring.

## Railway references

- [Railway monorepo deployment and root directories](https://docs.railway.com/deployments/monorepo)
- [Railway build and start commands](https://docs.railway.com/builds/build-and-start-commands)
- [Railway health checks and `PORT`](https://docs.railway.com/deployments/healthchecks)
- [Railway config-as-code reference](https://docs.railway.com/config-as-code/reference)
- [Railway variables](https://docs.railway.com/variables)
