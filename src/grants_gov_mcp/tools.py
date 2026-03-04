import json
from typing import Any

from fastmcp import FastMCP

from .models import FetchOpportunityInput, ResponseFormat, SearchGrantsInput
from .utils import (
    build_search_payload,
    format_opportunity_detail_markdown,
    format_search_results_markdown,
    handle_api_error,
    make_fetch_opportunity_request,
    make_search2_request,
)


def register_tools(mcp: FastMCP) -> None:
    """Register all grants.gov tools on the MCP server."""

    @mcp.tool(
        name="grants_gov_search_opportunities",
        annotations={
            "title": "Search Grants.gov Opportunities",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def grants_gov_search_opportunities(params: SearchGrantsInput) -> str:
        """Search for federal grant opportunities on Grants.gov.

        Queries the Grants.gov search2 API to find funding opportunities matching
        the given criteria. Supports full-text keyword search and filtering by
        agency, status, eligibility, and funding category. Returns paginated results.

        No authentication is required.

        Args:
            params (SearchGrantsInput): Validated search parameters containing:
                - keyword (Optional[str]): Full-text search across titles and descriptions
                - opp_num (Optional[str]): Exact opportunity number lookup
                - agencies (Optional[List[str]]): Agency code filters (e.g., ['HHS', 'NSF'])
                - opp_statuses (Optional[List[OppStatus]]): Status filters: 'forecasted', 'posted', 'closed', 'archived'
                - eligibilities (Optional[List[str]]): Eligibility code filters
                - funding_categories (Optional[List[str]]): Funding category code filters
                - aln (Optional[str]): Assistance Listing Number filter (e.g., '93.268')
                - rows (int): Results per page, 1–100 (default: 25)
                - start_record (int): 1-indexed pagination offset (default: 1)
                - response_format (ResponseFormat): 'markdown' or 'json' (default: 'markdown')

        Returns:
            str: Search results in the requested format.

            Markdown format includes:
            - Total match count and current page range
            - Per-opportunity: title, number, agency, status, open/close dates, type, ALN
            - Pagination hint with next start_record if more results exist

            JSON format schema:
            {
                "hit_count": int,           # Total matching opportunities
                "start_record": int,        # Current page start (1-indexed)
                "rows_requested": int,      # Rows requested
                "returned": int,            # Opportunities in this response
                "has_more": bool,           # Whether additional pages exist
                "next_start_record": int | null,  # start_record for next page
                "opportunities": [
                    {
                        "id": str,
                        "number": str,
                        "title": str,
                        "agencyCode": str,
                        "agencyName": str,
                        "openDate": str,
                        "closeDate": str,
                        "oppStatus": str,
                        "docType": str,
                        "alnlist": str
                    }
                ],
                "filter_options": {
                    "opp_statuses": [...],      # Available statuses with counts
                    "eligibilities": [...],      # Available eligibility types with counts
                    "funding_categories": [...], # Available categories with counts
                    "agencies": [...]            # Available agencies with counts
                }
            }

        Examples:
            - Find open NIH health grants: keyword='health', agencies=['HHS'], opp_statuses=['posted']
            - Browse all posted opportunities: opp_statuses=['posted'], rows=50
            - Look up a specific grant: opp_num='HHS-2024-ACF-OCC-0181'
            - Find education grants: funding_categories=['ED']
            - Paginate results: rows=25, start_record=26 (for second page)

        Error Handling:
            - Returns "No grant opportunities found..." if search has zero results
            - Returns "Error: Bad request..." if filter codes are invalid
            - Returns "Error: Request timed out..." on slow responses
        """
        try:
            payload = build_search_payload(
                keyword=params.keyword,
                opp_num=params.opp_num,
                agencies=[a.value if hasattr(a, "value") else a for a in params.agencies]
                if params.agencies
                else None,
                opp_statuses=[s.value for s in params.opp_statuses]
                if params.opp_statuses
                else None,
                eligibilities=params.eligibilities,
                funding_categories=params.funding_categories,
                aln=params.aln,
                rows=params.rows,
                start_record=params.start_record,
            )

            response = await make_search2_request(payload)

            # The API wraps results in a `data` key
            data: dict[str, Any] = response.get("data", response)

            hit_count: int = data.get("hitCount", 0)
            opp_hits: list[dict] = data.get("oppHits", [])
            returned = len(opp_hits)
            end_record = params.start_record + returned - 1
            has_more = hit_count > end_record
            next_start = end_record + 1 if has_more else None

            if params.response_format == ResponseFormat.JSON:
                result: dict[str, Any] = {
                    "hit_count": hit_count,
                    "start_record": params.start_record,
                    "rows_requested": params.rows,
                    "returned": returned,
                    "has_more": has_more,
                    "next_start_record": next_start,
                    "opportunities": opp_hits,
                    "filter_options": {
                        "opp_statuses": data.get("oppStatusOptions", []),
                        "eligibilities": data.get("eligibilities", []),
                        "funding_categories": data.get("fundingCategories", []),
                        "agencies": data.get("agencies", []),
                    },
                }
                return json.dumps(result, indent=2)

            return format_search_results_markdown(data, params.rows, params.start_record)

        except Exception as e:
            return handle_api_error(e)

    @mcp.tool(
        name="grants_gov_fetch_opportunity",
        annotations={
            "title": "Fetch Grant Opportunity Details",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def grants_gov_fetch_opportunity(params: FetchOpportunityInput) -> str:
        """Fetch full details for a single grant opportunity by its numeric ID.

        Retrieves comprehensive information about a specific Grants.gov opportunity
        including synopsis, eligibility, award amounts, contact info, funding
        instruments, activity categories, ALNs, and attachments.

        Use grants_gov_search_opportunities first to find opportunity IDs.
        No authentication is required.

        Args:
            params (FetchOpportunityInput): Input parameters containing:
                - opportunity_id (int): Numeric opportunity ID (e.g., 289999)
                - response_format (ResponseFormat): 'markdown' or 'json' (default: 'markdown')

        Returns:
            str: Opportunity details in the requested format.

            Markdown format includes:
            - Summary table: number, agency, posted/response dates, award ceiling/floor,
              expected awards, cost sharing requirement
            - Eligible applicant types
            - Funding instruments
            - Activity categories
            - Assistance Listing Numbers (ALN)
            - Description text
            - Attachment folder names

            JSON format returns the raw `data` object from the API with all fields.

        Examples:
            - Get details for opportunity 289999: opportunity_id=289999
            - Get machine-readable data: opportunity_id=289999, response_format='json'

        Error Handling:
            - Returns "Error: Opportunity not found..." if the ID does not exist
            - Returns "Error: Request timed out..." on slow responses
        """
        try:
            response = await make_fetch_opportunity_request(params.opportunity_id)
            data: dict[str, Any] = response.get("data", response)

            errors = data.get("errorMessages", [])
            if errors or not data.get("opportunityTitle"):
                return f"Error: Opportunity with ID {params.opportunity_id} was not found."

            if params.response_format == ResponseFormat.JSON:
                return json.dumps(data, indent=2)

            return format_opportunity_detail_markdown(data)

        except Exception as e:
            if isinstance(e, Exception) and "404" in str(e):
                return f"Error: Opportunity with ID {params.opportunity_id} was not found."
            return handle_api_error(e)
