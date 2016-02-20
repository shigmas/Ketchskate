from django.http import JsonResponse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.generic import View

from django.contrib import auth

from django.db.models import Avg

# Template libs
from django.shortcuts import render

import datetime
from django.utils import timezone

import string
import inspect
import types

from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from skate import ImageParsers

from urllib.parse import urlparse

import os
import json

from skate.models import *

class BaseView(View):
    command = None
    version = None

    def get(self, request):
        return self._handleCommand()

    def post(self, request):
        return self._handleCommand()

    def _getContent(self, request):
        content = None
        error = None
        if self.version == 'v1':
            # returns a dictionary from a POST request body in JSON format
            try:
                content = json.loads(str(request.body, encoding='utf-8'))
            except ValueError:
                error = 'Invalid JSON content in request body: (%s)' % content
                content = None
        else:
            content = self.request.POST

        return content, error
    
    
# Just loads template pages. almost statically
class PageView(BaseView):
    template = None

    def _handleCommand(self):
        page = 'skate/' + self.template
        return render(self.request,page,{})

class HomeView(BaseView):
    def _handleCommand(self):
        content = {}
        return render(self.request,'skate/index.html',content)

class StoreView(BaseView):

    def _handleCommand(self):
        content, error = self._getContent(self.request)

        commandDict = {'get_stores': self._getStores,
        }

        action = commandDict.get(self.command, None)
        if action is None:
            print('no command for %s' % self.command)
            return JsonResponse({}, safe=True)

        result, success = action(content)
        if self.version == 'v1':
            # return JSON result
            content = {}
            if success:
                if type(result) == type({}):
                    content = result
            else:
                content['message'] = result
            content['result'] = success
            return JsonResponse(content, safe=True)
        else:
            # return HTTP content (which is just to redirect to home, in this
            # case
            return HttpResponseRedirect('/skate/')

    def _getStores(self, content):

        stores = Store.objects.all()
        if self.version == 'v1':
            # for JSON, we convert the object to a python dictionary
            storesDict = None
            if stores:
                storesDict = {}
                for i in stores:
                    iDict = {}
                    fields = i._meta.concrete_fields
                    storeId = None
                    for field in fields:
                        if field.name == 'id':
                            storeId = getattr(i, field.name)
                        iDict[field.name] = getattr(i, field.name)
                    if storeId is not None:
                        storesDict[storeId] = iDict
            content['stores'] = storesDict
        else:
            # For a template to process
            content['stores'] = stores

        return content, True

