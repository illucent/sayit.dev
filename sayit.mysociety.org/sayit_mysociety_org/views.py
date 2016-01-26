# -*- coding: utf-8 -*-

import hashlib
import urlparse
import re
import calendar
import json
import requests
import datetime

from string import maketrans
from collections import defaultdict
from heapq import nlargest
from operator import itemgetter

from django import template
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.http import int_to_base36
from django.utils.html import strip_tags
from django.views.generic.edit import CreateView, FormView

from django.views.generic import (
    View, CreateView, UpdateView, DeleteView, DetailView, ListView,
    RedirectView, FormView,
    )

from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.template import Context, loader
from django.db.models import Count
from django.http.response import HttpResponse

from allauth.account.adapter import get_adapter
from allauth.account.views import PasswordResetFromKeyView
from allauth.account.signals import password_reset

from speeches.models import Speech, Section, Speaker
from speeches.search import SpeakerForm
from speeches.views import (
    NamespaceMixin, ParentlessList
    )

from instances.models import Instance
from instances.views import InstanceFormMixin, InstanceViewMixin

from haystack.forms import SearchForm
from haystack.query import RelatedSearchQuerySet
from haystack.views import SearchView
from popolo.models import Organization

from forms import ShareForm

def wordcloud(request):
    
    STOPWORDS = frozenset([
        # nltk.corpus.stopwords.words('english')
        u'i', 'ume', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your',
        u'yours', u'yourself', u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her',
        u'hers', u'herself', u'it', u'its', u'itself', u'they', u'them', u'their', u'theirs',
        u'themselves', u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those',
        u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had',
        u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if',
        u'or', u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', 'with',
        'about', 'against', 'between', 'into', 'through', 'during', 'before', u'after',
        u'above', u'below', u'to', u'from', u'up', u'down', u'in', u'out', u'on', u'off', u'over',
        u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where',
        u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other',
        u'some', u'such', u'no', u'nor', 'unot', u'only', u'own', u'same', u'so', u'than', u'too',
        u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now',
        # @see https://github.com/rhymeswithcycle/openparliament/blob/master/parliament/text_analysis/frequencymodel.py
        u"it's", u"we're", u"we'll", u"they're", u"can't", u"won't", u"isn't", "don't", "he's",
        u"she's", u"i'm", u"aren't", "government", "house", "committee", "would", "speaker",
        "motion", "mr", u"mrs", u"ms", u"member", u"minister", u"canada", u"members", u"time",
        u"prime", u"one", u"parliament", u"us", u"bill", u"act", u"like", u"canadians", u"people",
        u"said", u"want", u"could", u"issue", u"today", u"hon", u"order", u"party", u"canadian",
        u"think", u"also", u"new", u"get", u"many", u"say", u"look", u"country", u"legislation",
        u"law", u"department", u"two", u"day", u"days", u"madam", u"must", u"that's", u"okay",
        u"thank", u"really", u"much", u"there's", u"yes", u"no",
        # HTML tags
        'sup',
        # Nova Scotia
        u"nova", u"scotia", u"scotians", u"province", u"honourable", u"premier",
        # artifacts
        u"\ufffd", u"n't",
        # spanish
        u'00', u'0', u'esas', u'quiero', u'haciendo', u'otro', u'otra', u'otras', u'toda', u'toditos',
        u'aquí', u'sus', u'hace', u'con', u'creo', u'0000', u'dos', u'estos', u'fue', u'ahí', u'contra',
        u'de', u'durante', u'en', u'hacia', u'hasta', u'mediante', u'según', u'so', u'tras', u'decir',
        u'parte', u'años', u'esos', u'les', u'unos', u'este', u'ser', u'sino', u'entonces', u'hecho',
        u'ustedes', u'usted', u'van', u'sea', u'cada', u'debe', u'manera', u'nos', u'ellos', u'sin', u'las',
        u'esto', u'pero', u'eso', u'una', u'porque', u'hay', u'esta', u'están', u'está', u'donde', u'más', u'son',
        'todos', 'ese', 'estamos', 'hoy', 'como', 'han', 'tenemos', 'hemos', 'momento', 'puede',
        u'señor', u'señora', u'haciendonos', u'día', u'a', u'ante', u'bajo', u'cabe', u'no', u'No', u'el',
        u'Y', u'si', u'o', u'y', u'estas', u'debido', u'ya', u'qué', u'todo', u'esa', u'desde', u'del', u'para',
        u'uno', u'por', u'que', u'los', u'solo', u'dentro', u'podemos', u'algunos', u'estar', u'ahora',
        u'tema', u'mismo', u'sólo', u'temas', u'tiene', u'muy', u'cuando', u'nosotros', u'doctor',
        u'hacer', u'tienen', u'sobre', u'vamos', u'tres', u'así', u'ver', u'bien', u'cómo', u'entre', u'mucho',
        u'otros', 'todas', '000', 'voy', 'sido', 'era', 'vez', 'unas', 'cosas', 'general', 'tanto',
        u'frente', u'muchas', u'tener', u'tipo', u'mil', u'estoy', u'gran', u'san', u'tan', u'tengo', u'cual',
        u'dice', u'mayor', u'allá', u'solamente', u'bueno', u'primeramente', u'pues', u'consiguiente',
        u'debido', u'cuenta', u'menos', u'también', u'palabra',
    ])
    
    r_punctuation = re.compile(r"[^\s\w0-9'??-]", re.UNICODE)
    r_whitespace = re.compile(r'[\s?]+')

    hansard = Section.objects.filter(parent=None).order_by('-start_date').first()

    # Get the latest hansard's speeches as in DebateDetailView.
    section_ids = []
    for section in hansard._get_descendants(include_self=True):
        if section.title != 'NOTICES OF MOTION UNDER RULE 32(3)':
            section_ids.append(section.id)
    speeches = Speech.objects.filter(section__in=section_ids)

    # @see https://github.com/rhymeswithcycle/openparliament/blob/master/parliament/text_analysis/analyze.py
    # @see https://github.com/rhymeswithcycle/openparliament/blob/master/parliament/text_analysis/frequencymodel.py

    # get the counts of all non-stopwords.
    word_counts = defaultdict(int)
    total_count = 0

    for speech in speeches:
        for word in r_whitespace.split(r_punctuation.sub(' ', strip_tags(speech.text).lower())):
            if word not in STOPWORDS and len(word) > 2:
                word_counts[word] += 1
                total_count += 1
                
    topN = 59 # top N words
    word_counts = {word: count for word, count in word_counts.items()}
    most_common = nlargest(topN, word_counts.items(), key=itemgetter(1))
    most_common_words = json.dumps(most_common, ensure_ascii=False, encoding='UTF-8') # unicode handling

    return HttpResponse(most_common_words.encode(encoding='latin-1'), content_type='application/json, charset=UTF-8')
    
