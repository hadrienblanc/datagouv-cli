# CLI-Gouv

CLI to interact with [data.gouv.fr](https://www.data.gouv.fr/) - the French Open Data platform.

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
```

## APIs Used

| API | Base URL | Purpose |
|-----|----------|---------|
| Main API | `https://www.data.gouv.fr/api/1/` | Datasets, resources, organizations |
| Tabular API | `https://tabular-api.data.gouv.fr/api/v1/` | Query CSV/Excel data |
| Metrics API | `https://stats.data.gouv.fr/api/v1/` | Views, downloads statistics |

## License

MIT
