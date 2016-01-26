# -*- coding: utf8 -*-

import datetime
import re
import urllib
import urllib2

from django.conf import settings
from django.core.cache import cache
from django.core.files import File
from django.core import urlresolvers
from django.db import models
from django.template.defaultfilters import slugify

import lxml.html
