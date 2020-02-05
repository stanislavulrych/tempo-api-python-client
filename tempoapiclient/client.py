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
        yield data

    def get_accounts(self):
        """
        Retrieve existing accounts as a dictionary.
        """
        return { x["key"]: x for x in self._list("/accounts") }

    def get_account_categories(self):
        """
        Retrieve existing account categories as a dictionary.
        """
        return { x["key"]: x for x in self._list("/account-categories") }

    def get_account_category_types(self):
        """
        Retrieve all periods for a given date range as a list.
        """
        return self._list("/account-category-types")

    def get_periods(self, date_from, date_to):
        """
        Retrieve periods as a list.
        """
        params = {
            "from": self._resolve_date(date_from).isoformat(),
            "to": self._resolve_date(date_to).isoformat()
            }

        return self._list("/periods", **params)

    def get_work_attributes(self):
        """
        Returns worklog attributes inside ```date_from``` and ```date_to```,
        for particular ```user```, adding work attributes if ```add_work_attributes```.
        """
        return { x["key"]: x for x in self._list("/work-attributes") }

    def add_worklog_attributes(self, worklogs):
        """
        Return worklogs with added worklog attributes, destroys worklogs.
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

    def get_all_worklogs(self, date_from, date_to):
        date_from = self._resolve_date(date_from).isoformat()
        date_to = self._resolve_date(date_to).isoformat()
        url = f"/worklogs"
        params = { "from": date_from, "to": date_to, "limit": self.MAX_RESULTS }
        return self._list(url, **params)

    def get_user_worklogs(self, date_from, date_to, userid):
        """
        Returns worklogs inside ```date_from``` and ```date_to```,
        for particular ```user```.
        """

        date_from = self._resolve_date(date_from).isoformat()
        date_to = self._resolve_date(date_to).isoformat()
        url = f"/worklogs/user/{userid}"
        params = { "from": date_from, "to": date_to, "limit": self.MAX_RESULTS }
        return self._list(url, **params)

    def get_team_worklogs(self, date_from, date_to, teamid):
        """
        Returns worklogs inside ```date_from``` and ```date_to```,
        for particular ```team```.
        """

        date_from = self._resolve_date(date_from).isoformat()
        date_to = self._resolve_date(date_to).isoformat()
        url = f"/worklogs/team/{teamid}"
        params = { "from": date_from, "to": date_to, "limit": self.MAX_RESULTS }
        return self._list(url, **params)

    def get_team_members(self, teamid):
        """
        Returns members for particular ```team```.
        """

        url = f"/teams/{teamid}/members"
        return self._list(url)

    def get_team_memberships(self, membershipid):
        """
        Returns members for particular ```team membership id```.
        """

        url = f"/team-memberships/{membershipid}"
        return self._single(url)

    def get_account_team_membership(self, teamid, accountid):
        """
        Returns the active team membership of a specific ```accountid``` in a specific  ```teamid```.
        """

        url = f"/teams/{teamid}/members/{accountid}"
        return self._single(url)

    def get_user_schedule(self, date_from, date_to, user=None):
        """
        Returns user schedule inside ```date_from``` and ```date_to```,
        for particular ```user```.
        """
        date_from = self._resolve_date(date_from).isoformat()
        date_to = self._resolve_date(date_to).isoformat()
        url = "/user-schedule"
        if user is not None:
            url += "/{}".format(user)
        params = { "from": date_from, "to": date_to, "limit": self.MAX_RESULTS }
        return self._list(url, **params)
