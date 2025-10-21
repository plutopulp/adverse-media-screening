# Adverse Media Screening Tool

An AI-powered tool for compliance analysts to screen individuals against news articles for adverse media mentions. The system uses large language models to assess an article's credibility, extract all person entities and person-person relationships, match the analyst person query to article person entities and assess whether the coverage is adverse.

> **Project Context**: This was developed as a technical assessment for a compliance software role. The repository started from a Next.js + tRPC template provided by the hiring team (commit `d970003`). All subsequent development is original work.

## ✨ Features

- **Credibility Assessment**: Evaluates article reliability before performing expensive analysis
- Extracts all person entities from the article and the relationships between entities (for network understanding), resolving coreferencing as much as possible.
- **Person Matching**: LLM-based analysis matches individuals against article mentions with explainable confidence scores and detailed signal breakdowns.
- **Adverse Media Sentiment Analysis**: Identifies negative mentions with categorized risk levels (fraud, corruption, sanctions, etc.)
- **Results Persistence**: Saves screening results to disk (seemed fine for an MVP)
- **Explainable Outputs**: Every decision includes structured reasoning, evidence spans, and confidence scores
- **Multi-Provider Support**: Works with OpenAI or (possibly :p) Anthropic LLMs (Only developed with openai though and not tested anthropic), where model can be defined in settings environment.

## 🏗️ How It Works

The system runs a straightforward pipeline: scrape article → assess credibility → extract entities → match person → analyse sentiment → save result.

```
┌──────────────────────────────────────────────────────────────────┐
│                         Browser (React UI)                        │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Next.js + tRPC (Web Service)                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                   FastAPI (AI Service Pipeline)                   │
│                                                                    │
│  1. Scrape Article (newspaper3k)                                  │
│  2. Check Credibility (LLM) ────────┐                            │
│  3. Extract Entities (LLM) ──────────┤                           │
│  4. Match Person (LLM) ──────────────┼─► OpenAI/Anthropic       │
│  5. Analyse Sentiment (LLM) ─────────┤                           │
│  6. Save Result (file storage) ──────┘                           │
└──────────────────────────────────────────────────────────────────┘
```

**Key points**: Everything uses LLMs with temperature=0.0 for consistency. All outputs are structured (Pydantic models) with reasoning attached for explainability. The system is conservative - when uncertain, it flags for human review rather than making assumptions. Results are saved automatically so there's an audit trail.

## 📋 Prerequisites

- **Docker** with Compose v2 - [Install Docker Desktop](https://docs.docker.com/get-docker/)
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)
- **Make** (optional) - provides shortcut commands

Verify Docker is installed:

Docker is **required** for running the app as communication between Next.js and fastapi servers
happens over the docker network, but let me know if you encounter any issues and I can address that quickly.

```bash
docker compose version  # Should show v2.x.x
```

## 🚀 Setup

1. **Add your API key** to `services/ai/.env.defaults`:

   ```bash
   # Open services/ai/.env.defaults and replace:
   OPENAI__API_KEY=your-openai-api-key-here
   ```

1. **Build and start**:

   ```bash
   make start
   ```

   Or without Make:

   ```bash
   cd docker && docker compose build && docker compose up -d
   ```

That's it! Access at:

- 🌐 Web UI: http://localhost:3000
- 📚 API Docs: http://localhost:5001/docs

## 📖 Usage

### Performing a Screening

1. Navigate to http://localhost:3000
2. Enter the article URL
3. Provide person details:
   - First name, last name (required)
   - Middle name(s) (optional)
   - Date of birth (optional, improves matching accuracy)
4. Click "Screen Article"
5. Review the detailed results with:
   - Article credibility assessment
   - Person matching analysis with confidence scores
   - Adverse media sentiment (if matched)

### Viewing Past Screenings

1. Click "View Results" in the navbar
2. Browse all past screenings
3. Click any result card to see full details

### Example Test Cases

The application includes example screening results (loaded automatically on first run):

- **Roman Abramovich** - Adverse media (sanctions, oligarch connections)
- **Turkish Mayor** - Corruption allegations
- **Rachel Reeves** - Policy criticism (NOT adverse media)
- **No Match Examples** - Articles without the query person

## 🐳 Docker Commands

### Using Make

