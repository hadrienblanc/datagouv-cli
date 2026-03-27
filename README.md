# CLI-Gouv

CLI and MCP server to interact with [data.gouv.fr](https://www.data.gouv.fr/) - the French Open Data platform.

## Installation

```bash
uv tool install datagouv-cli
```

## CLI Usage

```bash
# Show help
datagouv-cli --help

# Search datasets
datagouv-cli search datasets "immobilier"
datagouv-cli search datasets "population" --org INSEE

# Get dataset info
datagouv-cli dataset show <dataset-id>

# List resources
datagouv-cli dataset resources <dataset-id>

# Get metrics
datagouv-cli dataset metrics <dataset-id>

# Query tabular data (CSV/Excel)
datagouv-cli resource query <resource-id> --where "code_postal = '75001'"
datagouv-cli resource schema <resource-id>

# Search dataservices (external APIs)
datagouv-cli search dataservices "adresse"
datagouv-cli dataservice openapi <dataservice-id>
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
datagouv-cli mcp

# Avec transport SSE
datagouv-cli mcp --transport sse --port 8080
```

### Configurer avec Claude Desktop

Ajouter dans la config Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json` sur macOS) :

```json
{
  "mcpServers": {
    "datagouv": {
      "command": "datagouv-cli",
      "args": ["mcp"]
    }
  }
}
```

### Configurer avec Claude Code

```bash
claude mcp add datagouv -- datagouv-cli mcp
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
uv run datagouv-cli --help

# Run MCP server locally (stdio)
uv run datagouv-cli mcp
```

## APIs Used

| API | Base URL | Purpose |
|-----|----------|---------|
| Main API | `https://www.data.gouv.fr/api/1/` | Datasets, resources, organizations |
| Tabular API | `https://tabular-api.data.gouv.fr/api/v1/` | Query CSV/Excel data |
| Metrics API | `https://stats.data.gouv.fr/api/v1/` | Views, downloads statistics |

## License

MIT
