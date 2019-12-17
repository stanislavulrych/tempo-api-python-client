# tempo-api-python-client
Python bindings for Tempo (https://tempo-io.github.io/tempo-api-docs/)

This is a Tempo API client library to simplify the interaction with Tempo timesheets.


## Getting Started

```
from tempoapiclient import client

tempo = client.Tempo(
    auth_token="<your_tempo_api_key>",
    base_url="https://api.tempo.io/core/3")

worklogs = tempo.get_worklogs("2019-11-10", "2019-11-11")

for i in worklogs:
    print(i)
```

## Changelog

- 2019-12-17: Initial version with /worklogs, /work-attributes and /user-schedule
- 2019-12-18: Updated client initialization, internal code reorganization

## Contributing

Contribution is welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.
