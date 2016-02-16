from django.conf.urls import patterns, url

# It's a pretty straight forward mapping, and we don't want to have import
# every class separately.
#from skate.View import QueryView, UserView
import skate.View

urlpatterns = patterns('',
                       url(r'^$', skate.View.HomeView.as_view()),
                       url(r'^login.html$',
                           skate.View.PageView.as_view(template='login.html')),
                       url(r'^create.html$',
                           skate.View.PageView.as_view(template='create.html')),
                       url(r'^list-partial.html$',
                           skate.View.PageView.as_view(template='list-partial.html')),
                       url(r'^login/$',
                           skate.View.UserView.as_view(command='login')),
                       url(r'^create/$',
                           skate.View.UserView.as_view(command='create')),
                       url(r'^logout/$',
                           skate.View.UserView.as_view(command='logout')),
                       url(r'^add_product/$',
                           skate.View.ItemView.as_view(command='add_item')),

                       # JSON API URL's. Some repitition, but saves
                       # a tiny bit of processing in the View
                       url(r'^v1/add_item/$',
                           skate.View.ItemView.as_view(command='add_item',
                                                       version='v1')),
                       url(r'^v1/get_items/$',
                           skate.View.ItemView.as_view(command='get_items',
                                                       version='v1')),
                       url(r'^v1/delete_item/$',
                           skate.View.ItemView.as_view(command='delete_item',
                                                       version='v1')),

                       url(r'^v1/delete_multiple_items/$',
                           skate.View.ItemView.as_view(command='delete_items',
                                                       version='v1')),

                       url(r'^v1/create_user/$',
                           skate.View.UserView.as_view(command='create_user',
                                                       version='v1')),
                       url(r'^v1/login_user/$',
                           skate.View.UserView.as_view(command='login_user',
                                                       version='v1')),
                       url(r'^v1/logout_user/$',
                           skate.View.UserView.as_view(command='logout_user',
                                                       version='v1')),
                       url(r'^v1/delete_user/$',
                           skate.View.UserView.as_view(command='delete_user',
                                                       version='v1')),
                       url(r'^v1/get_user/$',
                           skate.View.UserView.as_view(command='get_user',
                                                       version='v1')),
                       url(r'^v1/update_user/$',
                           skate.View.UserView.as_view(command='update_user',
                                                       version='v1')),
                       
)
