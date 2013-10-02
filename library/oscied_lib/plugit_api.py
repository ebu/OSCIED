# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Project Manager  : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer   : David Fischer (david.fischer.ch@gmail.com)
#  PlugIt Developer : Maximilien Cuony (maximilien@theglu.org)
#  Copyright        : Copyright (c) 2012-2013 EBU. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of EBU Technology & Innovation OSCIED + PlugIt Projects.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/ebu/OSCIED

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

