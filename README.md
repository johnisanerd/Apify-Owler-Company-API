# 🏢 Owler Company Intelligence API: competitor intelligence and private company data from a company URL

> Send company profile URLs, get back the named competitor set plus revenue estimates, employee counts, funding totals, industry, and headquarters. One row per company, as clean JSON.

**Actor page:** [apify.com/johnvc/owler-company-api](https://apify.com/johnvc/owler-company-api?fpr=9n7kx3)
**Input schema:** [apify.com/johnvc/owler-company-api/input-schema](https://apify.com/johnvc/owler-company-api/input-schema?fpr=9n7kx3)

Most company data tools tell you what a company is. This one also tells you who it competes with. Every record carries a competitor count and the **named competitor set**, each entry with its own profile URL you can feed straight back in, which is the layer competitor intelligence and market mapping actually run on. Alongside that you get the firmographics: industry classifications, employee count and band, revenue estimate and band, total funding raised, acquisitions, year founded, ownership, and headquarters address. This repo is a working Python client plus MCP install instructions for five assistants, so you can call the API from a script or ask an agent to do it for you.

## Video Walkthrough

[![Watch the walkthrough](https://img.youtube.com/vi/jREWahDGhJM/maxresdefault.jpg)](https://www.youtube.com/watch?v=jREWahDGhJM)

### Text walkthrough

The Owler Company Intelligence API takes one input, `companyUrls`, and returns one row per company. Pass full profile URLs like `https://www.owler.com/company/stripe`, or just the bare slug `stripe`; both resolve. What comes back is a competitor intelligence record: `totalCompetitors` plus a `competitors` array of names and profile URLs, and around that the firmographic block of `industry`, `employeeCount`, `estimatedEmployees`, `revenue`, `estimatedAnnualRevenue`, `totalFunding`, `totalAcquisitions`, `founded`, `ownership`, and the `city`, `state`, `country` of headquarters. The competitor URLs are the interesting part, because feeding them back in as a second batch is how you turn one lookup into a market map without a list to start from. A concrete use case: run one seed account, collect its 20-odd competitors, run those, and you have a sized competitive landscape with revenue bands and headcounts on every node. The bundled `--example competitor-map` recipe does exactly that in two passes. Rows that cannot be collected come back with `result_type` of `error` and a plain-language `error_message` instead of vanishing, and those inputs are not charged.

## Quick Start

### Prerequisites
- Python 3.11 or higher
- An Apify account and API key ([get a free key here](https://apify.com?fpr=9n7kx3))

1. **Clone the repository**
   ```bash
   git clone https://github.com/johnisanerd/Apify-Owler-Company-API.git
   cd Apify-Owler-Company-API
   ```

2. **Install dependencies with UV**
   ```bash
   # Install UV if you do not have it:
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install project dependencies:
   uv sync
   ```

3. **Configure your API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your Apify API key
   # Get your free API key at: https://apify.com?fpr=9n7kx3
   ```

4. **Run the example**
   ```bash
   uv run python owler-company-api-example.py

   # Or pick a recipe:
   uv run python owler-company-api-example.py --example competitor-map
   uv run python owler-company-api-example.py --example firmographics
   ```

### Alternative: set the API key directly
```bash
export APIFY_API_TOKEN="your_api_key_here"
uv run python owler-company-api-example.py
```

## Why Use This Owler Company Intelligence API?

**The competitor set is the differentiator.** Plenty of sources will hand you an industry code and a headcount band. Far fewer hand you a list of named rivals with links you can follow. That list is what makes competitor intelligence work possible from a script instead of from an analyst's browser tabs.

**Private company data without an enterprise contract.** Companies that file nothing publicly still get a revenue estimate as a number and as a band, plus total funding raised and acquisition count. That covers the questions most private company research starts with, at pay-per-record pricing rather than a seat licence.

**Firmographics that segmentation can actually use.** `industry`, `industries`, `estimatedEmployees`, `estimatedAnnualRevenue`, `founded`, `ownership`, `sicCode`, and the full headquarters address are the fields territory sizing and lead scoring filter on first. They arrive on the same row, so no join is needed.

**Built for batches.** Up to 1000 company URLs per run, collected in chunks, one charged event per company record actually returned. An input that resolves to nothing is not charged, so a partly stale list does not cost you for the dead entries.

**Agent friendly.** Each row carries a one-line `summary` in plain language, so an assistant reading the dataset does not need a post-processing step before it can answer a question about the company.

## Features

### Core Capabilities
- Named competitor set per company, with a follow-on profile URL for every rival
- Revenue as an exact estimate (`revenue`) and as a band (`estimatedAnnualRevenue`)
- Employee count as a number (`employeeCount`) and as a band (`estimatedEmployees`)
- Total funding raised and number of acquisitions made
- Industry classifications, SIC codes, year founded, and ownership status
- Full headquarters address: street, city, state or region, postal code, country
- Website, primary domain, and company description, useful as join keys and context
- Public-company extras when listed: stock exchange and ticker
- Bare slug shorthand, so `stripe` works the same as the full profile URL
- Batches of up to 1000 company URLs per run

### Data Quality
- Records are collected live at run time, not served from a cached copy
- Failed inputs return an `error` row with a readable `error_message` rather than disappearing
- Input URLs are validated before collection starts, so a malformed URL is rejected locally
- Fields the source profile does not list come back as `None`, never as invented values
- `fetched_at` timestamps every row so you can age your own cache

## Recipes

Three example recipes ship in `owler-company-api-example.py`. Each one keeps its input small on purpose, because billing is one charged event per company record returned.

### Company snapshot (default)

The general quick-start. Two companies in, a wide slice of the output printed: industry, headquarters, founding year, ownership, revenue band and estimate, employee band and estimate, funding, acquisitions, competitor count, the first three named competitors, and the row summary.

Local: `uv run python owler-company-api-example.py`

### Map a competitive set

Competitor intelligence in two passes. Pass one collects a seed company and reads its `competitors` array; pass two feeds those profile URLs back in so you get full records for the rivals too, with their own revenue bands, headcounts, and competitor counts. Raise `follow_count` in the function to widen the map.

Local: `uv run python owler-company-api-example.py --example competitor-map`

### Pull firmographics for one account

Firmographics and private company data for a single company: industries, SIC codes, employee band, revenue band and estimate, funding, acquisitions, ownership, founding year, exchange and ticker when the company is public, phone, and the full headquarters address.

Local: `uv run python owler-company-api-example.py --example firmographics`

**Schedule tip:** Save any of these inputs as a Task in the Apify Console and [schedule it](https://apify.com/johnvc/owler-company-api?fpr=9n7kx3) to run weekly or monthly. Competitor sets, headcounts, and funding totals move slowly, so a monthly refresh keeps an account list current without anyone remembering to press a button.

## Usage Examples

### Basic Example
```json
{
  "companyUrls": [
    "https://www.owler.com/company/stripe"
  ]
}
```

### Advanced Example
```json
{
  "companyUrls": [
    "https://www.owler.com/company/stripe",
    "https://www.owler.com/company/hubspot",
    "figma",
    "notion"
  ]
}
```

Bare slugs and full profile URLs can be mixed freely in the same list.

## Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `companyUrls` | `list[str]` | YES | - | Company profile URLs to collect, for example `https://www.owler.com/company/stripe`. A bare company slug such as `stripe` also works. Up to 1000 per run. One charged event per company record returned; inputs that return no record are not charged. |

That is the whole input surface. There are no paging or result-limit knobs, because cost tracks the length of `companyUrls` directly.

## Output Format

One row per input. `result_type` is `company` for a successful record and `error` for an input that could not be collected. Real output, competitor list trimmed for readability:

```json
{
  "result_type": "company",
  "companyId": "100163",
  "companyName": "HubSpot, Inc.",
  "profileUrl": "https://www.owler.com/company/hubspot",
  "website": "https://www.hubspot.com/",
  "domain": "hubspot.com",
  "description": "HubSpot is a Massachusetts-based CRM platform that provides solutions such as marketing automation and meeting scheduling for businesses.",
  "industry": "Software, Internet & Computer Services",
  "industries": ["Software, Internet & Computer Services"],
  "founded": 2006,
  "ownership": "Public",
  "city": "Cambridge",
  "state": "Massachusetts",
  "country": "USA",
  "zipcode": "02141",
  "streetAddress": "2 Canal Park",
  "phoneNumber": "1-888-482-7768",
  "revenue": 3448998000,
  "estimatedAnnualRevenue": "$1B - 5B",
  "employeeCount": 7430,
  "estimatedEmployees": "5,000 - 10,000",
  "totalFunding": 625698612,
  "totalAcquisitions": 15,
  "totalCompetitors": 21,
  "competitors": [
    { "name": "Bibblio", "profileUrl": "https://www.owler.com/company/bibblio" },
    { "name": "Ideaken", "profileUrl": "https://www.owler.com/company/ideaken" },
    { "name": "Cticorp", "profileUrl": "https://www.owler.com/company/cticorp" }
  ],
  "followers": 16696,
  "exchange": "NYSE",
  "ticker": "HUBS",
  "sicCode": ["7372", "7374"],
  "summary": "HubSpot, Inc. in Software, Internet & Computer Services - Cambridge, USA. Reported estimated revenue $1B - 5B, 7430 employees.",
  "fetched_at": "2026-08-07T17:47:33.590587+00:00"
}
```

An input that cannot be collected returns this shape instead:

```json
{
  "result_type": "error",
  "profileUrl": "https://www.owler.com/company/does-not-exist",
  "error_message": "This company page no longer exists on the source site.",
  "error_type": "CollectionError"
}
```

Not every profile lists every field. `ceoName`, `exchange`, `ticker`, `phoneNumber`, and `sicCode` show up only when the source profile carries them, so check for `None` before you depend on one.

## People also search for

### What is competitor intelligence?

It is the practice of tracking who a company competes with, how large those rivals are, and how that set shifts over time. This API supplies the raw layer: a competitor count and a named competitor set per company, with profile URLs you can follow to collect those rivals in turn.

### What are firmographics, and what is firmographic data used for?

Firmographics are to companies what demographics are to people: industry, employee count, revenue band, location, ownership, and age. Teams use them for segmenting accounts, sizing territories, scoring inbound leads, and building target account lists. Employee band and revenue band are usually the first two filters applied, and both are returned here.

### How do I find financial data on private companies?

Private companies file little or nothing publicly, so the practical route is estimation from headcount, funding, and sector benchmarks. This API returns a numeric revenue estimate, a banded revenue range, total funding raised, and acquisition count, which covers most private company data questions without an enterprise data contract.

### How do I choose a firmographic data provider?

Compare on coverage of the accounts you actually hold, on field freshness, and on pricing shape. Per-record pricing suits enrichment of a known list; seat licences suit browsing. This API is per-record, collects live at run time, and returns a documented field set you can check against your own accounts before committing.

### Is this an Owler scraper or an API?

Both descriptions get used. People search for an Owler scraper when what they want is structured company data on demand; this is an API on the Apify platform that returns exactly that as JSON, callable from Python, from MCP, or from the Apify Console.

### How do I use competitor intelligence data from Python?

Clone this repo, set `APIFY_API_TOKEN`, and run `uv run python owler-company-api-example.py --example competitor-map`. See Quick Start and Recipes above.

### Can I use this with MCP or Claude?

Yes. The install sections below add the Actor as an MCP tool in [Claude Code](https://claude.ai/referral/uIlpa7nPLg) (free trial), [Claude Cowork](https://claude.ai/referral/uIlpa7nPLg) (free trial), Claude on the web, Cursor, or ChatGPT. Then just ask for the competitor set and revenue estimate for a company by name.

### Does it return email addresses?

No. Records carry a website, a domain, and a phone number when listed, but no email addresses.

---

## Install in Claude Cowork Desktop

![Install in Claude Cowork Desktop](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_desktop.png)

Cowork is the desktop app's automation mode. To give it the Owler Company Intelligence API as a tool, add the Apify MCP server as a connector.

1. Open the Claude desktop app and go to **Settings → Connectors** (or **Settings → Developer → Edit Config** to edit `claude_desktop_config.json` directly).
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the Apify MCP server, preloaded with only this Actor:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.apify.com/?tools=actors,docs,johnvc/owler-company-api"
      ]
    }
  }
}
```

3. Restart the app. When Cowork first calls the tool, complete the OAuth prompt in your browser, or add your Apify API token in the connector settings to skip OAuth.
4. In a Cowork chat, confirm the tool is available and ask it to run the Owler Company Intelligence API.

Download the desktop app and start a free trial: https://claude.ai/referral/uIlpa7nPLg
More help: https://docs.apify.com/platform/integrations/claude-desktop

---

## Install in Claude Code

![Install in Claude Code](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_code.png)

Claude Code is the command-line tool. Add the Actor's MCP server with one command:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/owler-company-api"
```

To use a token instead of browser OAuth:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/owler-company-api" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

Then verify with `claude mcp list`, or run `/mcp` inside a session. Ask Claude Code to call the Owler Company Intelligence API.

Try Claude Code free: https://claude.ai/referral/uIlpa7nPLg
Claude Code MCP docs: https://code.claude.com/docs/en/mcp

---

## Install in Claude (website)

![Install in Claude (website)](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_ai.png)

On claude.ai you add Apify as a connector, then enable just this Actor's tool.

1. Go to **Settings → Connectors → Browse connectors** and search for **Apify MCP server**. Install it (enable or update if prompted).
2. When connecting, authenticate with your Apify API token, and enable the tool `johnvc/owler-company-api`.
3. In any chat, open **+ → Connectors** and turn on **Apify**.
4. Alternatively, choose **Add custom connector** and paste the full MCP URL `https://mcp.apify.com/?tools=actors,docs,johnvc/owler-company-api`, using OAuth when prompted.
5. Ask Claude to run the Owler Company Intelligence API.

Open Claude on the web: https://claude.ai

---

## Install in Cursor

![Install in Cursor](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_cursor.png)

Cursor reads MCP servers from a project file at `.cursor/mcp.json`.

1. In your project, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/owler-company-api"
    }
  }
}
```

2. If you prefer token auth over browser OAuth, add a header:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/owler-company-api",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

3. Open **Cursor → Settings → MCP** and confirm the **apify** server is connected (green dot).
4. In Composer or Chat, ask Cursor to call the Owler Company Intelligence API.

New to Cursor? Get it here: https://cursor.com/referral?code=XQP4VBLI3NNX

---

## Install in ChatGPT

![Install in ChatGPT](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_ChatGPT.png)

ChatGPT connects to the Apify MCP server through Developer mode (available on ChatGPT Pro, Plus, Business, Enterprise, and Education plans).

1. Click your profile icon, then go to **Settings > Apps**. If you do not see a **Create app** button, open **Advanced settings** and enable **Developer mode**.
2. Click **Create app** and fill out the form:
   - **Name:** Apify
   - **MCP Server URL:** `https://mcp.apify.com/?tools=actors,docs,johnvc/owler-company-api`
   - **Authentication:** OAuth
3. Click **Create** and authorize the connection with Apify.
4. To use the app in a conversation, click **+** in the chat, choose **Developer mode**, and select **Apify**.

More help: https://docs.apify.com/platform/integrations/mcp

---

## Related APIs

- [Crunchbase Company API](https://apify.com/johnvc/crunchbase-company-api?fpr=9n7kx3) for funding rounds and investor detail
- [PitchBook Company API](https://apify.com/johnvc/pitchbook-company-api?fpr=9n7kx3) for private-market financials
- [LinkedIn Company API](https://apify.com/johnvc/linkedin-company-api?fpr=9n7kx3) for headcount and company page detail

---

## 🌐 About Alpha OSINT

This example repo is part of [Alpha OSINT](https://www.alphaosint.com), toolset of financial and operations data sources and APIs.
For support or requests for this actor, please start a ticket [directly on our support page](https://apify.com/johnvc/owler-company-api/issues/open?fpr=9n7kx3).

---

[**Made with care**](https://apify.com/johnvc?fpr=9n7kx3)

*Use the Owler Company Intelligence API to power your competitor intelligence and account research workflows with reliable, structured results.*

Last Updated: 2026.08.23
