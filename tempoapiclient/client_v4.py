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

    def __init__(self, auth_token, base_url="https://api.tempo.io/4", limit=5000):
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
    
    def _resolve_time(self, value):
        _v = self.strip_hrs(value)
        _h = 0
        _m = 0
        _s = 0
        if _v.__contains__("pm"):
            _v = _v.replace("pm","")
            _h = int(_v.split(":")[0])
            if _h < 12:
                _h = _h+12
            elif _h == 12:
                _h = 0
        else:
            _h = int(_v.split(":")[0])
        if _h > 99:
            _h = int(_h/100)
        if _v.count(":") == 2:
            _m = int(_v.split(":")[1])
            _s = int(_v.split(":")[2])
        elif _v.count(":") == 1:
            _m = int(_v.split(":")[1])
        value = "{:02d}:{:02d}:{:02d}".format(_h, _m, _s)
        parsed = datetime.strptime(value,  r"%H:%M:%S").time()
        return parsed
    
    def strip_hrs(self, value):
        _hrs = ["am", "uhr", "hrs", "hours", "hour"]
        retval = value.lower().replace(" ","").replace(".",":")
        for i in _hrs:
            retval = retval.replace(i, "")
        return retval.strip()

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

    def put(self, path, data=None, params=None, headers=None, not_json_response=None, trailing=None):
        path_absolute = super().url_joiner(self._base_url, path)
        return super().put(path_absolute, data=data, params=params, headers=headers, trailing=trailing)

    def delete(self, path, data=None, params=None, headers=None, not_json_response=None, trailing=None):
        path_absolute = super().url_joiner(self._base_url, path)
        return super().delete(path_absolute, headers=headers, trailing=trailing)

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
    def get_plans(self, dateFrom=None, dateTo=None, id=None, accountId=None, accountIds=None, assigneeTypes=None, genericResourceId=None, genericResourceIds=None, planIds=None, planItemIds=None, planItemTypes=None, plannedTimeBreakdown=None, updatedFrom=None):
        """
        Retrieves a list of existing Plans that matches the given search parameters.
        :param dateFrom:
        :param dateTo:
        :param id:                      ~~~ retrieve plan ~~~
        :param accountId:               ~~~ retrieve plans for user ~~~
        :param accountIds:              ~~~ search plans ~~~
        :param assigneeTypes:           ~~~ search plans ~~~
        :param genericResourceId:       ~~~ retrieve plans for generic resource ~~~
        :param genericResourceIds:      ~~~ search plans ~~~
        :param planIds:                 ~~~ search plans ~~~
        :param planItemIds:             ~~~ search plans ~~~
        :param planItemTypes:           ~~~ search plans ~~~
        :param plannedTimeBreakdown:    ~~~ search plans ~~~
        :param updatedFrom:             ~~~ retrieve plans for user / retrieve plans for generic resource / search plans ~~~
        """

        if id:
            url = f"plans/{id}"
            return self.get(url)
        elif accountId:
            url = f"/plans/user/{accountId}"
            params = {
                "offset": 0,
                "limit": self._limit
            }
            if plannedTimeBreakdown:
                params['plannedTimeBreakdown'] = plannedTimeBreakdown
            if dateFrom:
                params['from'] = self._resolve_date(dateFrom).isoformat()
            if dateTo:
                params['to'] = self._resolve_date(dateTo).isoformat()
            if updatedFrom:
                params['updatedFrom'] = self._resolve_date(updatedFrom).isoformat()

            return self.get(url, params=params)
        elif genericResourceId:
            url = f"/plans/generic-resource/{genericResourceId}"
            params = {
                "offset": 0,
                "limit": self._limit
            }
            if plannedTimeBreakdown:
                params['plannedTimeBreakdown'] = plannedTimeBreakdown
            if dateFrom:
                params['from'] = self._resolve_date(dateFrom).isoformat()
            if dateTo:
                params['to'] = self._resolve_date(dateTo).isoformat()
            if updatedFrom:
                params['updatedFrom'] = self._resolve_date(updatedFrom).isoformat()

            return self.get(url, params=params)
        elif dateFrom and dateTo:
            data = {
                "from": self._resolve_date(dateFrom).isoformat(),
                "to": self._resolve_date(dateTo).isoformat(),
                "offset": 0,
                "limit": self._limit
            }
            if accountIds:
                data['accountIds'] = accountIds
            if assigneeTypes:
                data['assigneeTypes'] = assigneeTypes
            if genericResourceIds:
                data['genericResourceIds'] = genericResourceIds
            if planIds:
                data['planIds'] = planIds
            if planItemIds:
                data['planItemIds'] = planItemIds
            if planItemTypes:
                data['planItemTypes'] = planItemTypes
            if plannedTimeBreakdown:
                data['plannedTimeBreakdown'] = plannedTimeBreakdown
            if updatedFrom:
                data['updatedFrom'] = self._resolve_date(updatedFrom).isoformat()
            url = "/plans/search"
            return self.post(url, data=data)
        return

    def get_plan(self, id):
        return self.get_plans(id=id)

    def get_plan_for_user(self, accountId, plannedTimeBreakdown=None, dateFrom=None, dateTo=None, updatedFrom=None):
        return self.get_plans(accountId=accountId, plannedTimeBreakdown=plannedTimeBreakdown, dateFrom=dateFrom, dateTo=dateTo, updatedFrom=updatedFrom)

    def get_plan_for_resource(self, genericResourceId, plannedTimeBreakdown=None, dateFrom=None, dateTo=None, updatedFrom=None):
        return self.get_plans(genericResourceId=genericResourceId, plannedTimeBreakdown=plannedTimeBreakdown, dateFrom=dateFrom, dateTo=dateTo, updatedFrom=updatedFrom)

    def search_plans(self, dateFrom, dateTo, accountIds=None, assigneeTypes=None, genericResourceIds=None, planIds=None, planItemIds=None, planItemTypes=None, plannedTimeBreakdown=None, updatedFrom=None):
        return self.get_plans(dateFrom=dateFrom, dateTo=dateTo, accountIds=accountIds, assigneeTypes=assigneeTypes, genericResourceIds=genericResourceIds, planIds=planIds, planItemIds=planItemIds, planItemTypes=planItemTypes, plannedTimeBreakdown=plannedTimeBreakdown, updatedFrom=updatedFrom)

    def create_plan(self, assigneeId, assigneeType, startDate, endDate, planItemId, planItemType, plannedSecondsPerDay, description=None, includeNonWorkingDays=None, planApprovalReviewerId=None, planApprovalStatus=None, recurrenceEndDate=None, rule=None):
        """
        :param assigneeId:
        :param assigneeType:
        :param startDate:
        :param endDate:
        :param planItemId:
        :param planItemType:
        :param plannedSecondsPerDay:
        :param description:
        :param includeNonWorkingDays:
        :param planApprovalReviewerId:
        :param planApprovalStatus:
        :param recurrenceEndDate:
        :param rule:
        """
        data = {
            "assigneeId": assigneeId,
            "assigneeType": assigneeType, # Enum: "USER" "GENERIC"
            "startDate": self._resolve_date(startDate).isoformat(),
            "endDate": self._resolve_date(endDate).isoformat(),
            "planItemId": planItemId,
            "planItemType": planItemType, # Enum: "ISSUE" "PROJECT"
            "plannedSecondsPerDay": plannedSecondsPerDay
        }
        if description:
            data['description'] = description
        if includeNonWorkingDays:
            data['includeNonWorkingDays'] = includeNonWorkingDays
        if planApprovalReviewerId:
            if not planApprovalStatus:
                data['planApproval'] = {
                    "reviewerId": planApprovalReviewerId,
                    "status": "REQUESTED"
                }
            else:
                data['planApproval'] = {
                    "reviewerId": planApprovalReviewerId,
                    "status": planApprovalStatus # Enum: "APPROVED" "REJECTED" "REQUESTED"
                }
        if recurrenceEndDate:
            data['recurrenceEndDate'] = recurrenceEndDate
        if rule:
            data['rule'] = rule   # Enum: "NEVER" "WEEKLY" "BI_WEEKLY" "MONTHLY"

        url = "/plans"
        return self.post(url, data=data)

    def update_plan(self, id, assigneeId, assigneeType, startDate, endDate, planItemId, planItemType, plannedSecondsPerDay, description=None, includeNonWorkingDays=None, planApprovalReviewerId=None, planApprovalStatus=None, recurrenceEndDate=None, rule=None):
        """
        :param id:
        :param assigneeId:
        :param assigneeType:
        :param startDate:
        :param endDate:
        :param planItemId:
        :param planItemType:
        :param plannedSecondsPerDay:
        :param description:
        :param includeNonWorkingDays:
        :param planApprovalReviewerId:
        :param planApprovalStatus:
        :param recurrenceEndDate:
        :param rule:
        """
        data = {
            "assigneeId": assigneeId,
            "assigneeType": assigneeType, # Enum: "USER" "GENERIC"
            "startDate": self._resolve_date(startDate).isoformat(),
            "endDate": self._resolve_date(endDate).isoformat(),
            "planItemId": planItemId,
            "planItemType": planItemType, # Enum: "ISSUE" "PROJECT"
            "plannedSecondsPerDay": plannedSecondsPerDay
        }
        if description:
            data['description'] = description
        if includeNonWorkingDays:
            data['includeNonWorkingDays'] = includeNonWorkingDays
        if planApprovalReviewerId:
            if not planApprovalStatus:
                data['planApproval'] = {
                    "reviewerId": planApprovalReviewerId,
                    "status": "REQUESTED"
                }
            else:
                data['planApproval'] = {
                    "reviewerId": planApprovalReviewerId,
                    "status": planApprovalStatus # Enum: "APPROVED" "REJECTED" "REQUESTED"
                }
        if recurrenceEndDate:
            data['recurrenceEndDate'] = recurrenceEndDate
        if rule:
            data['rule'] = rule   # Enum: "NEVER" "WEEKLY" "BI_WEEKLY" "MONTHLY"

        url = f"/plans/{id}"
        return self.put(url, data=data)

    def delete_plan(self, id):
        url = f"/plans/{id}"
        return self.delete(url)

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
    def get_team_memberships(self, teamId):
        """
        Returns members.
        :param teamId:
        """

        url = f"/team-memberships/team/{teamId}"
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
                     accountKey=None, projectId=None, teamId=None, accountId=None, issueId=None):
        """
        Returns worklogs for particular parameters.
        :param dateFrom:
        :param dateTo:
        :param updatedFrom:
        :param worklogId:
        :param jiraWorklogId:
        :param jiraFilterId:
        :param accountKey:
        :param projectId:
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
        elif teamId:
            url += f"/team/{teamId}"
        elif accountId:
            url += f"/user/{accountId}"
        elif issueId:
            url += f"/issue/{issueId}"
        elif projectId:
            url += f"/project/{projectId}"
        
        return self.get(url, params=params)

    def search_worklogs(self, dateFrom, dateTo, updatedFrom=None, authorIds=None, issueIds=None, projectIds=None,
                     	offset=None, limit=None):
        """
        Retrieves a list of existing Worklogs that matches the given search parameter.
        :param offset:
        :param limit:
        """

        params = {
            "offset": 0 if offset is None else offset,
            "limit": self._limit if limit is None else limit
        }

        data = {
            "from": self._resolve_date(dateFrom).isoformat(),
            "to": self._resolve_date(dateTo).isoformat()
        }

        if updatedFrom:
            data["updatedFrom"] = updatedFrom
        if authorIds:
            data["authorIds"] = authorIds
        if issueIds:
            data["issueIds"] = issueIds
        if projectIds:
            data["projectIds"] = projectIds

        url = f"/worklogs/search"

        return self.post(url, params=params, data=data)

    def create_worklog(self, accountId, issueId, dateFrom, timeSpentSeconds, billableSeconds=None, description=None,
                       remainingEstimateSeconds=None, startTime=None, attributes=None):
        """
        Creates a new Worklog using the provided input and returns the newly created Worklog.
        :param accountId:
        :param issueId:
        :param dateFrom:
        :param timeSpentSeconds:
        :param billableSeconds:
        :param description:
        :param remainingEstimateSeconds:
        :param startTime:
        :param attributes:
        """

        url = f"/worklogs"
        
        data = {
            "authorAccountId": str(accountId),
            "issueId": int(issueId),
            "startDate": self._resolve_date(dateFrom).isoformat(),
            "timeSpentSeconds": int(timeSpentSeconds),
            "attributes": attributes
        }

        if billableSeconds:
            data["billableSeconds"] = int(billableSeconds)
        if description:
            data["description"] = str(description)
        if remainingEstimateSeconds:
            data["remainingEstimateSeconds"] = int(remainingEstimateSeconds)
        if startTime:
            data["startTime"] = self._resolve_time(startTime).isoformat()
        
        return self.post(url, data=data)

    def update_worklog(self, id, accountId, dateFrom, timeSpentSeconds, billableSeconds=None, description=None,
                       remainingEstimateSeconds=None, startTime=None):
        """
        Updates an existing Worklog using the provided input and returns the updated Worklog.
        :param id: The ID of the Worklog to be updated
        :param accountId: The Author account ID of the user author
        :param dateFrom: The start date of the Worklog
        :param timeSpentSeconds: The total amount of time spent in seconds
        :param billableSeconds: The amount of seconds billable
        :param description: The description of the Worklog
        :param remainingEstimateSeconds: The total amount of estimated remaining seconds
        :param startTime: The start time of the Worklog

        See https://apidocs.tempo.io/#tag/Worklogs/operation/updateWorklog
        """

        url = f"/worklogs/{id}"
        
        data = {
            "authorAccountId": str(accountId),
            "startDate": self._resolve_date(dateFrom).isoformat(),
            "timeSpentSeconds": int(timeSpentSeconds),
        }

        if billableSeconds:
            data["billableSeconds"] = int(billableSeconds)
        if description:
            data["description"] = str(description)
        if remainingEstimateSeconds:
            data["remainingEstimateSeconds"] = int(remainingEstimateSeconds)
        if startTime:
            data["startTime"] = self._resolve_time(startTime).isoformat()
        
        return self.put(url, data=data)

    def delete_worklog(self, id):
        """
        Deletes a Worklog
        :param id: The ID of the Worklog to be deleted

        See https://apidocs.tempo.io/#tag/Worklogs/operation/deleteWorklog
        """
        url = f"/worklogs/{id}"
        return self.delete(url)

# Customer

    def create_customer(self, key=None, name=None, data=None):
        """
        Create customer
        :param key:
        :param name:
        """

        # either provide data, or build from other params
        if (not(data)):
          data = {
            "key": key,
            "name": name
          }
        url = f"/customers"

        return self.post(url, data=data)

    def update_customer(self, key=None, name=None, data=None):
        """
        Update customer
        :param key:
        :param name:
        """

        # either provide data, or build from other params
        if (not(data)):
          data = {
            "key": key,
            "name": name
          }

        url = f"/customers/{key}"

        return self.put(url, data=data)

# Account

    def create_account(self, key=None, leadAccountId=None, name=None, status=None, categoryKey=None, contactAccountId=None, customerKey=None, externalContactName=None, isGlobal=None, data=None):
        """
        Create account
        :param key:
        :param leadAccountId:
        :param name:
        :param status: # Enum: "CLOSED" "OPEN" "ARCHIVED"
        :param categoryKey:
        :param contactAccountId:
        :param customerKey:
        :param externalContactName:
        :param isGlobal:
        """

        # either provide data, or build from other params
        if (not(data)):
          data = {
            "key": key,
            "leadAccountId": leadAccountId,
            "name": name,
            "status": status,
            "categoryKey": categoryKey,
            "contactAccountId": contactAccountId,
            "customerKey": customerKey,
            "externalContactName": externalContactName,
            "global": isGlobal
          }

        url = f"/accounts"

        return self.post(url, data=data)

    def update_account(self, key=None, leadAccountId=None, name=None, status=None, categoryKey=None, contactAccountId=None, customerKey=None, externalContactName=None, isGlobal=None, data=None):
        """
        Create account
        :param key:
        :param leadAccountId:
        :param name:
        :param status: # Enum: "CLOSED" "OPEN" "ARCHIVED"
        :param categoryKey:
        :param contactAccountId:
        :param customerKey:
        :param externalContactName:
        :param isGlobal:
        """

        # either provide data, or build from other params
        if (not(data)):
          data = {
            "key": key,
            "leadAccountId": leadAccountId,
            "name": name,
            "status": status,
            "categoryKey": categoryKey,
            "contactAccountId": contactAccountId,
            "customerKey": customerKey,
            "externalContactName": externalContactName,
            "global": isGlobal
          }

        url = f"/accounts/{key}"

        return self.put(url, data=data)
