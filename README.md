# tempo-api-python-client
Python bindings for Tempo Rest API.

This is a Tempo API client library to simplify the interaction with Tempo timesheets.

Pip release is available: https://pypi.org/project/tempo-api-python-client/

Tempo Rest API documentation can be found at https://apidocs.tempo.io/


## Installation

Install current release by pip

```
pip install tempo-api-python-client
```


## Getting Started

You need an API token for communicating with tempo REST APIs. 

```
from tempoapiclient import client

tempo = client.Tempo(
    auth_token="<your_tempo_api_key>",
    base_url="https://api.tempo.io/core/3")

worklogs = tempo.get_worklogs(
    dateFrom="2019-11-10",
    dateTo="2019-11-11"
    )

for i in worklogs:
    print(i)
```

There are also functions to retrieve `user` and `team`-specific worklogs.


## Code Format

- Flake8: `flake8 --max-line-length=120 tempoapiclient/*`

- Pylint: `pylint --max-line-length=120 tempoapiclient`

## Contributing

Contribution is welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.
