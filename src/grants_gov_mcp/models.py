from enum import Enum
from typing import Any, Optional, List

from pydantic import BaseModel, Field, ConfigDict


class Agency(str, Enum):
    """Top-level agency codes for filtering grant searches."""
    AMERICORPS = "AC"
    USDA = "USDA"
    DOC = "DOC"
    DOD = "DOD"
    ED = "ED"
    DOE = "DOE"
    DOE_OFFICE_OF_SCIENCE = "PAMS"
    HHS = "HHS"
    DHS = "DHS"
    HUD = "HUD"
    DOJ = "USDOJ"
    DOL = "DOL"
    DOS = "DOS"
    DOI = "DOI"
    TREASURY = "USDOT"
    DOT = "DOT"
    VA = "VA"
    EPA = "EPA"
    IMLS = "IMLS"
    MCC = "MCC"
    NASA = "NASA"
    NEA = "NEA"
    NEH = "NEH"
    ONDCP = "ONDCP"
    NSF = "NSF"


# Mapping from top-level agency code to its sub-agency codes.
# Used in to_payload() to expand parent codes to all sub-agencies.
AGENCY_SUBAGENCIES: dict[str, list[str]] = {
    "USDA": ["USDA-FS", "USDA-NIFA", "USDA-RBCS", "USDA-RHS", "USDA-RUS"],
    "DOC": ["DOC", "DOC-DOCNOAAERA", "DOC-EDA", "DOC-NIST"],
    "DOD": [
        "DOD", "DOD-AF347CS", "DOD-AFRL", "DOD-AFRL-AFRLDET8", "DOD-AFRL-RW",
        "DOD-AFOSR", "DOD-AMC", "DOD-AMC-ACCAPGD", "DOD-AMC-ACCAPGN", "DOD-AMC-ACCRI",
        "DOD-AMRAA", "DOD-COE-ERDC", "DOD-DARPA-BTO", "DOD-DARPA-DSO", "DOD-DARPA-I2O",
        "DOD-DARPA-TTO", "DOD-DTRA", "DOD-NGIA", "DOD-OEA", "DOD-ONR", "DOD-ONR-AIR",
        "DOD-ONR-NRL", "DOD-ONR-SEA-CRANE", "DOD-ONR-SEA-N00178", "DOD-ONR-SEA-NSWFCRD",
        "DOD-ONR-SUP", "DOD-USAFA", "DOD-WHS",
    ],
    "DOE": ["DOE-ARPAE", "DOE-GFO", "DOE-01", "DOE-ID", "DOE-NETL", "DOE-NNSA"],
    "PAMS": ["PAMS-SC"],
    "HHS": [
        "HHS-ACF-CB", "HHS-ACF-OFVPS", "HHS-ACL", "HHS-AHRQ", "HHS-ASPR",
        "HHS-CDC-GHC", "HHS-CDC-HHSCDCERA", "HHS-CDC-NCBDDD", "HHS-CDC-NCEZID",
        "HHS-CDC-NCIPC", "HHS-CDC-NCIRD", "HHS-CDC-OPHPR", "HHS-CMS", "HHS-FDA",
        "HHS-HRSA", "HHS-IHS", "HHS-NIH11", "HHS-OPHS", "HHS-OS-ASPR",
        "HHS-OS-ONC", "HHS-SAMHS-SAMHSA",
    ],
    "DHS": ["DHS-USCG"],
    "USDOJ": ["USDOJ-BOP-NIC", "USDOJ-OJP-BJA", "USDOJ-OJP-OJJDP", "USDOJ-OJP-OVC"],
    "DOL": ["DOL-ETA", "DOL-ETA-VETS", "DOL-ILAB", "DOL-VETS"],
    "DOS": [
        "DOS-ALB", "DOS-AGO", "DOS-ARG", "DOS-AUS", "DOS-AZE", "DOS-BGD", "DOS-BEN",
        "DOS-CHN", "DOS-COD", "DOS-CPV", "DOS-CYP", "DOS-DJI", "DOS-DOM", "DOS-DRL",
        "DOS-ECA", "DOS-EGY", "DOS-ESP", "DOS-EUR", "DOS-GAB", "DOS-GEO", "DOS-GFS",
        "DOS-GHSD", "DOS-GRC", "DOS-GTIP", "DOS-IND", "DOS-IDN", "DOS-INL", "DOS-ISN",
        "DOS-ITA", "DOS-JPN", "DOS-KAZ", "DOS-LVA", "DOS-MEX", "DOS-MKD", "DOS-MOZ",
        "DOS-MUS", "DOS-NLD", "DOS-PHL", "DOS-PRM", "DOS-SLE", "DOS-SRB", "DOS-TUN",
        "DOS-USEU", "DOS-USUN", "DOS-VEN", "DOS-ZAF", "DOS-ZWE",
    ],
    "DOI": ["DOI-BIA", "DOI-BLM", "DOI-BOR", "DOI-FWS", "DOI-FWS-REG4", "DOI-IBC", "DOI-NPS", "DOI-USGS1"],
    "USDOT": ["USDOT-GCR"],
    "DOT": ["DOT-FAA-FAA ARG", "DOT-FAA-FAA COE-AJFE", "DOT-FAA-FAA COE-FAA JAMS", "DOT-FAA-FAA COE-TTHP", "DOT-FTA", "DOT-MA", "DOT-NHTSA"],
    "VA": ["VA-CSHF", "VA-HPGPDP", "VA-NCA", "VA-NCAC", "VA-NVSP", "VA-VLGP"],
    "NASA": ["NASA", "NASA-HQ"],
}


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
            "Agency codes to filter results. Accepts top-level codes (e.g., 'USDA', 'DOE', 'NSF') "
            "which automatically expand to all sub-agencies, or specific sub-agency codes "
            "(e.g., 'USDA-NIFA', 'DOE-ARPAE') for narrower filtering. Both can be mixed. "
            "Note: DOE Office of Science uses top-level code 'PAMS'."
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

    def to_payload(self) -> dict[str, Any]:
        """Build the JSON payload for a search2 POST request."""
        payload: dict[str, Any] = {
            "rows": self.rows,
            "startRecord": self.start_record,
        }
        if self.keyword:
            payload["keyword"] = self.keyword
        if self.opp_num:
            payload["oppNum"] = self.opp_num
        if self.agencies:
            codes: list[str] = []
            seen: set[str] = set()
            for a in self.agencies:
                for code in AGENCY_SUBAGENCIES.get(a, [a]):
                    if code not in seen:
                        seen.add(code)
                        codes.append(code)
            payload["agencies"] = "|".join(codes)
        if self.opp_statuses:
            payload["oppStatuses"] = "|".join(s.value for s in self.opp_statuses)
        if self.eligibilities:
            payload["eligibilities"] = "|".join(self.eligibilities)
        if self.funding_categories:
            payload["fundingCategories"] = "|".join(self.funding_categories)
        if self.aln:
            payload["aln"] = self.aln
        return payload
