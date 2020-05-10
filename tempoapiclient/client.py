# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import unicode_literals

import requests
from datetime import date, datetime


class Tempo(object):
    """
    Basic Client for accessing Tempo Rest API as provided by api.tempo.io.
    """

    # Maximum number of result in single response (pagination)
    # NOTE: maximum number allowed by API is 1000
    MAX_RESULTS = 1000

    def __init__(self, auth_token, base_url="https://api.tempo.io/core/3"):
        self._token = auth_token
        self.BASE_URL = base_url
        self.work_attributes = None

    def _resolve_date(self, value):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
    
        parsed = date.fromisoformat(value)
        return parsed

    def _list(self, url, **params):
        # Resolve parameters
        url = self.BASE_URL + url
        headers = { "Authorization": "Bearer {}".format(self._token) }
        params = params.copy()

        # Return paginated results
        processed = 0
        while True:
            params["offset"] = processed
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            metadata = data.get("metadata", {})
            results = data.get("results", [])
            processed += metadata.get("count", 0)
            for result in results:
                yield result
            if "next" not in metadata or metadata.get("count", 0) < metadata.get("limit", 0):
                break

    def _single(self, url, **params):
        # Resolve parameters
        url = self.BASE_URL + url
        headers = { "Authorization": "Bearer {}".format(self._token) }

        # Return a single result
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data


# Accounts

    def get_accounts(self):
        """
        Retrieve existing accounts as a dictionary.
        """
        return { x["key"]: x for x in self._list("/accounts") }


# Account - Categories

    def get_account_categories(self):
        """
        Retrieve existing account categories as a dictionary.
        """
        return { x["key"]: x for x in self._list("/account-categories") }


# Account - Category - Types

    def get_account_category_types(self):

        """
        Retrieve all periods for a given date range as a list.
        """
        return self._list("/account-category-types")

# Account - Links

    ## TBD


# Customers

    def get_customers(self, key=None):

        """
        Retrieve all customers or customer with ```key```.
        """

        url = "/customers"
        if key:
            url += f"/{key}"
        return self._list(url)


# Plans

    def get_plans(self, id=None, userId=None):

        """
        Retrieve plans or plan with ```id``` or plan for ```userId````.
        """

        url = "/plans"
        if id:
            url += f"/{id}"
        elif userId:
            url += f"/plans/user/{userId}"
        return self._list(url)


# Programs

    ## TBD


# Roles

    ## TBD


# Teams

    def get_teams(self, teamId=None):
        """
        Returns ```teams``` or the details of team ```teamId```.
        """

        url = f"/teams"
        if (teamId):
            url += f"/{teamId}"

        return self._single(url)

    def get_team_members(self, teamId):
        """
        Returns members for particular ```teamId```.
        """

        url = f"/teams/{teamId}/members"
        return self._single(url)

# Team - Links

## TBD


# Team - Memberships

    def get_team_memberships(self, membershipId):
        """
        Returns members for particular ```team membershipId```.
        """

        url = f"/team-memberships/{membershipId}"
        return self._single(url)

    def get_account_team_membership(self, teamId, accountId):
        """
        Returns the active team membership of a specific ```accountId``` in a specific  ```teamId```.
        """

        url = f"/teams/{teamId}/members/{accountId}"
        return self._list(url)

    def get_account_team_memberships(self, teamId, accountId):
        """
        Returns all team memberships of a specific ```accountId``` in a specific  ```teamId```.
        """

        url = f"/teams/{teamId}/members/{accountId}/memberships"
        return self._list(url)

# Periods

    def get_periods(self, dateFrom, dateTo):
        """
        Retrieve periods as a list.
        """
        params = {
            "from": self._resolve_date(dateFrom).isoformat(),
            "to": self._resolve_date(dateTo).isoformat()
            }

        return self._single("/periods", **params)

# Timesheet Approvals

    def get_timesheet_approvals_waiting(self):
        """
        Retrieve waiting timesheet approvals
        """

        url = f"/timesheet-approvals/waiting"
        params = { "limit": self.MAX_RESULTS }
        return self._list(url, **params)

    def get_timesheet_approvals(self, dateFrom=None, dateTo=None, userId=None, teamId=None):
        """
        Retrieve timesheet approval between ```dateFrom``` and ```dateTo``` if specified; or for ```userId``` or ```teamId```.
        """
        
        params = {}
        if dateFrom:
            params["from"] = self._resolve_date(dateFrom).isoformat()
        if dateTo:
            params["to"] = self._resolve_date(dateTo).isoformat()

        url = f"/timesheet-approvals"
        if userId:
            url += f"/user/{userId}"
        elif teamId:
            url += f"/team/{teamId}"
        return self._single(url, **params)

# User Schedule

    def get_user_schedule(self, dateFrom, dateTo, userId=None):
        """
        Returns user schedule inside ```dateFrom``` and ```dateTo```,
        for particular ```userId```.
        """
        params = {
            "from": self._resolve_date(dateFrom).isoformat(),
            "to": self._resolve_date(dateTo).isoformat(),
            "limit": self.MAX_RESULTS
            }
        url = "/user-schedule"
        if userId:
            url += f"/{userId}"
        return self._list(url, **params)


# Work Attributes

    def get_work_attributes(self):
        """
        Returns worklog attributes.
        """
        return { x["key"]: x for x in self._list("/work-attributes") }

    def add_worklog_attributes(self, worklogs):
        """
        Update worklog attributes in worklogs.
        """

        if not self.work_attributes:
            self.work_attributes = self.get_work_attributes()

        for worklog in worklogs:
            attributes = (worklog.get("attributes") or {}).get("values") or {}
            resolved_attributes = {}

            for attribute in attributes:
                key = attribute.get("key")
                if key:
                    name = self.work_attributes.get(key, {}).get("name", key)
                    resolved_attributes[name] = attribute["value"]

            worklog["attributes"] = resolved_attributes

            yield worklog

# Workload Schemes

    def get_workload_schemes(self, id=None):
        url = f"/workload-schemes"
        if id:
            url += f"/{id}"
        return self._list(url)

# Holiday Schemes

    def get_holiday_schemes(self, holidaySchemeId=None):
        url = f"/holiday-schemes"
        if holidaySchemeId:
            url += f"/{holidaySchemeId}/holidays"
        return self._list(url)

# Worklogs

    def get_worklogs(self, dateFrom, dateTo, worklogId=None, jiraWorklogId=None, jiraFilterId=None, accountKey=None, projectKey=None, teamId=None, accountId=None, issue=None):
        """
        Returns worklogs inside ```dateFrom``` and ```dateTo```,
        for particular parameter: ```worklogId```, ```jiraWorklogId```,  ```jiraFilterId```, ```accountKey```, ```projectKey```, ```teamId```, ```accountId```, ```issue```.
        """

        params = {
            "from": self._resolve_date(dateFrom).isoformat(),
            "to": self._resolve_date(dateTo).isoformat(),
            "limit": self.MAX_RESULTS
            }
        url = f"/worklogs"
        if worklogId:
            url += f"/{worklogId}"
        elif jiraWorklogId:
            url += f"/jira/{jiraWorklogId}"
        elif jiraFilterId:
            url += f"/jira/filter/{jiraFilterId}"
        elif accountKey:
            url += f"/account/{accountKey}"
        elif projectKey:
            url += f"/project/{projectKey}"
        elif teamId:
            url += f"/team/{teamId}"
        elif accountId:
            url += f"/user/{accountId}"
        elif issue:
            url += f"/issue/{issue}"

        return self._list(url, **params)
