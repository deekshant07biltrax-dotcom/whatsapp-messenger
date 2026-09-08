# WhatsApp Messenger - Docker Setup

## Quick Start (Single Command)

Run the entire application with Docker Compose:

```bash
docker-compose up -d
```

That's it! The application will be available at `http://localhost:5556`

## What This Setup Does

This Docker setup eliminates the need to manually run:
- `python app.py` - Flask application
- `python tunnel.py` - Cloudflare tunnel

Everything is now containerized and runs automatically with a single command.

## Prerequisites

- Docker installed on your system
- Docker Compose installed (or use `docker compose` for newer versions)
- Groq AI API key (get one from https://console.groq.com/)

## Environment Configuration

Create a `.env` file in the project root (recommended):

```env
LM_STUDIO_BASE_URL=https://api.groq.com/openai/v1
LM_STUDIO_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.1-8b-instant
MAX_TOKENS=8000
```

**Important**: Replace `your_groq_api_key_here` with your actual Groq API key (starts with `gsk_`).

If you don't create a `.env` file, the application will use default values but won't work without a valid API key.

## Docker Commands

### Start the application
```bash
docker-compose up -d
```

### Stop the application
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### Restart the application
```bash
docker-compose restart
```

### Update and rebuild
```bash
docker-compose down
docker-compose up -d --build
```

## Accessing the Application

- **Local Access**: `http://localhost:5556`
- **Logs**: Available in the `./logs` directory (mapped from container)

## For Public Access (Optional)

If you need to share the application publicly, you can still use the tunnel script:

1. Start the Docker container:
   ```bash
   docker-compose up -d
   ```

2. Run the tunnel script separately:
   ```bash
   python tunnel.py 5556
   ```

The tunnel will expose the Docker container to the public internet.

## Features of This Docker Setup

- **Automatic Restart**: Container restarts automatically if it crashes
- **Health Checks**: Built-in health monitoring
- **Log Persistence**: Logs are saved to your local `./logs` directory
- **Environment Variables**: Easy configuration without modifying code
- **Port Mapping**: Standard port 5556 mapped to host
- **Production Ready**: Uses Gunicorn with optimized settings

## Troubleshooting

### Container won't start
```bash
docker-compose logs
```

### Port already in use
Change the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8080:5556"  # Change 5556 to your preferred port
```

### Need to rebuild after code changes
```bash
docker-compose up -d --build
```

### View container status
```bash
docker-compose ps
```

## Old Method (For Reference)

Before Docker, you had to run:
```bash
# Terminal 1
python app.py

# Terminal 2  
python tunnel.py
```

Now with Docker, just:
```bash
docker-compose up -d
```

## Deployment Options

This Docker setup works with:
- Local development
- Docker Swarm
- Kubernetes (with minor adjustments)
- Any cloud provider that supports Docker