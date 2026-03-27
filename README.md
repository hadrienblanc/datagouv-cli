# CLI-Gouv

CLI to interact with [data.gouv.fr](https://www.data.gouv.fr/) - the French Open Data platform.

## Installation

```bash
# With uv (recommended)
uv tool install cli-gouv

# With pipx
pipx install cli-gouv

# With pip
pip install cli-gouv
```

## Usage

```bash
# Show help
cli-gouv --help

# Search datasets
cli-gouv search "immobilier"

# Get dataset info
cli-gouv dataset show <dataset-id>

# List resources
cli-gouv dataset resources <dataset-id>

# Query resource data
cli-gouv resource query <resource-id> "code_postal = 75001"
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
```

## License

MIT
