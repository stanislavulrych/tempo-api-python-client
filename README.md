# tempo-api-python-client

Python bindings for Tempo Rest API.

This is a Tempo API client library to simplify the interaction with Tempo timesheets. The implementation supports Tempo API v3 and v4.

Pip release is available: https://pypi.org/project/tempo-api-python-client/

Tempo Rest API documentation can be found at https://apidocs.tempo.io/


## Installation

Install current release by pip

```
pip install tempo-api-python-client
```


## Getting Started

You need an API token for communicating with tempo REST APIs. 

### For v3 use

    from tempoapiclient import client_v3

    tempo = client_v3.Tempo(
        auth_token="<your_tempo_api_key>",
        )

    worklogs = tempo.get_worklogs(
        dateFrom="2019-11-10",
        dateTo="2019-11-11"
        )

    for i in worklogs:
        print(i)

### For v4 use

    from tempoapiclient import client_v4

    tempo = client_v4.Tempo(
        auth_token="<your_tempo_api_key>",
        )

#### Retrieve Worklogs

    worklogs = tempo.get_worklogs(
        dateFrom="2019-11-10",
        dateTo="2019-11-11"
        )

    for i in worklogs:
        print(i)

There are also functions to retrieve `user` and `team`-specific worklogs.


#### Create Worklog

    logged_worklog = tempo.create_worklog(
        accountId="<your_jira_account_id>",
        issueId=12345,
        dateFrom="2019-11-11",
        timeSpentSeconds=3600,
        description="Something",
        startTime="17:00:00"
        attributes=[{_WorkType_: "Development"}]
    )

#### Update Worklog

    logged_worklog = tempo.update_worklog(
        id="<id_of_the_worklog_to_be_updated>"  # required
        accountId="<your_jira_account_id>",     # required
        dateFrom="2019-11-11",                  # required
        timeSpentSeconds=3600,                  # required
        description="Something",                # optional
        startTime="17:00:00"                    # optional
    )

#### Delete Worklog

    delete_response = tempo.delete_worklog(<worklog_id>)


## Code Format

- Flake8: `flake8 --max-line-length=120 tempoapiclient/*`

- Pylint: `pylint --max-line-length=120 tempoapiclient`


## Contributing

Contribution is welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.
