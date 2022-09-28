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

from datetime import date, datetime

from .rest_client import RestAPIClient


class Tempo(RestAPIClient):
    """
    Basic Client for accessing Tempo Rest API as provided by api.tempo.io.
    """

    def __init__(self, auth_token, base_url="https://api.tempo.io/core/3", limit=1000):
        self._limit = limit   # default limit for pagination (1000 is maximum for Tempo API)
        self._base_url = base_url
        super().__init__(auth_token=auth_token)

    def _resolve_date(self, value):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value

        parsed = datetime.strptime(value,  r"%Y-%m-%d").date()

        return parsed

    def get(self, path, data=None, flags=None, params=None, headers=None, not_json_response=None, trailing=None):
        path_absolute = super().url_joiner(self._base_url, path)
        resp = super().get(path_absolute, data=data, flags=flags, params=params, headers=headers,
                           not_json_response=not_json_response, trailing=trailing)

        # single item returned
        if 'results' not in resp:
            return resp

        # multiple items
        results = resp['results']

        # handle all results paginated
        while 'next' in resp.get('metadata'):
            resp = super().get(resp.get('metadata').get('next'))
            results.extend(resp['results'])

        return results

    def post(self, path, data=None, params=None, headers=None, not_json_response=None, trailing=None):
        path_absolute = super().url_joiner(self._base_url, path)
        return super().post(path_absolute, data=data, params=params, headers=headers, trailing=trailing)

# Accounts

    def get_accounts(self):
        """
        Retrieves existing accounts.
        """
        return self.get("/accounts")

    # Account - Categories
    def get_account_categories(self):
        """
        Retrieves existing account categories.
        """
        return self.get("/account-categories")

    # Account - Category - Types
    def get_account_category_types(self):
        """
        Retrieves all periods for a given date range as a list.
        """
        return self.get("/account-category-types")

    # Account - Links
    ## TBD

    # Customers
    def get_customers(self, key=None):
        """
        Retrieves all customers or customer.
        :param key: Return customer for ```key```.
        """

        url = "/customers"
        if key:
            url += f"/{key}"
        return self.get(url)

    # Plans
    def get_plans(self, dateFrom, dateTo, assigneeType=None, planItemType=None, updatedFrom=None, id=None, userId=None):
        """
        Retrieves plans or plan.
        :param dateFrom:
        :param dateTo:
        :param assigneeType:
        :param planItemType:
        :param updatedFrom:
        :param id: Plan id
        :param userId: ```AccountId``` for user in Tempo
        """
        params = {
            "from": self._resolve_date(dateFrom).isoformat(),
            "to": self._resolve_date(dateTo).isoformat(),
            "offset": 0,
            "limit": self._limit
        }
        if assigneeType:
            params['assigneeType'] = assigneeType
        if planItemType:
            params['planItemType'] = planItemType
        if updatedFrom:
            params['updatedFrom'] = self._resolve_date(updatedFrom).isoformat()

        url = "/plans"
        if id:
            url += f"/{id}"
        elif userId:
            url += f"/plans/user/{userId}"
        return self.get(url, params=params)

    # Programs
    ## TBD

    # Roles
    ## TBD

    # Teams
    def get_teams(self, teamId=None):
        """
        Returns teams information.
        :param teamId: Returns details for team ```teamId```.
        """

        url = f"/teams"
        if (teamId):
            url += f"/{teamId}"

        return self.get(url)

    def get_team_members(self, teamId):
        """
        Returns members for particular team.
        :param teamId: teamId
        """

        url = f"/teams/{teamId}/members"
        return self.get(url)

    # Team - Links
    ## TBD

    # Team - Memberships
    def get_team_memberships(self, membershipId):
        """
        Returns members.
        :param membershipId:
        """

        url = f"/team-memberships/{membershipId}"
        return self.get(url)

    def get_account_team_membership(self, teamId, accountId):
        """
        Returns the active team membership.
        :param accountId:
        :param teamId:
        """

        return self.get(f"/teams/{teamId}/members/{accountId}")

    def get_account_team_memberships(self, teamId, accountId):
        """
        Returns all team memberships.
        :param accountId:
        :param teamId:
        """

        return self.get(f"/teams/{teamId}/members/{accountId}/memberships")

