u"""Tools to access the PlugIt API"""

import requests


class PlugItAPI(object):
	u"""Main instance to access PlugIt API"""

	def __init__(self, url):
		u"""Create a new PlugItAPI instance, need url as the main endpoint for the API"""
		self.url = url

	def _request(self, uri, params=None, data=None, verb=u'GET'):
		u"""Call a method of the PlugIt API"""
		return getattr(requests, verb.lower())(self.url + uri, params=params, data=data, stream=True)

	def get_user(self, user_pk):
		u"""Return the user with id (private key) equal to user_pk"""
		request = self._request(u'user/' + user_pk)
		if not request:
			return None

		# Base properties
		user = User()
		user.pk = user.id = user_pk

		# Copy data inside the user
		data = request.json()
		for attr in data:
			setattr(user, attr, data[attr])

		return user


class User():
	u"""Represent an user"""

