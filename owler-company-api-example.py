"""Owler Company Intelligence API: A Quick Start Example.

See more at: https://apify.com/johnvc/owler-company-api?fpr=9n7kx3
Input schema: https://apify.com/johnvc/owler-company-api/input-schema?fpr=9n7kx3

This script shows how to call the Owler Company Intelligence API on Apify from
Python and read its structured JSON output. Every run returns one row per
company: revenue estimates, employee counts, funding totals, the named
competitor set, industry, headquarters location, and more.

Get your free Apify API key at: https://apify.com?fpr=9n7kx3

Examples:
  uv run python owler-company-api-example.py
  uv run python owler-company-api-example.py --example default
  uv run python owler-company-api-example.py --example competitor-map
  uv run python owler-company-api-example.py --example firmographics
"""

from __future__ import annotations

import argparse
import os
from typing import Any

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

ACTOR_ID = "johnvc/owler-company-api"


def _fetch(client: ApifyClient, company_urls: list[str]) -> list[dict[str, Any]]:
    """Run the Actor for a list of company URLs and return the dataset rows.

    Args:
        client: An authenticated Apify client.
        company_urls: Company profile URLs, or bare company slugs.

    Returns:
        One row per input that resolved. Rows carry `result_type` of either
        "company" or "error", so a failed input is visible rather than silent.
    """
    run_input: dict[str, Any] = {"companyUrls": company_urls}

    # apify-client 3.x returns a typed Run object, not a dict, so read the
    # dataset id as an attribute.
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    if run is None:
        raise SystemExit("The Actor run did not return a result.")

    print(f"Run id: {run.id}")
    return list(client.dataset(run.default_dataset_id).iterate_items())