class InstanceCreate(CreateView):
    model = Instance
    fields = ['label', 'title', 'description']

    def is_stashed(self):
        return self.request.GET.get('post') and self.request.session.get('instance')

    def get(self, request, *args, **kwargs):
        if self.is_stashed():
            return self.post(request, *args, **kwargs)
        return super(InstanceCreate, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(InstanceCreate, self).get_form_kwargs()
        if self.is_stashed():
            kwargs['data'] = self.request.session['instance']
            del self.request.session['instance']
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_authenticated():
            form.instance.created_by = self.request.user
            redirect = super(InstanceCreate, self).form_valid(form)
            self.object.users.add(self.request.user)
            return redirect
        else:
            self.request.session['instance'] = form.cleaned_data
            return redirect_to_login(
                self.request.path + '?post=1',
                login_url=reverse("account_signup"),
            )


class ShareWithCollaborators(InstanceFormMixin, FormView):
    template_name = 'share_instance_with_collaborators.html'

    form_class = ShareForm
    success_url = reverse_lazy('share_instance')

    # substantially cargo-culted from allauth.account.forms.ResetPasswordForm
    def form_valid(self, form):
        email = form.cleaned_data["email"]

        users = form.users
        if users:
            context = {
                "instance": self.request.instance,
                "inviter": self.request.user,
                "invitee": users[0],
                }
            get_adapter().send_mail('instance_invite_existing',
                                    email,
                                    context)
            user_ids = [x.id for x in users]

        else:
            # Create a new user with email address as username
            # or a bit of a hash of the email address if it's longer
            # than Django's 30 character username limit.
            if len(email) > 30:
                username = hashlib.md5(email).hexdigest()[:10]
            else:
                username = email

            # Let's try creating a new user and sending an email to them
            # with a link to the password reset page.
            # FIXME - should probably try/catch the very unlikely situation
            # where we have a duplicate username, I guess.
            user = User.objects.create_user(username, email=email)
            user_ids = (user.id,)

            temp_key = default_token_generator.make_token(user)

            instance_url = self.request.instance.get_absolute_url()

            # send the password reset email
            path = reverse("instance_accept_invite",
                           kwargs=dict(uidb36=int_to_base36(user.id),
                                       key=temp_key))
            url = urlparse.urljoin(instance_url, path)
            context = {
                "instance": self.request.instance,
                "inviter": self.request.user,
                "invitee": user,
                "password_reset_url": url,
                }
            get_adapter().send_mail('accept_invite',
                                    email,
                                    context)

        self.request.instance.users.add(*user_ids)

        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Your invitation has been sent.',
            )
        return super(ShareWithCollaborators, self).form_valid(form)


class AcceptInvite(PasswordResetFromKeyView):
    template_name = 'accept_invitation.html'
    success_message_template = 'messages/accept_invite_success.txt'

    def get_success_url(self):
        return reverse('speeches:home')

    def form_valid(self, form):
        form.save()
        get_adapter().add_message(self.request,
                                  messages.SUCCESS,
                                  self.success_message_template)
        password_reset.send(sender=self.reset_user.__class__,
                            request=self.request,
                            user=self.reset_user)
        get_adapter().login(self.request, self.reset_user)

        return super(PasswordResetFromKeyView, self).form_valid(form)
