# tempo-api-python-client

Python bindings for [Tempo REST API v4](https://apidocs.tempo.io/) — sync (`Client_v4`) and async (`AsyncClient_v4`).

PyPI: https://pypi.org/project/tempo-api-python-client/

## Requirements

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) for development

## Installation

```bash
uv add tempo-api-python-client
```

## Getting started

You need a Tempo API token from your Tempo/Jira instance.

### Synchronous usage (scripts, Jupyter)

```python
from tempoapi import Client_v4

with Client_v4(auth_token="<your_tempo_api_key>") as tempo:
    worklogs = tempo.get_worklogs(dateFrom="2019-11-10", dateTo="2019-11-11")
```

### Async usage

```python
import asyncio

from tempoapi import AsyncClient_v4


async def main() -> None:
    async with AsyncClient_v4(auth_token="<your_tempo_api_key>") as tempo:
        worklogs = await tempo.get_worklogs(
            dateFrom="2019-11-10",
            dateTo="2019-11-11",
        )
        for worklog in worklogs:
            print(worklog)


asyncio.run(main())
```

## Development

```bash
uv sync --extra dev
uv run ruff check .
uv run pytest
```

## License

Apache License 2.0
