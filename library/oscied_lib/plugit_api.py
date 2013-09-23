u"""Tools to access the PlugIt API"""

import requests


class PlugItAPI(object):
	u"""Main instance to access PlugIt API"""

	def __init__(self, url):
		u"""Create a new PlugItAPI instance, need URL as the main endpoint for the API"""
		self.url = url

	def _request(self, uri, params=None, data=None, verb=u'GET'):
		u"""Call a method of the PlugIt API"""
		return getattr(requests, verb.lower())(self.url + uri, params=params, data=data, stream=True)

	def get_user(self, user_pk):
		u"""Return the user with id (private key) equal to user_pk"""
		response = self._request(u'user/' + user_pk)
		if response:
			# Set base properties and copy data inside the user
			user = User()
			user.pk = user.id = user_pk
			user.__dict__.update(response.json())
			return user
		return None

	def get_organization(self, organization_pk):
		u"""Return an organization with id (private key) equal to organization_pk"""
		response = self._request(u'orga/' + organization_pk)
		if response:
			# Set base properties and copy data inside the organization
			organization = Organization()
			organization.pk = organization.id = organization_pk
			organization.__dict__.update(response.json())
			return organization
		return None

class User(object):
	u"""Represent an user"""

class Organization(object):
	u"""Represent an organization"""

