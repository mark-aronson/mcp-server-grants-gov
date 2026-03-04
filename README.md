# mcp-server-grants-gov

An MCP server for the [Grants.gov](https://www.grants.gov) API. Enables LLMs to search and retrieve federal grant opportunities without any authentication.

## Tools

### `grants_gov_search_opportunities`
Search for federal grant opportunities using keyword, agency, status, eligibility, funding category, or Assistance Listing Number (ALN). Returns paginated results.

| Parameter | Type | Description |
|-----------|------|-------------|
| `keyword` | string | Full-text search across titles and descriptions |
| `opp_num` | string | Exact opportunity number lookup |
| `agencies` | string[] | Agency code filters (e.g. `["HHS", "NSF", "DOE"]`) |
| `opp_statuses` | string[] | `forecasted`, `posted`, `closed`, `archived` |
| `eligibilities` | string[] | Eligibility code filters |
| `funding_categories` | string[] | Funding category code filters (e.g. `["HL", "ED"]`) |
| `aln` | string | Assistance Listing Number (e.g. `"93.268"`) |
| `rows` | int | Results per page, 1–100 (default: 25) |
| `start_record` | int | 1-indexed pagination offset (default: 1) |
| `response_format` | string | `markdown` (default) or `json` |

### `grants_gov_fetch_opportunity`
Fetch full details for a single opportunity by its numeric ID. Returns synopsis, award amounts, eligible applicant types, funding instruments, activity categories, ALNs, description, and attachments.

| Parameter | Type | Description |
|-----------|------|-------------|
| `opportunity_id` | int | Numeric opportunity ID (obtain from search results) |
| `response_format` | string | `markdown` (default) or `json` |

## Installation

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/your-org/mcp-server-grants-gov
cd mcp-server-grants-gov
uv sync
```

## Usage

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "grants-gov": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/mcp-server-grants-gov",
        "grants-gov-mcp"
      ]
    }
  }
}
```

### stdio (any MCP client)

```bash
uv run grants-gov-mcp
```

### HTTP (cloud/uvicorn)

```bash
PORT=8000 uv run grants-gov-mcp
```

## Development

Install in editable mode so changes take effect immediately:

```bash
uv pip install -e .
```
