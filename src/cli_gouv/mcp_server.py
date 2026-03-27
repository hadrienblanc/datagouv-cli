"""MCP Server exposing data.gouv.fr as tools for LLMs."""

import json
from contextlib import asynccontextmanager
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from cli_gouv.api.client import DataGouvAPIError
from cli_gouv.api.dataservices import DataservicesClient, OpenAPIFetchError
from cli_gouv.api.datasets import DatasetsClient
from cli_gouv.api.metrics import MetricsClient
from cli_gouv.api.resources import ResourcesClient

# Shared HTTP client for connection pooling across MCP tool calls
_shared_http_client: httpx.AsyncClient | None = None


async def _get_shared_client() -> httpx.AsyncClient:
    """Get or create the shared HTTP client."""
    global _shared_http_client
    if _shared_http_client is None or _shared_http_client.is_closed:
        _shared_http_client = httpx.AsyncClient(timeout=30.0)
    return _shared_http_client


@asynccontextmanager
async def _use_client(client_class: type):
    """Create an API client that reuses the shared HTTP connection pool."""
    client = client_class()
    client._client = await _get_shared_client()
    try:
        yield client
    finally:
        # Don't close — the shared client stays alive
        pass


async def _shutdown_client() -> None:
    """Close the shared HTTP client on server shutdown."""
    global _shared_http_client
    if _shared_http_client and not _shared_http_client.is_closed:
        await _shared_http_client.aclose()
        _shared_http_client = None


mcp = FastMCP(
    "datagouv",
    instructions=(
        "Serveur MCP pour data.gouv.fr, la plateforme open data de la France. "
        "Permet de rechercher des jeux de données, consulter des ressources, "
        "interroger des données tabulaires, et explorer des APIs externes."
    ),
)


def _json_result(data: Any) -> str:
    """Serialize result to JSON string for MCP response."""
    return json.dumps(data, indent=2, ensure_ascii=False)


def _error_result(message: str) -> str:
    """Format an error message as JSON."""
    return json.dumps({"error": message}, ensure_ascii=False)


# --- Dataset tools ---


@mcp.tool()
async def search_datasets(
    query: str,
    page: int = 1,
    page_size: int = 20,
    organization: str | None = None,
    tag: str | None = None,
    sort: str | None = None,
) -> str:
    """Rechercher des jeux de données sur data.gouv.fr.

    Args:
        query: Termes de recherche (ex: "population", "immobilier", "énergie").
        page: Numéro de page (commence à 1).
        page_size: Nombre de résultats par page (max 100).
        organization: Filtrer par organisation (ID ou nom).
        tag: Filtrer par tag.
        sort: Tri (ex: "-created", "title", "-views").

    Returns:
        Liste de datasets avec pagination.
    """
    try:
        async with _use_client(DatasetsClient) as client:
            result = await client.search(
                query=query,
                page=page,
                page_size=page_size,
                organization=organization,
                tag=tag,
                sort=sort,
            )
        return _json_result(result)
    except (ValueError, DataGouvAPIError) as e:
        return _error_result(str(e))


@mcp.tool()
async def get_dataset_info(dataset_id: str) -> str:
    """Obtenir les informations détaillées d'un jeu de données.

    Args:
        dataset_id: Identifiant ou slug du dataset (ex: "population-francaise").

    Returns:
        Métadonnées complètes : titre, description, organisation, licence, tags, ressources.
    """
    try:
        async with _use_client(DatasetsClient) as client:
            result = await client.get_dataset(dataset_id)
        return _json_result(result)
    except (ValueError, DataGouvAPIError) as e:
        return _error_result(str(e))


@mcp.tool()
async def list_resources(dataset_id: str) -> str:
    """Lister les ressources (fichiers) d'un jeu de données.

    Args:
        dataset_id: Identifiant ou slug du dataset.

    Returns:
        Liste des ressources avec titre, format, taille, URL de téléchargement.
    """
    try:
        async with _use_client(DatasetsClient) as client:
            result = await client.list_resources(dataset_id)
        return _json_result(result)
    except (ValueError, DataGouvAPIError) as e:
        return _error_result(str(e))


# --- Resource tools ---


