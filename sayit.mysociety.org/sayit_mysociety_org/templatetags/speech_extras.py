# -*- coding: utf-8 -*-

import re
import json
import bleach

from collections import defaultdict
from heapq import nlargest
from operator import itemgetter
from django import template
from django.utils.html import strip_tags
from unicodedata import normalize
from speeches.models import Speech, Section, Speaker
from django.db.models import Count
from django.template.defaultfilters import stringfilter
from django.utils.html import linebreaks
from django.utils.safestring import mark_safe, SafeData
from django_bleach.templatetags.bleach_tags import bleach_args

register = template.Library()

@register.top_speakers_tag
def get_top_speakers(count=9):
    
    top_speakers_list = Speech.objects.values('speaker').annotate(count=Count('speaker')).order_by('speaker').order_by(
        '-count')[0:count]
    top_speakers = []
    for speaker in top_speakers_list:
        the_speaker = Speaker.objects.get(pk=speaker['speaker'])
        # setattr(the_speaker, 'count', speaker['count])
        the_speaker.count = speaker['count']
        top_speakers.append(the_speaker)
    return top_speakers