```bash
make build      # Build all services
make start      # Start services (detached mode)
make stop       # Stop all services
make restart    # Restart services
make logs       # View logs (follow mode)
make ps         # Show service status
make shell-ai   # Open shell in AI service
make shell-web  # Open shell in web service
```

### Using Docker Compose Directly

```bash
cd docker

docker compose build              # Build services
docker compose up -d              # Start (detached)
docker compose down               # Stop and remove
docker compose logs -f            # View logs
docker compose ps                 # Service status
docker compose exec ai sh         # Shell in AI service
docker compose exec web sh        # Shell in web service
```

## ⚙️ Configuration

The application loads settings from `services/ai/.env.defaults`.

### Results Storage

Results are automatically saved to `services/ai/results/`. Example results are loaded on first run to provide test data for reviewers.

### Development vs Production

**Production Mode** (default - faster UX):

```bash
make start
# or: docker compose up ai web
```

**Development Mode** (hot reload for code changes):

```bash
make dev-start
# or: docker compose up ai web-dev
```

## 📁 Project Structure

```
.
├── docker/                     # Docker configuration
│   ├── docker-compose.yml     # Service orchestration
│   ├── ai.Dockerfile          # AI service image
│   └── web.Dockerfile         # Web service image
├── services/
│   ├── ai/                    # FastAPI backend
│   │   ├── app/               # Application code
│   │   │   ├── config.py      # Settings management
│   │   │   ├── dependencies.py # Dependency injection
│   │   │   ├── routes/        # API endpoints
│   │   │   ├── services/      # Core pipeline stages
│   │   │   └── utils/         # Utilities
│   │   ├── downloads/         # Example articles
│   │   ├── results/           # Saved screening results
│   │   ├── .env.defaults      # Default configuration
│   │   └── pyproject.toml     # Python dependencies
│   └── web/                   # Next.js frontend
│       ├── src/
│       │   ├── app/           # Next.js App Router
│       │   ├── lib/           # Utilities
│       │   ├── server/        # tRPC server
│       │   └── types/         # TypeScript definitions
│       ├── .env.defaults      # Default configuration
│       └── package.json       # Node dependencies
├── Makefile                   # Convenience commands
└── README.md                  # This file
```

## 🔍 API Documentation

Once running, visit http://localhost:5001/docs for interactive API documentation (Swagger UI).

### Key Endpoints

- `POST /screening/screen` - Perform a new screening
- `GET /screening/results` - List all saved results
- `GET /screening/results/{id}` - Get specific result
- `GET /health` - Health check

## 🛠️ Development

### Code Quality (AI Service)

```bash
make format     # Format Python code (black + isort)
make lint       # Lint Python code (flake8)
make test       # Run tests (pytest)
```

### Viewing Logs

```bash
# All services
make logs

```

### Rebuilding After Changes

```bash
# Rebuild specific service
make rebuild-ai
make rebuild-web

# Rebuild all
make rebuild
```

## 🐛 Troubleshooting

### Services Won't Start

**Check Docker is running:**

```bash
docker ps
```

**Check ports are available:**

```bash
# On Mac/Linux
lsof -i :3000
lsof -i :5001

# On Windows
netstat -ano | findstr :3000
netstat -ano | findstr :5001
```

**View service logs:**

```bash
make logs
```

### LLM Errors

**"Invalid API key":**

- Verify your API key in `services/ai/.env`
- Check you're using the correct provider (OpenAI vs Anthropic)

**"Rate limit exceeded":**

- Your API account has hit rate limits
- Wait and retry, or upgrade your API plan

**"Model not found":**

- Verify the model name in `.env` matches your provider
- Check your API account has access to the model

### Results Not Persisting

**Check volume mount:**

```bash
ls -la services/ai/results/
# Should show: data/ and index.json
```

**Check permissions:**

```bash
# Results directory should be writable
chmod -R 755 services/ai/results/
```

**View storage logs:**

```bash
cd docker && docker compose logs -f ai | grep -i result
```

### Frontend Build Errors

**Clear Next.js cache:**

```bash
cd services/web
rm -rf .next
npm run build
```

**Reinstall dependencies:**

```bash
cd services/web
rm -rf node_modules package-lock.json
npm install
```

### Still Having Issues?

1. Check the logs: `make logs`
2. Verify environment variables: `cat services/ai/.env`
3. Restart services: `make restart`
4. Rebuild from scratch: `make clean && make build && make start`
