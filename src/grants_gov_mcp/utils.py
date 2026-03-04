import json
from typing import Any

import httpx

SEARCH2_URL = "https://api.grants.gov/v1/api/search2"
FETCH_OPPORTUNITY_URL = "https://api.grants.gov/v1/api/fetchOpportunity"
REQUEST_TIMEOUT = 30.0


async def make_search2_request(payload: dict[str, Any]) -> dict[str, Any]:
    """POST the payload to the grants.gov search2 endpoint and return parsed JSON."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            SEARCH2_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()


async def make_fetch_opportunity_request(opportunity_id: int) -> dict[str, Any]:
    """POST to the grants.gov fetchOpportunity endpoint and return parsed JSON."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            FETCH_OPPORTUNITY_URL,
            json={"opportunityId": opportunity_id},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()


def format_opportunity_detail_markdown(data: dict[str, Any]) -> str:
    """Format a full fetchOpportunity data object into Markdown."""
    title = data.get("opportunityTitle", "Untitled")
    number = data.get("opportunityNumber", "N/A")
    opp_id = data.get("id", "N/A")
    agency_code = data.get("owningAgencyCode", "N/A")

    synopsis: dict[str, Any] = data.get("synopsis", {})
    agency_name = synopsis.get("agencyName", agency_code)
    posting_date = _format_date(synopsis.get("postingDate"))
    response_date = _format_date(synopsis.get("responseDate") or synopsis.get("archiveDate"))
    response_date_label = "Response Date" if synopsis.get("responseDate") else "Archive Date"
    cost_sharing = synopsis.get("costSharingOrMatchingInd", False)
    award_ceiling = synopsis.get("awardCeiling") or synopsis.get("awardCeilingFormatted", "N/A")
    award_floor = synopsis.get("awardFloor") or synopsis.get("awardFloorFormatted", "N/A")
    expected_awards = synopsis.get("numberOfAwards", "N/A")
    description = synopsis.get("synopsisDesc", "")

    # Collect list fields
    applicant_types: list[str] = [
        at.get("description", at.get("applicantType", ""))
        for at in synopsis.get("applicantTypes", [])
    ]
    funding_instruments: list[str] = [
        fi.get("description", fi.get("fundingInstrumentType", ""))
        for fi in synopsis.get("fundingInstruments", [])
    ]
    activity_categories: list[str] = [
        ac.get("description", ac.get("fundingActivityCategory", ""))
        for ac in synopsis.get("fundingActivityCategories", [])
    ]
    alns: list[str] = [
        f"{a.get('alnNumber', '')} — {a.get('programTitle', '')}".strip(" —")
        for a in data.get("alns", [])
    ]
    attachments: list[str] = [
        f.get("folderName", "") or f.get("title", "")
        for folder in data.get("synopsisAttachmentFolders", [])
        for f in ([folder] if isinstance(folder, dict) else [])
        if f.get("folderName") or f.get("title")
    ]

    lines = [
        f"## {title}",
        f"",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| **Opportunity #** | {number} |",
        f"| **ID** | {opp_id} |",
        f"| **Agency** | {agency_name} ({agency_code}) |",
        f"| **Posted** | {posting_date} |",
        f"| {response_date_label} | {response_date} |",
        f"| **Award Ceiling** | {award_ceiling} |",
        f"| **Award Floor** | {award_floor} |",
        f"| **Expected Awards** | {expected_awards} |",
        f"| **Cost Sharing** | {'Yes' if cost_sharing else 'No'} |",
        f"",
    ]

    if applicant_types:
        lines += ["**Eligible Applicants:**", ""] + [f"- {t}" for t in applicant_types if t] + [""]
    if funding_instruments:
        lines += ["**Funding Instruments:**", ""] + [f"- {i}" for i in funding_instruments if i] + [""]
    if activity_categories:
        lines += ["**Activity Categories:**", ""] + [f"- {c}" for c in activity_categories if c] + [""]
    if alns:
        lines += ["**Assistance Listing Numbers (ALN):**", ""] + [f"- {a}" for a in alns if a] + [""]
    if description:
        lines += ["**Description:**", "", description.strip(), ""]
    if attachments:
        lines += ["**Attachments:**", ""] + [f"- {a}" for a in attachments if a] + [""]

    return "\n".join(lines)


