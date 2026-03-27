# CLI-Gouv

CLI and MCP server to interact with [data.gouv.fr](https://www.data.gouv.fr/) - the French Open Data platform.

## Installation

```bash
# With uv (recommended)
uv tool install cli-gouv

# With pipx
pipx install cli-gouv

# With pip
pip install cli-gouv
```

## CLI Usage

```bash
# Show help
cli-gouv --help

# Search datasets
cli-gouv search datasets "immobilier"
cli-gouv search datasets "population" --org INSEE

# Get dataset info
cli-gouv dataset show <dataset-id>

# List resources
cli-gouv dataset resources <dataset-id>

# Get metrics
cli-gouv dataset metrics <dataset-id>

# Query tabular data (CSV/Excel)
cli-gouv resource query <resource-id> --where "code_postal = '75001'"
cli-gouv resource schema <resource-id>

# Search dataservices (external APIs)
cli-gouv search dataservices "adresse"
cli-gouv dataservice openapi <dataservice-id>
```

## MCP Server

This package includes an MCP (Model Context Protocol) server that exposes data.gouv.fr functionality to LLMs.

### Available Tools

| Tool | Description |
|------|-------------|
| `search_datasets` | Rechercher des jeux de données |
| `get_dataset_info` | Obtenir les détails d'un dataset |
| `list_resources` | Lister les ressources d'un dataset |
| `query_resource_data` | Interroger des données tabulaires (CSV/XLS) |
| `get_resource_schema` | Obtenir le schéma d'une ressource |
| `search_dataservices` | Rechercher des APIs externes |
| `get_dataservice_info` | Obtenir les détails d'un dataservice |
| `get_openapi_spec` | Récupérer la spécification OpenAPI |
| `get_metrics` | Statistiques de consultation (vues, téléchargements) |

### Lancer le serveur MCP

```bash
# Via la CLI (transport stdio par défaut)
cli-gouv mcp

# Avec transport SSE
cli-gouv mcp --transport sse --port 8080
```

### Configurer avec Claude Desktop

Ajouter dans la config Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json` sur macOS) :

```json
{
  "mcpServers": {
    "datagouv": {
      "command": "cli-gouv",
      "args": ["mcp"]
    }
  }
}
```

### Configurer avec Claude Code

```bash
claude mcp add datagouv -- cli-gouv mcp
```

## Development

```bash
# Clone and install
git clone https://github.com/hadrienblanc/datagouv-cli.git
cd datagouv-cli
uv sync

# Run tests
uv run pytest -v

# Run CLI locally
uv run cli-gouv --help

# Run MCP server locally (stdio)
uv run cli-gouv mcp
```

## APIs Used

| API | Base URL | Purpose |
|-----|----------|---------|
| Main API | `https://www.data.gouv.fr/api/1/` | Datasets, resources, organizations |
| Tabular API | `https://tabular-api.data.gouv.fr/api/v1/` | Query CSV/Excel data |
| Metrics API | `https://stats.data.gouv.fr/api/v1/` | Views, downloads statistics |

## License

MIT
