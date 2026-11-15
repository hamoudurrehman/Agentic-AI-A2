# GigBid Portfolio MCP Server

A standalone Model Context Protocol (MCP) server that exposes a developer's verified case studies, technical skills, open-source repositories, and historical proposals through standard MCP JSON-RPC 2.0 endpoints.

Compatible with **Claude Desktop**, **Cursor**, **Windsurf**, and any MCP-compliant agent host.

---

## Capabilities & Tools

| Tool | Type | Description |
| :--- | :--- | :--- |
| `search_evidence` | Read | Retrieve evidence items (case studies, repositories, proposals) matching technical requirements with similarity scoring. |
| `get_case_study` | Read | Fetch complete details, metrics, and deliverables for a specific case study ID. |
| `list_skills` | Read | List verified technical competencies for the freelancer persona. |

### Resource Templates
- `portfolio://case/{id}` — Direct URI to load full case study.
- `portfolio://proposal/{id}` — Direct URI to load historical proposal texts.
- `portfolio://skills` — Direct URI to load active technical skill tree.

### Prompt Templates
- `answer_screening_question` — Reusable prompt template grounding an interview question strictly in portfolio facts.
- `draft_evidence_summary` — Summarizes production deployments for a given technology.

---

## Installation & Usage

### Option 1: Run with `uvx`
```bash
uvx --from git+https://github.com/YOUR_USERNAME/gigbid.git#subdirectory=gigbid/mcp_servers/portfolio gigbid-portfolio-server
```

### Option 2: Local Pip Installation
```bash
cd gigbid/mcp_servers/portfolio
pip install -e .
gigbid-portfolio-server
```

### Option 3: Claude Desktop Configuration (`claude_desktop_config.json`)
Add the following to your Claude Desktop config:

```json
{
  "mcpServers": {
    "portfolio": {
      "command": "python",
      "args": ["-m", "gigbid.mcp_servers.portfolio.server"]
    }
  }
}
```

### Option 4: Docker
```bash
docker run -i --rm -p 8001:8001 gigbid/portfolio-mcp:latest
```

---

## License
MIT License.
