# Videoflix Backend

Videoflix is a Django REST Framework backend for a video streaming application.

The backend provides user authentication, account activation, password reset functionality, video management and HLS video streaming in multiple resolutions.

Video processing is handled asynchronously using Django RQ and Redis.

## Technologies

- Python
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Django RQ
- Gunicorn
- Docker
- FFmpeg
- HLS (HTTP Live Streaming)
- JWT authentication

## Features

- User registration via email
- Account activation via email
- JWT authentication using HTTP-only cookies
- Login and logout
- Access token refresh
- Password reset via email
- Video management through Django Admin
- Automatic thumbnail generation
- Automatic HLS video conversion
- HLS streaming in 480p, 720p and 1080p
- Background video processing with Django RQ
- PostgreSQL database
- Redis integration

## Requirements

To run the project, you need:

- Docker
- Docker Compose

The application and its required services are started through Docker Compose.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/MarcAndreBuck/videoflix_backend.git
cd videoflix_backend
```

### 2. Create the environment file

Copy `.env.template` and create a `.env` file from it.

Linux/macOS:

```bash
cp .env.template .env
```

Windows PowerShell:

```powershell
Copy-Item .env.template .env
```

Adjust the environment variables in `.env` if necessary.

The configuration includes:

- Django settings
- Superuser credentials
- PostgreSQL credentials
- Redis configuration
- Frontend URL
- Email configuration
- JWT cookie security settings

### 3. Start the application

```bash
docker compose up --build
```

The backend is available at:

```text
http://localhost:8000
```

The startup process automatically:

- waits for PostgreSQL
- collects static files
- creates and applies database migrations
- creates the configured Django superuser if it does not exist
- starts the Django RQ worker
- starts Gunicorn

## Django Admin

The Django Admin interface is available at:

```text
http://localhost:8000/admin/
```

The initial superuser credentials are configured through the following environment variables:

```text
DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_PASSWORD
DJANGO_SUPERUSER_EMAIL
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/register/` | Register a new user |
| GET | `/api/activate/<uidb64>/<token>/` | Activate a user account |
| POST | `/api/login/` | Log in and set authentication cookies |
| POST | `/api/logout/` | Log out and invalidate the refresh token |
| POST | `/api/token/refresh/` | Refresh the access token |
| POST | `/api/password_reset/` | Request a password reset email |
| POST | `/api/password_confirm/<uidb64>/<token>/` | Set a new password |

### Video

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/video/` | Return all available videos |
| GET | `/api/video/<movie_id>/<resolution>/index.m3u8` | Return an HLS manifest |
| GET | `/api/video/<movie_id>/<resolution>/<segment>/` | Return an HLS video segment |

Video endpoints require JWT authentication.

## Video Processing

Videos can be uploaded through the Django Admin interface.

After a new video is created, a Django signal queues the video processing task using Django RQ.

FFmpeg then automatically:

1. generates a thumbnail
2. creates a 480p HLS version
3. creates a 720p HLS version
4. creates a 1080p HLS version

The generated HLS files are stored in the media directory and consist of `.m3u8` manifests and `.ts` video segments.

## Authentication

Authentication is based on JWT tokens.

After a successful login, the backend stores the access and refresh tokens in HTTP-only cookies.

The access token is used to authenticate protected API requests. The refresh token can be used to obtain a new access token and is invalidated during logout.

Cookie security can be configured through:

```text
JWT_COOKIE_SECURITY_ENABLED
```

## Background Tasks

Video processing runs asynchronously using Django RQ.

Redis is used by the RQ queue and is provided as a separate Docker service.

The default queue is started automatically together with the backend container.

## Database

Videoflix uses PostgreSQL.

Database credentials are configured in `.env`:

```text
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

The PostgreSQL data is persisted using a Docker volume.

## Email Configuration

Account activation and password reset require an SMTP server.

Configure the following values in `.env`:

```text
EMAIL_HOST
EMAIL_PORT
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
EMAIL_USE_TLS
EMAIL_USE_SSL
DEFAULT_FROM_EMAIL
```

The frontend URL used for generated email links is configured through:

```text
FRONTEND_URL
```

## Stop the Application

To stop the running containers:

```bash
docker compose down
```

To start them again:

```bash
docker compose up
```