# Periods

    def get_periods(self, dateFrom, dateTo):
        """
        Retrieves periods.
        :param dateFrom:
        :param dateTo:
        """

        params = {
            "from": self._resolve_date(dateFrom).isoformat(),
            "to": self._resolve_date(dateTo).isoformat()
            }

        return self.get("/periods", params=params)

# Timesheet Approvals

    def get_timesheet_approvals_waiting(self):
        """
        Retrieve waiting timesheet approvals
        """

        return self.get(f"/timesheet-approvals/waiting")

    def get_timesheet_approvals(self, dateFrom=None, dateTo=None, userId=None, teamId=None):
        """
        Retrieves timesheet approvals.
        :param dateFrom:
        :param dateTo:
        :param userId:
        :param teamId:
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
        return self.get(url, params=params)

    # User Schedule
    def get_user_schedule(self, dateFrom, dateTo, userId=None):
        """
        Returns user schedule.
        :param dateFrom:
        :param dateTo:
        :param userId:
        """

        params = {
            "from": self._resolve_date(dateFrom).isoformat(),
            "to": self._resolve_date(dateTo).isoformat()
            }
        url = "/user-schedule"
        if userId:
            url += f"/{userId}"
        return self.get(url, params=params)

    # Work Attributes
    def get_work_attributes(self):
        """
        Returns worklog attributes.
        """
        return self.get("/work-attributes")

    # Workload Schemes
    def get_workload_schemes(self, id=None):
        url = f"/workload-schemes"
        if id:
            url += f"/{id}"
        return self.get(url)

# Holiday Schemes

    def get_holiday_schemes(self, holidaySchemeId=None, year=None):
        """
        Retrieve holidays for an existing holiday scheme.
        :param holidaySchemeId:
        :param year:
        """
        url = f"/holiday-schemes"
        if holidaySchemeId:
            url += f"/{holidaySchemeId}/holidays"

        params = {}

        if year:
            params["year"] = year

        return self.get(url, params=params)

    def create_holiday_scheme(self, schemeName, schemeDescription=None):
        """
        Create holiday scheme
        :param name:
        :param description:
        """

        url = f"/holiday-schemes"

        data = {"name": schemeName, "description": schemeDescription}

        return self.post(url, data=data)

    def create_holiday(self, holidaySchemeId, type=None, name=None, description=None, durationSeconds=None, date=None, data=None):
        """
        Create holiday scheme
        :param name:
        :param description:
        """

        # either provide data, or build from other params
        if (not(data)):
          data = {
            "type": type,
            "name": name,
            "description": description,
            "durationSeconds": durationSeconds,
            "date": date
          }

        url = f"/holiday-schemes/" + str(holidaySchemeId) + "/holidays"

        return self.post(url, data=data)




# Worklogs

    def get_worklogs(self, dateFrom, dateTo, updatedFrom=None, worklogId=None, jiraWorklogId=None, jiraFilterId=None,
                     accountKey=None, projectKey=None, teamId=None, accountId=None, issueId=None):
        """
        Returns worklogs for particular parameters.
        :param dateFrom:
        :param dateTo:
        :param updatedFrom:
        :param worklogId:
        :param jiraWorklogId:
        :param jiraFilterId:
        :param accountKey:
        :param projectKey:
        :param teamId:
        :param accountId:
        :param issue:
        """

        params = {
            "from": self._resolve_date(dateFrom).isoformat(),
            "to": self._resolve_date(dateTo).isoformat(),
            "offset": 0,
            "limit": self._limit
            }

        if updatedFrom:
            params["updatedFrom"] = self._resolve_date(updatedFrom).isoformat()

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
        elif issueId:
            url += f"/issue/{issueId}"

        return self.get(url, params=params)
