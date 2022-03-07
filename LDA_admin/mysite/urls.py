from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()
from mysite.views import blog

from mysite.settings import STATIC_PATH

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
  #	(r'^admin/', include('django.contrib.admin.urls')),
    url(r'^hello$',"mysite.views.hello_page"),
    url(r'^request_one$',"mysite.views.request_doc_ajax"),
    url(r"^test/$", "mysite.views.hello"),
    url(r"^submit_token", "mysite.views.submit_token"),
    url(r"^topic/$", "mysite.views.topic"),
    url(r"^newword_single/$", "mysite.views.new_word_single"),
    url(r"^newword_compond/$", "mysite.views.new_word_compond"),
    url(r"^graph/$", "mysite.views.get_graph"),
    url(r"^newword_timeline$", "mysite.views.newword_timeline"),
    url(r"^newword_timeline_default", "mysite.views.newword_timeline_default"),
    url(r"^quality", "mysite.doc_quality_views.doc_quality_score"),
    url(r"^test_cache", "mysite.doc_quality_views.test_cache"),
   #  url(r"^teacher/$", "mysite.views.teacher_show"),
   #  url(r"^choice_teacher$", "mysite.views.choice_teacher"),
   #  url(r"^delete_choice", "mysite.views.delete_choice")
  	# (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':"static/"}),
) 

