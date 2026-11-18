# CampusOps – Smart Campus Facility Booking & Maintenance

A learning/demo implementation for CSA10 Software Engineering Assignment 3 using Vue 3, Django REST Framework, PostgreSQL, Docker Compose, Git and GitHub.

## Features in this starter
- Facility catalogue and operations dashboard
- Booking requests with server-side overlap validation
- Booking request state and demo approval action
- Maintenance ticket creation and guarded state transitions
- Optimistic version checks for ticket updates
- Controlled sensor event intake with unique `(source_id, event_id)` deduplication
- Audit events for booking, ticket and sensor-generated ticket actions
- Two Django API containers behind Nginx, sharing PostgreSQL
- Named PostgreSQL volume for persistent data

## Run on macOS
1. Install Docker Desktop and start it.
2. Open Terminal and enter the project directory.
3. Copy environment example: `cp .env.example .env` and change the local values.
4. Start: `docker compose up --build -d`
5. Check: `docker compose ps`
6. Open `http://localhost:3000`.
7. API health: `http://localhost:3000/api/health/`.
8. Logs: `docker compose logs -f backend1 backend2 frontend`.

## Stop and preserve data
`docker compose down` stops and removes containers but keeps the named volume. Do not use `docker compose down -v` if you need to keep the demo records.

## Push source to GitHub
Create an empty repository on GitHub, then run:
```
git init
git add .
git commit -m "feat: initial smart campus full-stack application"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/smart-campus-facility-platform.git
git push -u origin main
```

## Push the frontend image to Docker Hub
Sign in to Docker Hub and create a repository, e.g. `YOUR_DOCKERHUB_USERNAME/campusops-frontend`.
```
docker login
docker build -t YOUR_DOCKERHUB_USERNAME/campusops-frontend:1.0.0 ./frontend
docker push YOUR_DOCKERHUB_USERNAME/campusops-frontend:1.0.0
```
For backend image:
```
docker build -t YOUR_DOCKERHUB_USERNAME/campusops-backend:1.0.0 ./backend
docker push YOUR_DOCKERHUB_USERNAME/campusops-backend:1.0.0
```
Update Compose `build:` to `image:` for a pull-based deployment after publishing images.

## Important academic limitations
This is a teaching starter, not production-ready. The demo approval route uses a role field in the request body and is NOT secure authentication. Add real login/token authentication and derive role from the authenticated server-side user before presenting it as secure RBAC. The current Django development server is used for local demonstration; use a production WSGI server, HTTPS, restricted CORS/hosts, secure secrets, health checks and tested migrations before production. Booking overlap currently locks the facility row within a transaction; for a strict database-level invariant under all deployments, add PostgreSQL `btree_gist` and an exclusion constraint migration. Run tests and capture actual outputs before making claims in the assignment.

## Suggested genuine evidence screenshots
1. `docker compose ps` showing postgres, backend1, backend2 and frontend.
2. Browser at `http://localhost:3000` showing the live dashboard.
3. Facility catalogue and booking form with records returned by API.
4. Booking overlap rejection after submitting two overlapping requests.
5. Maintenance queue and ticket state progression.
6. Repeated sensor event showing duplicate result and one ticket.
7. GitHub repository file list and commit history.
8. Docker Hub repositories/tags after successful push.
9. Restart test: create record, `docker compose restart backend1`, retrieve same record.