@mcp.tool()
async def query_resource_data(
    resource_id: str,
    where: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> str:
    """Interroger les données tabulaires d'une ressource (CSV/XLS) via le Tabular API.

    Args:
        resource_id: Identifiant de la ressource.
        where: Clause WHERE SQL-like (ex: "code_postal = '75001'").
        page: Numéro de page.
        page_size: Nombre de lignes par page (max 200).

    Returns:
        Données tabulaires avec pagination.
    """
    try:
        async with _use_client(ResourcesClient) as client:
            result = await client.query_tabular(
                resource_id=resource_id,
                query=where,
                page=page,
                page_size=page_size,
            )
        return _json_result(result)
    except (ValueError, DataGouvAPIError) as e:
        return _error_result(str(e))


@mcp.tool()
async def get_resource_schema(resource_id: str) -> str:
    """Obtenir le schéma (colonnes et types) d'une ressource tabulaire.

    Args:
        resource_id: Identifiant de la ressource.

    Returns:
        Schéma avec noms de colonnes, types et descriptions.
    """
    try:
        async with _use_client(ResourcesClient) as client:
            result = await client.get_schema(resource_id)
        return _json_result(result)
    except (ValueError, DataGouvAPIError) as e:
        return _error_result(str(e))


# --- Dataservice tools ---


@mcp.tool()
async def search_dataservices(
    query: str,
    page: int = 1,
    page_size: int = 20,
    organization: str | None = None,
    tag: str | None = None,
) -> str:
    """Rechercher des dataservices (APIs externes) référencés sur data.gouv.fr.

    Args:
        query: Termes de recherche (ex: "adresse", "géocodage").
        page: Numéro de page.
        page_size: Nombre de résultats par page (max 100).
        organization: Filtrer par organisation.
        tag: Filtrer par tag.

    Returns:
        Liste de dataservices avec pagination.
    """
    try:
        async with _use_client(DataservicesClient) as client:
            result = await client.search(
                query=query,
                page=page,
                page_size=page_size,
                organization=organization,
                tag=tag,
            )
        return _json_result(result)
    except (ValueError, DataGouvAPIError) as e:
        return _error_result(str(e))


@mcp.tool()
async def get_dataservice_info(dataservice_id: str) -> str:
    """Obtenir les informations détaillées d'un dataservice (API externe).

    Args:
        dataservice_id: Identifiant du dataservice.

    Returns:
        Métadonnées : titre, description, URL de base, URL OpenAPI, licence.
    """
    try:
        async with _use_client(DataservicesClient) as client:
            result = await client.get_dataservice(dataservice_id)
        return _json_result(result)
    except (ValueError, DataGouvAPIError) as e:
        return _error_result(str(e))


@mcp.tool()
async def get_openapi_spec(dataservice_id: str) -> str:
    """Récupérer la spécification OpenAPI d'un dataservice.

    Args:
        dataservice_id: Identifiant du dataservice.

    Returns:
        Spécification OpenAPI complète (endpoints, méthodes, paramètres).
    """
    try:
        async with _use_client(DataservicesClient) as client:
            result = await client.get_openapi_spec(dataservice_id)
        return _json_result(result)
    except (ValueError, OpenAPIFetchError, DataGouvAPIError) as e:
        return _error_result(str(e))


# --- Metrics tools ---


@mcp.tool()
async def get_metrics(
    dataset_id: str | None = None,
    resource_id: str | None = None,
    limit: int = 12,
) -> str:
    """Obtenir les statistiques de consultation (vues, téléchargements).

    Args:
        dataset_id: Identifiant du dataset (optionnel, au moins un ID requis).
        resource_id: Identifiant de la ressource (optionnel, au moins un ID requis).
        limit: Nombre de mois à retourner (max 100).

    Returns:
        Statistiques mensuelles de vues et téléchargements.
    """
    try:
        async with _use_client(MetricsClient) as client:
            result = await client.get_combined_metrics(
                dataset_id=dataset_id,
                resource_id=resource_id,
                limit=limit,
            )
        return _json_result(result)
    except (ValueError, DataGouvAPIError) as e:
        return _error_result(str(e))
