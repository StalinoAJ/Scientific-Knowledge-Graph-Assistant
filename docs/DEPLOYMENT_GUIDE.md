# Scientific Knowledge Graph Assistant - Alpha Version 🚀

## Prerequisites

Before running the application, please ensure you have the following installed:

1.  **Docker Desktop**: [Download Here](https://www.docker.com/products/docker-desktop/) (Must be running)
2.  **Ollama**: [Download Here](https://ollama.ai/) (Required for AI features)

## Quick Start (Windows)

1.  **Start Ollama**:
    Open a terminal and run:
    ```bash
    ollama serve
    ```
    *Ensure you have pulled the model at least once:* `ollama pull llama3.2`

2.  **Run the App**:
    Double-click the `start_app.bat` file in this folder.

3.  **Access**:
    -   **Web Interface**: [http://localhost:3000](http://localhost:3000)
    -   **Admin Panel**: Click the "Admin & Tools" button in the top right.

## Manual Start (Mac/Linux)

If you are on Mac or Linux, run these commands in part terminal:

```bash
# 1. Start containers
docker-compose up -d --build

# 2. View logs (optional)
docker-compose logs -f
```

## Troubleshooting

-   **"Docker is not running"**: Open Docker Desktop and wait for the engine to start.
-   **"Ollama connection failed"**: Ensure `ollama serve` is running in a separate terminal window.
-   **Database Error**: If the graph is empty or behaving strangely, use the **Admin Panel -> Data Management -> Delete All Data** to reset the system.

## System Architecture

-   **Frontend**: React + TypeScript (Port 3000)
-   **Backend**: FastAPI + Python (Port 8000)
-   **Database**: Neo4j Graph Database (Port 7474)
-   **AI**: Local Llama 3.2 via Ollama
