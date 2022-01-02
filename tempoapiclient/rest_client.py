# coding=utf-8
import logging
import requests
from requests.exceptions import HTTPError
from json import dumps
from six.moves.urllib.parse import urlencode

log = logging.getLogger()


class RestAPIClient(object):
    default_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = None

    def __init__(self, url="", auth_token=None, timeout=None, verify_ssl=None, proxies=None, advanced_mode=None):
        self._url = url
        self._auth_token = auth_token
        self._timeout = timeout
        self._verify_ssl = verify_ssl
        self._proxies = proxies
        self._advanced_mode = advanced_mode
        self._session = requests.Session()
        self._update_header("Authorization", "Bearer {}".format(auth_token))

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _update_header(self, key, value):
        """
        Update header for exist session
        :param key:
        :param value:
        :return:
        """
        self._session.headers.update({key: value})

    def _response_handler(self, response):

        if self._advanced_mode:
            return response

        try:
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
            return response.json()

        except HTTPError as http_err:
            log.error(f'HTTP error occurred: {http_err.response.text}')
            raise SystemExit(http_err)
        except Exception as err:
            log.error(err)
            raise SystemExit(err)

    @staticmethod
    def url_joiner(url, path, trailing=None):
        url_link = path
        if url:
            url_link = '/'.join(s.strip('/') for s in [url, path])
        if trailing:
            url_link += '/'
        return url_link

    def close(self):
        return self._session.close()

    def _request(self, method='GET', path='/', data=None, json=None, flags=None, params=None, headers=None,
                 files=None, trailing=None):
        """

        :param method:
        :param path:
        :param data:
        :param json:
        :param flags:
        :param params:
        :param headers:
        :param files:
        :param trailing: bool
        :return:
        """
        url = self.url_joiner(self._url, path, trailing)
        if params or flags:
            url += '?'
        if params:
            url += urlencode(params or {})
        if flags:
            url += ('&' if params else '') + '&'.join(flags or [])
        json_dump = None
        if files is None:
            data = None if not data else dumps(data)
            json_dump = None if not json else dumps(json)

        headers = headers or self.default_headers
        response = self._session.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            json=json,
            timeout=self._timeout,
            verify=self._verify_ssl,
            files=files,
            proxies=self._proxies
        )
        response.encoding = 'utf-8'

        log.debug("HTTP: {} {} -> {} {}".format(method, path, response.status_code, response.reason))
        return response

    def get(self, path, data=None, flags=None, params=None, headers=None, not_json_response=None, trailing=None):
        """
        Get request based on the python-requests module. You can override headers, and also, get not json response
        :param path:
        :param data:
        :param flags:
        :param params:
        :param headers:
        :param not_json_response: OPTIONAL: For get content from raw requests packet
        :param trailing: OPTIONAL: for wrap slash symbol in the end of string
        :return:
        """
        response = self._request('GET', path=path, flags=flags, params=params, data=data, headers=headers,
                                 trailing=trailing)

        return self._response_handler(response)

    def post(self, path, data=None, json=None, headers=None, files=None, params=None, trailing=None):
        response = self._request('POST', path=path, data=data, json=json, headers=headers, files=files, params=params,
                                 trailing=trailing)
        return self._response_handler(response)

    def put(self, path, data=None, headers=None, files=None, trailing=None, params=None):
        response = self._request('PUT', path=path, data=data, headers=headers, files=files, params=params,
                                 trailing=trailing)
        return self._response_handler(response)

    def delete(self, path, data=None, headers=None, params=None, trailing=None):
        """
        Deletes resources at given paths.
        :rtype: dict
        :return: Empty dictionary to have consistent interface.
        """
        response = self._request('DELETE', path=path, data=data, headers=headers, params=params, trailing=trailing)
        return self._response_handler(response)
