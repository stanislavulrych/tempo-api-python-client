from datetime import date, datetime
from typing import Any, Self

import httpx

from tempoapi._helpers import resolve_date, resolve_time
from tempoapi._http import create_tempo_sync_client, request_json_sync, url_joiner


class Client_v4:  # noqa: N801
    """Synchronous client for Tempo REST API v4 (https://api.tempo.io/4)."""

    def __init__(
        self,
        auth_token: str,
        base_url: str = "https://api.tempo.io/4",
        limit: int = 5000,
    ) -> None:
        self._auth_token = auth_token
        self._base_url = base_url
        self._limit = limit
        self._client: httpx.Client | None = create_tempo_sync_client(self._auth_token)

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _client_or_raise(self) -> httpx.Client:
        if self._client is None:
            raise RuntimeError("Client_v4 is closed")
        return self._client

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        path_absolute = url_joiner(self._base_url, path)
        resp = request_json_sync(
            self._client_or_raise(),
            "GET",
            path_absolute,
            params=params,
            headers=headers,
        )

        if "results" not in resp:
            return resp

        results = resp["results"]
        metadata = resp.get("metadata") or {}
        while "next" in metadata:
            resp = request_json_sync(self._client_or_raise(), "GET", metadata["next"])
            results.extend(resp["results"])
            metadata = resp.get("metadata") or {}

        return results

    def post(
        self,
        path: str,
        *,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        path_absolute = url_joiner(self._base_url, path)
        return request_json_sync(
            self._client_or_raise(),
            "POST",
            path_absolute,
            json=data,
            params=params,
            headers=headers,
        )

    def put(
        self,
        path: str,
        *,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        path_absolute = url_joiner(self._base_url, path)
        return request_json_sync(
            self._client_or_raise(),
            "PUT",
            path_absolute,
            json=data,
            params=params,
            headers=headers,
        )

    def delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        path_absolute = url_joiner(self._base_url, path)
        return request_json_sync(
            self._client_or_raise(),
            "DELETE",
            path_absolute,
            params=params,
            headers=headers,
        )

    def get_accounts(self) -> Any:
        return self.get("/accounts")

    def get_account_categories(self) -> Any:
        return self.get("/account-categories")

    def get_account_category_types(self) -> Any:
        return self.get("/account-category-types")

    def get_customers(self, key: str | None = None) -> Any:
        url = "/customers"
        if key:
            url += f"/{key}"
        return self.get(url)

    def get_plans(
        self,
        dateFrom: str | date | datetime | None = None,  # noqa: N803
        dateTo: str | date | datetime | None = None,  # noqa: N803
        id: str | None = None,  # noqa: A002
        accountId: str | None = None,  # noqa: N803
        accountIds: list[str] | None = None,  # noqa: N803
        assigneeTypes: list[str] | None = None,  # noqa: N803
        genericResourceId: str | None = None,  # noqa: N803
        genericResourceIds: list[str] | None = None,  # noqa: N803
        planIds: list[str] | None = None,  # noqa: N803
        planItemIds: list[str] | None = None,  # noqa: N803
        planItemTypes: list[str] | None = None,  # noqa: N803
        plannedTimeBreakdown: str | None = None,  # noqa: N803
        updatedFrom: str | date | datetime | None = None,  # noqa: N803
    ) -> Any:
        if id:
            return self.get(f"plans/{id}")
        if accountId:
            url = f"/plans/user/{accountId}"
            params: dict[str, Any] = {"offset": 0, "limit": self._limit}
            if plannedTimeBreakdown:
                params["plannedTimeBreakdown"] = plannedTimeBreakdown
            if dateFrom:
                params["from"] = resolve_date(dateFrom).isoformat()
            if dateTo:
                params["to"] = resolve_date(dateTo).isoformat()
            if updatedFrom:
                params["updatedFrom"] = resolve_date(updatedFrom).isoformat()
            return self.get(url, params=params)
        if genericResourceId:
            url = f"/plans/generic-resource/{genericResourceId}"
            params = {"offset": 0, "limit": self._limit}
            if plannedTimeBreakdown:
                params["plannedTimeBreakdown"] = plannedTimeBreakdown
            if dateFrom:
                params["from"] = resolve_date(dateFrom).isoformat()
            if dateTo:
                params["to"] = resolve_date(dateTo).isoformat()
            if updatedFrom:
                params["updatedFrom"] = resolve_date(updatedFrom).isoformat()
            return self.get(url, params=params)
        if dateFrom and dateTo:
            data: dict[str, Any] = {
                "from": resolve_date(dateFrom).isoformat(),
                "to": resolve_date(dateTo).isoformat(),
                "offset": 0,
                "limit": self._limit,
            }
            if accountIds:
                data["accountIds"] = accountIds
            if assigneeTypes:
                data["assigneeTypes"] = assigneeTypes
            if genericResourceIds:
                data["genericResourceIds"] = genericResourceIds
            if planIds:
                data["planIds"] = planIds
            if planItemIds:
                data["planItemIds"] = planItemIds
            if planItemTypes:
                data["planItemTypes"] = planItemTypes
            if plannedTimeBreakdown:
                data["plannedTimeBreakdown"] = plannedTimeBreakdown
            if updatedFrom:
                data["updatedFrom"] = resolve_date(updatedFrom).isoformat()
            return self.post("/plans/search", data=data)
        return None

    def get_plan(self, id: str) -> Any:  # noqa: A002
        return self.get_plans(id=id)

    def get_plan_for_user(
        self,
        accountId: str,  # noqa: N803
        plannedTimeBreakdown: str | None = None,  # noqa: N803
        dateFrom: str | date | datetime | None = None,  # noqa: N803
        dateTo: str | date | datetime | None = None,  # noqa: N803
        updatedFrom: str | date | datetime | None = None,  # noqa: N803
    ) -> Any:
        return self.get_plans(
            accountId=accountId,
            plannedTimeBreakdown=plannedTimeBreakdown,
            dateFrom=dateFrom,
            dateTo=dateTo,
            updatedFrom=updatedFrom,
        )

    def get_plan_for_resource(
        self,
        genericResourceId: str,  # noqa: N803
        plannedTimeBreakdown: str | None = None,  # noqa: N803
        dateFrom: str | date | datetime | None = None,  # noqa: N803
        dateTo: str | date | datetime | None = None,  # noqa: N803
        updatedFrom: str | date | datetime | None = None,  # noqa: N803
    ) -> Any:
        return self.get_plans(
            genericResourceId=genericResourceId,
            plannedTimeBreakdown=plannedTimeBreakdown,
            dateFrom=dateFrom,
            dateTo=dateTo,
            updatedFrom=updatedFrom,
        )

    def search_plans(
        self,
        dateFrom: str | date | datetime,  # noqa: N803
        dateTo: str | date | datetime,  # noqa: N803
        accountIds: list[str] | None = None,  # noqa: N803
        assigneeTypes: list[str] | None = None,  # noqa: N803
        genericResourceIds: list[str] | None = None,  # noqa: N803
        planIds: list[str] | None = None,  # noqa: N803
        planItemIds: list[str] | None = None,  # noqa: N803
        planItemTypes: list[str] | None = None,  # noqa: N803
        plannedTimeBreakdown: str | None = None,  # noqa: N803
        updatedFrom: str | date | datetime | None = None,  # noqa: N803
    ) -> Any:
        return self.get_plans(
            dateFrom=dateFrom,
            dateTo=dateTo,
            accountIds=accountIds,
            assigneeTypes=assigneeTypes,
            genericResourceIds=genericResourceIds,
            planIds=planIds,
            planItemIds=planItemIds,
            planItemTypes=planItemTypes,
            plannedTimeBreakdown=plannedTimeBreakdown,
            updatedFrom=updatedFrom,
        )

    def create_plan(
        self,
        assigneeId: str,  # noqa: N803
        assigneeType: str,  # noqa: N803
        startDate: str | date | datetime,  # noqa: N803
        endDate: str | date | datetime,  # noqa: N803
        planItemId: str,  # noqa: N803
        planItemType: str,  # noqa: N803
        plannedSecondsPerDay: int,  # noqa: N803
        description: str | None = None,
        includeNonWorkingDays: bool | None = None,  # noqa: N803
        planApprovalReviewerId: str | None = None,  # noqa: N803
        planApprovalStatus: str | None = None,  # noqa: N803
        recurrenceEndDate: str | None = None,  # noqa: N803
        rule: str | None = None,
    ) -> Any:
        data: dict[str, Any] = {
            "assigneeId": assigneeId,
            "assigneeType": assigneeType,
            "startDate": resolve_date(startDate).isoformat(),
            "endDate": resolve_date(endDate).isoformat(),
            "planItemId": planItemId,
            "planItemType": planItemType,
            "plannedSecondsPerDay": plannedSecondsPerDay,
        }
        if description:
            data["description"] = description
        if includeNonWorkingDays:
            data["includeNonWorkingDays"] = includeNonWorkingDays
        if planApprovalReviewerId:
            if not planApprovalStatus:
                data["planApproval"] = {"reviewerId": planApprovalReviewerId, "status": "REQUESTED"}
            else:
                data["planApproval"] = {"reviewerId": planApprovalReviewerId, "status": planApprovalStatus}
        if recurrenceEndDate:
            data["recurrenceEndDate"] = recurrenceEndDate
        if rule:
            data["rule"] = rule
        return self.post("/plans", data=data)

    def update_plan(
        self,
        id: str,  # noqa: A002
        assigneeId: str,  # noqa: N803
        assigneeType: str,  # noqa: N803
        startDate: str | date | datetime,  # noqa: N803
        endDate: str | date | datetime,  # noqa: N803
        planItemId: str,  # noqa: N803
        planItemType: str,  # noqa: N803
        plannedSecondsPerDay: int,  # noqa: N803
        description: str | None = None,
        includeNonWorkingDays: bool | None = None,  # noqa: N803
        planApprovalReviewerId: str | None = None,  # noqa: N803
        planApprovalStatus: str | None = None,  # noqa: N803
        recurrenceEndDate: str | None = None,  # noqa: N803
        rule: str | None = None,
    ) -> Any:
        data: dict[str, Any] = {
            "assigneeId": assigneeId,
            "assigneeType": assigneeType,
            "startDate": resolve_date(startDate).isoformat(),
            "endDate": resolve_date(endDate).isoformat(),
            "planItemId": planItemId,
            "planItemType": planItemType,
            "plannedSecondsPerDay": plannedSecondsPerDay,
        }
        if description:
            data["description"] = description
        if includeNonWorkingDays:
            data["includeNonWorkingDays"] = includeNonWorkingDays
        if planApprovalReviewerId:
            if not planApprovalStatus:
                data["planApproval"] = {"reviewerId": planApprovalReviewerId, "status": "REQUESTED"}
            else:
                data["planApproval"] = {"reviewerId": planApprovalReviewerId, "status": planApprovalStatus}
        if recurrenceEndDate:
            data["recurrenceEndDate"] = recurrenceEndDate
        if rule:
            data["rule"] = rule
        return self.put(f"/plans/{id}", data=data)

    def delete_plan(self, id: str) -> Any:  # noqa: A002
        return self.delete(f"/plans/{id}")

    def get_teams(self, teamId: str | None = None) -> Any:  # noqa: N803
        url = "/teams"
        if teamId:
            url += f"/{teamId}"
        return self.get(url)

    def get_team_members(self, teamId: str) -> Any:  # noqa: N803
        return self.get(f"/teams/{teamId}/members")

    def get_team_memberships(self, teamId: str) -> Any:  # noqa: N803
        return self.get(f"/team-memberships/team/{teamId}")

    def get_account_team_membership(self, teamId: str, accountId: str) -> Any:  # noqa: N803
        return self.get(f"/teams/{teamId}/members/{accountId}")

    def get_account_team_memberships(self, teamId: str, accountId: str) -> Any:  # noqa: N803
        return self.get(f"/teams/{teamId}/members/{accountId}/memberships")

    def get_periods(
        self,
        dateFrom: str | date | datetime,  # noqa: N803
        dateTo: str | date | datetime,  # noqa: N803
    ) -> Any:
        params = {
            "from": resolve_date(dateFrom).isoformat(),
            "to": resolve_date(dateTo).isoformat(),
        }
        return self.get("/periods", params=params)

    def get_timesheet_approvals_waiting(self) -> Any:
        return self.get("/timesheet-approvals/waiting")

    def get_timesheet_approvals(
        self,
        dateFrom: str | date | datetime | None = None,  # noqa: N803
        dateTo: str | date | datetime | None = None,  # noqa: N803
        userId: str | None = None,  # noqa: N803
        teamId: str | None = None,  # noqa: N803
    ) -> Any:
        params: dict[str, Any] = {}
        if dateFrom:
            params["from"] = resolve_date(dateFrom).isoformat()
        if dateTo:
            params["to"] = resolve_date(dateTo).isoformat()
        url = "/timesheet-approvals"
        if userId:
            url += f"/user/{userId}"
        elif teamId:
            url += f"/team/{teamId}"
        return self.get(url, params=params)

    def get_user_schedule(
        self,
        dateFrom: str | date | datetime,  # noqa: N803
        dateTo: str | date | datetime,  # noqa: N803
        userId: str | None = None,  # noqa: N803
    ) -> Any:
        params = {
            "from": resolve_date(dateFrom).isoformat(),
            "to": resolve_date(dateTo).isoformat(),
        }
        url = "/user-schedule"
        if userId:
            url += f"/{userId}"
        return self.get(url, params=params)

    def get_work_attributes(self) -> Any:
        return self.get("/work-attributes")

    def get_workload_schemes(self, id: str | None = None) -> Any:  # noqa: A002
        url = "/workload-schemes"
        if id:
            url += f"/{id}"
        return self.get(url)

    def get_holiday_schemes(
        self,
        holidaySchemeId: str | None = None,  # noqa: N803
        year: int | str | None = None,
    ) -> Any:
        url = "/holiday-schemes"
        if holidaySchemeId:
            url += f"/{holidaySchemeId}/holidays"
        params: dict[str, Any] = {}
        if year:
            params["year"] = year
        return self.get(url, params=params)

    def get_floating_holidays(self, holidaySchemeId: str) -> Any:  # noqa: N803
        return self.get(f"/holiday-schemes/{holidaySchemeId}/holidays/floating")

    def create_holiday_scheme(
        self,
        schemeName: str,  # noqa: N803
        schemeDescription: str | None = None,  # noqa: N803
    ) -> Any:
        data = {"name": schemeName, "description": schemeDescription}
        return self.post("/holiday-schemes", data=data)

    def create_holiday(
        self,
        holidaySchemeId: str,  # noqa: N803
        type: str | None = None,  # noqa: A002
        name: str | None = None,
        description: str | None = None,
        durationSeconds: int | None = None,  # noqa: N803
        date: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        if not data:
            data = {
                "type": type,
                "name": name,
                "description": description,
                "durationSeconds": durationSeconds,
                "date": date,
            }
        return self.post(f"/holiday-schemes/{holidaySchemeId}/holidays", data=data)

    def get_worklogs(
        self,
        dateFrom: str | date | datetime,  # noqa: N803
        dateTo: str | date | datetime,  # noqa: N803
        updatedFrom: str | date | datetime | None = None,  # noqa: N803
        worklogId: str | None = None,  # noqa: N803
        jiraWorklogId: str | None = None,  # noqa: N803
        jiraFilterId: str | None = None,  # noqa: N803
        accountKey: str | None = None,  # noqa: N803
        projectId: str | int | None = None,  # noqa: N803
        teamId: str | None = None,  # noqa: N803
        accountId: str | None = None,  # noqa: N803
        issueId: str | int | None = None,  # noqa: N803
    ) -> Any:
        params: dict[str, Any] = {
            "from": resolve_date(dateFrom).isoformat(),
            "to": resolve_date(dateTo).isoformat(),
            "offset": 0,
            "limit": self._limit,
        }
        if updatedFrom:
            params["updatedFrom"] = resolve_date(updatedFrom).isoformat()

        url = "/worklogs"
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

    def search_worklogs(
        self,
        dateFrom: str | date | datetime,  # noqa: N803
        dateTo: str | date | datetime,  # noqa: N803
        updatedFrom: str | None = None,  # noqa: N803
        authorIds: list[str] | None = None,  # noqa: N803
        issueIds: list[str] | None = None,  # noqa: N803
        projectIds: list[str] | None = None,  # noqa: N803
        offset: int | None = None,
        limit: int | None = None,
    ) -> Any:
        params = {"offset": 0 if offset is None else offset, "limit": self._limit if limit is None else limit}
        data: dict[str, Any] = {
            "from": resolve_date(dateFrom).isoformat(),
            "to": resolve_date(dateTo).isoformat(),
        }
        if updatedFrom:
            data["updatedFrom"] = updatedFrom
        if authorIds:
            data["authorIds"] = authorIds
        if issueIds:
            data["issueIds"] = issueIds
        if projectIds:
            data["projectIds"] = projectIds
        return self.post("/worklogs/search", params=params, data=data)

    def create_worklog(
        self,
        accountId: str,  # noqa: N803
        issueId: str | int,  # noqa: N803
        dateFrom: str | date | datetime,  # noqa: N803
        timeSpentSeconds: int,  # noqa: N803
        billableSeconds: int | None = None,  # noqa: N803
        description: str | None = None,
        remainingEstimateSeconds: int | None = None,  # noqa: N803
        startTime: str | None = None,  # noqa: N803
        attributes: list[dict[str, Any]] | None = None,
    ) -> Any:
        data: dict[str, Any] = {
            "authorAccountId": str(accountId),
            "issueId": int(issueId),
            "startDate": resolve_date(dateFrom).isoformat(),
            "timeSpentSeconds": int(timeSpentSeconds),
            "attributes": attributes,
        }
        if billableSeconds:
            data["billableSeconds"] = int(billableSeconds)
        if description:
            data["description"] = str(description)
        if remainingEstimateSeconds:
            data["remainingEstimateSeconds"] = int(remainingEstimateSeconds)
        if startTime:
            data["startTime"] = resolve_time(startTime).isoformat()
        return self.post("/worklogs", data=data)

    def update_worklog(
        self,
        id: str,  # noqa: A002
        accountId: str,  # noqa: N803
        dateFrom: str | date | datetime,  # noqa: N803
        timeSpentSeconds: int,  # noqa: N803
        billableSeconds: int | None = None,  # noqa: N803
        description: str | None = None,
        remainingEstimateSeconds: int | None = None,  # noqa: N803
        startTime: str | None = None,  # noqa: N803
    ) -> Any:
        data: dict[str, Any] = {
            "authorAccountId": str(accountId),
            "startDate": resolve_date(dateFrom).isoformat(),
            "timeSpentSeconds": int(timeSpentSeconds),
        }
        if billableSeconds:
            data["billableSeconds"] = int(billableSeconds)
        if description:
            data["description"] = str(description)
        if remainingEstimateSeconds:
            data["remainingEstimateSeconds"] = int(remainingEstimateSeconds)
        if startTime:
            data["startTime"] = resolve_time(startTime).isoformat()
        return self.put(f"/worklogs/{id}", data=data)

    def delete_worklog(self, id: str) -> Any:  # noqa: A002
        return self.delete(f"/worklogs/{id}")

    def create_customer(
        self,
        key: str | None = None,
        name: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        if not data:
            data = {"key": key, "name": name}
        return self.post("/customers", data=data)

    def update_customer(
        self,
        key: str | None = None,
        name: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        if not data:
            data = {"key": key, "name": name}
        return self.put(f"/customers/{key}", data=data)

    def create_account(
        self,
        key: str | None = None,
        leadAccountId: str | None = None,  # noqa: N803
        name: str | None = None,
        status: str | None = None,
        categoryKey: str | None = None,  # noqa: N803
        contactAccountId: str | None = None,  # noqa: N803
        customerKey: str | None = None,  # noqa: N803
        externalContactName: str | None = None,  # noqa: N803
        isGlobal: bool | None = None,  # noqa: N803
        data: dict[str, Any] | None = None,
    ) -> Any:
        if not data:
            data = {
                "key": key,
                "leadAccountId": leadAccountId,
                "name": name,
                "status": status,
                "categoryKey": categoryKey,
                "contactAccountId": contactAccountId,
                "customerKey": customerKey,
                "externalContactName": externalContactName,
                "global": isGlobal,
            }
        return self.post("/accounts", data=data)

    def update_account(
        self,
        key: str | None = None,
        leadAccountId: str | None = None,  # noqa: N803
        name: str | None = None,
        status: str | None = None,
        categoryKey: str | None = None,  # noqa: N803
        contactAccountId: str | None = None,  # noqa: N803
        customerKey: str | None = None,  # noqa: N803
        externalContactName: str | None = None,  # noqa: N803
        isGlobal: bool | None = None,  # noqa: N803
        data: dict[str, Any] | None = None,
    ) -> Any:
        if not data:
            data = {
                "key": key,
                "leadAccountId": leadAccountId,
                "name": name,
                "status": status,
                "categoryKey": categoryKey,
                "contactAccountId": contactAccountId,
                "customerKey": customerKey,
                "externalContactName": externalContactName,
                "global": isGlobal,
            }
        return self.put(f"/accounts/{key}", data=data)