class ItemView(BaseView):

    def _handleCommand(self):
        content, error = self._getContent(self.request)

        commandDict = {'add_item': self._addItem,
                       'get_items': self._getItems,
                       'delete_item': self._deleteItem,
                       'delete_items': self._deleteItems}

        action = commandDict.get(self.command, None)
        if action is None:
            print('no command for %s' % self.command)
            return JsonResponse({}, safe=True)

        result, success = action(content)
        if self.version == 'v1':
            # return JSON result
            content = {}
            if success:
                if type(result) == type({}):
                    content = result
            else:
                content['message'] = result
            content['result'] = success
            return JsonResponse(content, safe=True)
        else:
            # return HTTP content (which is just to redirect to home, in this
            # case
            return HttpResponseRedirect('/skate/')

    def _getStoreFromHost(self, sentUrlHost):
        if sentUrlHost.startswith('m.'):
            host = sentUrlHost.replace('m.','',1)
        else:
            host = sentUrlHost
        print('looking for host: %s' % host)
        return Store.objects.filter(host__contains=host)

    def _addItem(self, content):
        if not self.request.user.is_authenticated():
            return 'User is not logged in', False

        productUrl = content.get('product_url',None)
        productId = content.get('product_identifier',None)
        productLimitPrice = content.get('product_limit_price',None)
        urlPieces = urlparse(productUrl)
        if productUrl is not None and productId is not None and \
           (urlPieces.scheme == 'http' or urlPieces.scheme == 'https'):
            # The URL may have been sent to us with 'm.<domain>', but we'll
            # save it with the canonical hostname
            store = self._getStoreFromHost(urlPieces.netloc)
            if len(store) == 1:
                parser = ImageParsers.GetParser(store[0].name)
                urlPath = '%s?%s' % (urlPieces.path, urlPieces.query)
                parser.setPath(urlPath)
                parser.parse()
                print('found image: %s' % parser.mainImage)
                # Looks like we have enough information to get/create the item
                item = Item(identifier = productId,
                            createTime = timezone.now(),
                            creator = self.request.user,
                            urlPath = urlPath,
                            mainImageUrl = parser.mainImage,
                            altImageUrl = parser.altImage,
                            store = store[0],
                            sku = '000000')
                if productLimitPrice is not None:
                    item.productLimitPrice = productLimitPrice
                item.save()
                return None, True
            else:
                print('no store for %s' % urlPieces.netloc)
                return 'no store for url', False

        return 'not enough information to create item', False

    def _getItems(self, content):
        if not self.request.user.is_authenticated():
            return 'User is not logged in', False

        items = Item.objects.filter(creator=self.request.user)
        if self.version == 'v1':
            # for JSON, we convert the object to a python dictionary
            itemsDict = None
            if items:
                itemsDict = {}
                for i in items:
                    iDict = {}
                    fields = i._meta.concrete_fields
                    itemId = None
                    for field in fields:
                        if field.name == 'id':
                            itemId = getattr(i, field.name)
                        # Test if a relationship. If so, don't add it.
                        if field.name == 'urlPath':
                            store = getattr(i, 'store')
                            urlPath = getattr(i, field.name)
                            iDict['url'] = 'http://%s/%s' % (store.host, urlPath)
                        if field.rel is None:
                            iDict[field.name] = getattr(i, field.name)
                    if itemId is not None:
                        itemsDict[itemId] = iDict
            content['product_items'] = itemsDict
        else:
            content['product_items'] = items

        return content, True

    def _deleteItem(self, content):
        error = None
        if self.request.user.is_authenticated():
            itemId = int(content.get('product_id',None))
            print('getting item with id %s type: %s' % (itemId, type(itemId)))
            items = Item.objects.filter(pk= itemId, creator=self.request.user)
            # items should only be one.
            print('deleting items %s, count: %s' % (items, len(items)))
            if len(items) == 1:
                items[0].delete()
            else:
                error = 'No item %s for user %s' % (itemId, self.request.user)
        else:
            error = 'not logged in'

        if error:
            print('returning true')
            return error, False
        else:
            print('returning false')
            return error, True


    def _deleteItems(self, content):
        error = None
        print('deleting items')
        if self.request.user.is_authenticated():
            itemIds = content.get('product_ids',None)
            for itemIdParam in itemIds:
                itemId = int(itemIdParam)
                print('deleting %d' % itemId)
                items = Item.objects.filter(pk= itemId, creator=self.request.user)
                # items should only be one.
                if len(items) != 1:
                    error = 'No item %s for user %s' % (itemId, self.request.user)
                else:
                    items[0].delete()
        else:
            error = 'not logged in'

        if error:
            return error, False
        else:
            return error, True

class UserView(BaseView):
    
    def _handleCommand(self):
        content, error = self._getContent(self.request)

        commandDict = {
            # These are not JSON calls. They redirect back home
            'login': self._login,
            'create': self._create,
            'logout': self._logout,
            # These are JSON API calls
            'create_user': self._createUser,
            'login_user': self._loginUser,
            'logout_user': self._logoutUser,
            'delete_user': self._deleteUser,
            'get_user': self._getUser,
            'update_user': self._updateUser,
        }

        action = commandDict.get(self.command, None)
        if action is None:
            print('no command for %s' % self.command)

        result, success = action(content)
        if self.version == 'v1':
            # return JSON result
            # if ! success, result is a message string
            content = {}
            if success:
                if type(result) == type({}):
                    content = result
            else:
                content['message'] = result
            content['result'] = success
            return JsonResponse(content, safe=True)
        else:
            # return HTTP content (which is just to redirect to home, in this
            # case
            return HttpResponseRedirect('/skate/')

    def _getCreds(self, content):
        return (content.get('login',None), content.get('password',None),
                content.get('email',None))

    def _login(self, content):
        return self._loginUser(content)

    def _create(self, content):
        return self._createUser(content)

    def _logout(self, content):
        return self._logoutUser(content)

    def _createUser(self, content):
        login, password, email = self._getCreds(content)

        if email is None or login is None or password is None:
            return 'email is required to create a user', False
        else:
            user = auth.models.User.objects.create_user(login, email, password)
            if user is not None and user.is_active:
                user = auth.authenticate(username=login, password=password)
                return auth.login(self.request, user), True

        return 'Unable to create and login user', False

    def _loginUser(self, content):
        login, password, email = self._getCreds(content)

        if login is None or password is None:
            return 'login and password are required to login', False
        else:
            user = auth.authenticate(username=login, password=password)
            if user is not None and user.is_active:
                return auth.login(self.request, user), True

        return 'Unable to create and login user', False

    def _logoutUser(self, content):
        return auth.logout(self.request), True

    def _deleteUser(self, content):
        user = self.request.user
        if user and not user.is_anonymous():
            return user.delete(), True

        return 'Unable to delete user', False

    def _getUser(self, content):
        return 'not implemented'

    def _updateUser(self, content):
        return 'not implemented'
