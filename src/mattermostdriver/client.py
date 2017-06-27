import json

import logging
import requests

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('mattermostdriver.websocket')


class InvalidOrMissingParameters(requests.HTTPError):
	"""
	Raised when mattermost returns a
	400 Invalid or missing parameters in URL or request body
	"""


class NoAccessTokenProvided(requests.HTTPError):
	"""
	Raised when mattermost returns a
	401 No access token provided
	"""


class NotEnoughPermissions(requests.HTTPError):
	"""
	Raised when mattermost returns a
	403 Do not have appropriate permissions
	"""


class ResourceNotFound(requests.HTTPError):
	"""
	Raised when mattermost returns a
	404 Resource not found
	"""


class ContentTooLarge(requests.HTTPError):
	"""
	Raised when mattermost returns a
	413 Content too large
	"""


class FeatureDisabled(requests.HTTPError):
	"""
	Raised when mattermost returns a
	501 Feature is disabled
	"""


class Client:
	def __init__(self, options):
		self._url = '{scheme:s}://{url:s}{basepath:s}'.format(
			scheme=options['scheme'],
			url=options['url'],
			basepath=options['basepath']
		)
		self._scheme = options['scheme']
		self._basepath = options['basepath']
		self._port = options['port']
		self._verify = options['verify']
		self._token = ''
		self._cookies = None
		self._userid = ''
		self._username = ''

	@property
	def userid(self):
		return self._userid

	@userid.setter
	def userid(self, user_id):
		self._userid = user_id

	@property
	def username(self):
		return self._username

	@username.setter
	def username(self, username):
		self._username = username

	@property
	def url(self):
		return self._url

	@property
	def cookies(self):
		return self._cookies

	@cookies.setter
	def cookies(self, cookies):
		self._cookies = cookies

	@property
	def token(self):
		return self._token

	@token.setter
	def token(self, t):
		self._token = t

	def auth_header(self):
		if self._token == '':
			return {}
		return {"Authorization": "Bearer {token:s}".format(token=self._token)}

	def make_request(self, method, endpoint, options=None, params=None, data=None):
		if options is None:
			options = {}
		if params is None:
			params = {}
		if data is None:
			data = {}
		method = method.lower()
		request = requests.get
		if method == 'post':
			request = requests.post
		elif method == 'put':
			request = requests.put
		elif method == 'delete':
			request = requests.delete

		response = request(
				self.url + endpoint,
				headers=self.auth_header(),
				verify=self._verify,
				json=options,
				params=params,
				data=data
			)
		try:
			response.raise_for_status()
		except requests.HTTPError as e:
			data = json.loads(e.response.text)
			if data['status_code'] == 400:
				raise InvalidOrMissingParameters(data['message'])
			elif data['status_code'] == 401:
				raise NoAccessTokenProvided(data['message'])
			elif data['status_code'] == 403:
				raise NotEnoughPermissions(data['message'])
			elif data['status_code'] == 413:
				raise ContentTooLarge(data['message'])
			elif data['status_code'] == 501:
				raise FeatureDisabled(data['message'])
			else:
				raise

		log.debug(json.loads(response.text))
		return response

	def get(self, endpoint, options=None, params=None):
		return json.loads(
			self.make_request('get', endpoint, options=options, params=params).text
		)

	def post(self, endpoint, options=None, params=None, data=None):
		return json.loads(
			self.make_request('post', endpoint, options=options, params=params, data=data).text
		)

	def put(self, endpoint, options=None, params=None, data=None):
		return json.loads(
			self.make_request('put', endpoint, options=options, params=params, data=data).text
		)

	def delete(self, endpoint, options=None, params=None, data=None):
		return json.loads(
			self.make_request('delete', endpoint, options=options, params=params, data=data).text
		)