def handle_api_error(e: Exception) -> str:
    """Return a clear, actionable error message for common HTTP and network failures."""
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 400:
            return (
                "Error: Bad request — one or more parameters are invalid. "
                "Check that agency codes, eligibility codes, and funding category codes are correct."
            )
        if status == 429:
            return "Error: Rate limit exceeded. Please wait before retrying."
        if status >= 500:
            return f"Error: Grants.gov server error ({status}). The API may be temporarily unavailable."
        return f"Error: API request failed with status {status}."
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. The Grants.gov API may be slow — try again or reduce the number of rows."
    if isinstance(e, httpx.ConnectError):
        return "Error: Could not connect to Grants.gov. Check your internet connection."
    return f"Error: Unexpected error — {type(e).__name__}: {e}"


def _format_date(date_str: str | None) -> str:
    """Return date string as-is or 'N/A' if missing."""
    return date_str if date_str else "N/A"


def format_opportunity_markdown(opp: dict[str, Any]) -> str:
    """Format a single opportunity dict into a Markdown block."""
    title = opp.get("title", "Untitled")
    number = opp.get("number", "N/A")
    agency = opp.get("agencyName", opp.get("agencyCode", "N/A"))
    status = opp.get("oppStatus", "N/A")
    open_date = _format_date(opp.get("openDate"))
    close_date = _format_date(opp.get("closeDate"))
    doc_type = opp.get("docType", "N/A")
    aln_list = opp.get("alnlist", "")

    lines = [
        f"### {title}",
        f"- **Opportunity #**: {number}",
        f"- **Agency**: {agency}",
        f"- **Status**: {status}",
        f"- **Open Date**: {open_date}",
        f"- **Close Date**: {close_date}",
        f"- **Type**: {doc_type}",
    ]
    if aln_list:
        lines.append(f"- **ALN**: {aln_list}")
    return "\n".join(lines)


def format_search_results_markdown(
    data: dict[str, Any],
    rows: int,
    start_record: int,
) -> str:
    """Format the full search2 response data as Markdown."""
    hit_count: int = data.get("hitCount", 0)
    opp_hits: list[dict] = data.get("oppHits", [])

    if not opp_hits:
        return "No grant opportunities found matching your search criteria."

    shown = len(opp_hits)
    end_record = start_record + shown - 1
    has_more = hit_count > end_record

    lines = [
        f"## Grants.gov Search Results",
        f"",
        f"**Total matches**: {hit_count:,}  |  "
        f"**Showing**: {start_record}–{end_record}",
        f"",
    ]

    for opp in opp_hits:
        lines.append(format_opportunity_markdown(opp))
        lines.append("")

    if has_more:
        next_start = end_record + 1
        lines.append(
            f"---\n*{hit_count - end_record:,} more results available. "
            f"Use `start_record={next_start}` and `rows={rows}` to fetch the next page.*"
        )

    return "\n".join(lines)


def build_search_payload(
    keyword: str | None,
    opp_num: str | None,
    agencies: list[str] | None,
    opp_statuses: list[str] | None,
    eligibilities: list[str] | None,
    funding_categories: list[str] | None,
    aln: str | None,
    rows: int,
    start_record: int,
) -> dict[str, Any]:
    """Build the JSON payload for a search2 POST request."""
    payload: dict[str, Any] = {
        "rows": rows,
        "startRecord": start_record,
    }
    if keyword:
        payload["keyword"] = keyword
    if opp_num:
        payload["oppNum"] = opp_num
    if agencies:
        payload["agencies"] = "|".join(agencies)
    if opp_statuses:
        payload["oppStatuses"] = "|".join(opp_statuses)
    if eligibilities:
        payload["eligibilities"] = "|".join(eligibilities)
    if funding_categories:
        payload["fundingCategories"] = "|".join(funding_categories)
    if aln:
        payload["aln"] = aln
    return payload