def _split_rows(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Separate company rows from error rows."""
    companies = [r for r in rows if r.get("result_type") == "company"]
    errors = [r for r in rows if r.get("result_type") == "error"]
    return companies, errors


def _report_errors(errors: list[dict[str, Any]]) -> None:
    """Print any inputs that produced no company record."""
    for row in errors:
        print(
            f"  no record for {row.get('profileUrl') or '(unknown input)'}: "
            f"{row.get('error_message')}"
        )


def run_default(client: ApifyClient) -> None:
    """Cheap general quick-start showing the widest slice of the output."""
    # Two companies keeps this first run inexpensive. Billing is one charged
    # event per company record returned, so cost scales with the length of
    # companyUrls. Raise the list once you know your budget. A bare slug such
    # as "figma" works as shorthand for the full profile URL.
    rows = _fetch(
        client,
        [
            "https://www.owler.com/company/stripe",
            "figma",
        ],
    )
    companies, errors = _split_rows(rows)
    print(f"Returned {len(companies)} company record(s).\n")

    for company in companies:
        print(f"{company.get('companyName')}  ({company.get('domain')})")
        print(f"  Industry:    {company.get('industry')}")
        print(
            f"  HQ:          {company.get('city')}, "
            f"{company.get('state')}, {company.get('country')}"
        )
        print(f"  Founded:     {company.get('founded')}")
        print(f"  Ownership:   {company.get('ownership')}")
        print(
            f"  Revenue:     {company.get('estimatedAnnualRevenue')} "
            f"(estimate {company.get('revenue')})"
        )
        print(
            f"  Employees:   {company.get('estimatedEmployees')} "
            f"(estimate {company.get('employeeCount')})"
        )
        print(f"  Funding:     {company.get('totalFunding')}")
        print(f"  Acquisitions:{company.get('totalAcquisitions')}")
        print(f"  Competitors: {company.get('totalCompetitors')}")
        for rival in (company.get("competitors") or [])[:3]:
            print(f"    - {rival.get('name')}: {rival.get('profileUrl')}")
        print(f"  Profile:     {company.get('profileUrl')}")
        print(f"  Summary:     {company.get('summary')}\n")

    _report_errors(errors)


def run_competitor_map(client: ApifyClient) -> None:
    """Competitor intelligence in two passes: seed company, then its rivals.

    Pass one collects the seed company and its named competitor set. Pass two
    feeds the competitor profile URLs back in so you get full records for the
    rivals as well. That second pass is what turns a single lookup into a
    market map.
    """
    # One seed company, then only the top 2 competitors, so the whole recipe
    # costs 3 charged records. Raise FOLLOW_COUNT to map a wider market.
    follow_count = 2

    seed_rows = _fetch(client, ["https://www.owler.com/company/stripe"])
    seeds, seed_errors = _split_rows(seed_rows)
    _report_errors(seed_errors)
    if not seeds:
        raise SystemExit("The seed company returned no record.")

    seed = seeds[0]
    competitors = seed.get("competitors") or []
    print(
        f"{seed.get('companyName')} tracks "
        f"{seed.get('totalCompetitors')} competitor(s); "
        f"{len(competitors)} named in this record.\n"
    )

    follow_urls = [
        rival["profileUrl"]
        for rival in competitors[:follow_count]
        if rival.get("profileUrl")
    ]
    if not follow_urls:
        print("No competitor profile URLs to follow.")
        return

    print(f"Second pass on {len(follow_urls)} competitor profile(s)...\n")
    rival_rows = _fetch(client, follow_urls)
    rivals, rival_errors = _split_rows(rival_rows)

    for rival in rivals:
        print(f"{rival.get('companyName')}  ({rival.get('domain')})")
        print(f"  Industry:  {rival.get('industry')}")
        print(f"  Revenue:   {rival.get('estimatedAnnualRevenue')}")
        print(f"  Employees: {rival.get('estimatedEmployees')}")
        print(f"  Rivals:    {rival.get('totalCompetitors')}\n")

    _report_errors(rival_errors)


def run_firmographics(client: ApifyClient) -> None:
    """Firmographics and private company data for a single account.

    Prints the fields account segmentation and territory sizing usually run on:
    industry, employee band, revenue band, headquarters, ownership, year
    founded, SIC codes, and total funding raised. Fields the profile does not
    list come back as None, so check before you rely on one.
    """
    # A single company, so this recipe costs one charged record.
    rows = _fetch(client, ["https://www.owler.com/company/hubspot"])
    companies, errors = _split_rows(rows)

    for company in companies:
        print(f"{company.get('companyName')}")
        print(f"  Website:      {company.get('website')}")
        print(f"  Domain:       {company.get('domain')}")
        print(f"  Industries:   {company.get('industries')}")
        print(f"  SIC codes:    {company.get('sicCode')}")
        print(f"  Employees:    {company.get('estimatedEmployees')}")
        print(f"  Revenue band: {company.get('estimatedAnnualRevenue')}")
        print(f"  Revenue:      {company.get('revenue')}")
        print(f"  Funding:      {company.get('totalFunding')}")
        print(f"  Acquisitions: {company.get('totalAcquisitions')}")
        print(f"  Ownership:    {company.get('ownership')}")
        print(f"  Founded:      {company.get('founded')}")
        print(f"  Exchange:     {company.get('exchange')}")
        print(f"  Ticker:       {company.get('ticker')}")
        print(f"  Phone:        {company.get('phoneNumber')}")
        print(f"  CEO:          {company.get('ceoName')}")
        print(f"  Followers:    {company.get('followers')}")
        print(
            f"  HQ:           {company.get('streetAddress')}, "
            f"{company.get('city')}, {company.get('state')} "
            f"{company.get('zipcode')}, {company.get('country')}"
        )
        print(f"  Description:  {company.get('description')}\n")

    _report_errors(errors)


def main() -> None:
    """Dispatch one of the example recipes."""
    parser = argparse.ArgumentParser(
        description="Owler Company Intelligence API examples"
    )
    parser.add_argument(
        "--example",
        default="default",
        choices=["default", "competitor-map", "firmographics"],
        help="Which recipe to run (see the README Recipes section).",
    )
    args = parser.parse_args()

    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        raise SystemExit("Set APIFY_API_TOKEN in .env or the environment.")

    client = ApifyClient(token)
    dispatch = {
        "default": run_default,
        "competitor-map": run_competitor_map,
        "firmographics": run_firmographics,
    }
    dispatch[args.example](client)


if __name__ == "__main__":
    main()
