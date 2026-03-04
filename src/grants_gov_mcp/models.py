from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class OppStatus(str, Enum):
    """Opportunity status codes for filtering grant searches."""
    FORECASTED = "forecasted"
    POSTED = "posted"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


class FetchOpportunityInput(BaseModel):
    """Input model for the grants.gov fetchOpportunity endpoint."""
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    opportunity_id: int = Field(
        ...,
        description="Numeric ID of the grant opportunity to retrieve (e.g., 289999). Obtain IDs from grants_gov_search_opportunities results.",
        gt=0,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for the raw API data object.",
    )


class SearchGrantsInput(BaseModel):
    """Input model for the grants.gov search2 endpoint."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    keyword: Optional[str] = Field(
        default=None,
        description="Keyword to search across opportunity titles, descriptions, and related text (e.g., 'climate research', 'maternal health').",
        max_length=500,
    )
    opp_num: Optional[str] = Field(
        default=None,
        description="Specific opportunity number to look up (e.g., 'HHS-2024-ACF-OCC-0181').",
        max_length=200,
    )
    agencies: Optional[List[str]] = Field(
        default=None,
        description=(
            "List of agency codes to filter results (e.g., ['HHS', 'DOE', 'NSF']). "
            "Use grants_gov_get_filter_options to discover available agency codes."
        ),
    )
    opp_statuses: Optional[List[OppStatus]] = Field(
        default=None,
        description=(
            "Opportunity statuses to include. Allowed values: 'forecasted', 'posted', 'closed', 'archived'. "
            "Defaults to all statuses if not specified."
        ),
    )
    eligibilities: Optional[List[str]] = Field(
        default=None,
        description=(
            "Eligibility codes to filter by (e.g., ['25', '20'] for state governments and private institutions). "
            "Use grants_gov_get_filter_options to discover available eligibility codes."
        ),
    )
    funding_categories: Optional[List[str]] = Field(
        default=None,
        description=(
            "Funding category codes to filter by (e.g., ['HL', 'ED'] for health and education). "
            "Use grants_gov_get_filter_options to discover available category codes."
        ),
    )
    aln: Optional[str] = Field(
        default=None,
        description="Assistance Listing Number (formerly CFDA number) to filter by (e.g., '93.268').",
        max_length=50,
    )
    rows: int = Field(
        default=25,
        description="Number of results to return per page (1–100).",
        ge=1,
        le=100,
    )
    start_record: int = Field(
        default=1,
        description="1-indexed starting record for pagination. Use with rows to page through results.",
        ge=1,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable structured data.",
    )
