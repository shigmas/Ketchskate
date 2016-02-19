from django.test import TestCase

# Tests for working through the Entry/Accessor api.  We need a model to start
# with, so we just use our "real" one.


from django.contrib.auth.models import User

import datetime

import time

import json

import os.path
import os

appUrl = '/skate'

def _createV1Url(path):
    return os.path.join(appUrl,'v1',path) + '/'

# Actually, the base class for all tests.
class UserViewTests(TestCase):
    user = 'user'
    password = 'password'
    email = 'test0@futomen.net'

    def _createUser(self, user, password, email, expectSuccess = True,
                    message=None):
        data = {'login':user,
                'password':password,
                'email':email,
        }

        jsonData = json.dumps(data)
        url = _createV1Url('create_user')
        response = self.client.post(url, jsonData,
                                    content_type='application/json')
        contents = json.loads(str(response.content, encoding='utf-8'))
        if expectSuccess:
            self.assertEquals(contents['result'],True)
        else:
            self.assertEquals(contents['result'],False)
            if message:
                self.assertEquals(contents['message'], message)

    def _deleteUser(self, expectedResult):
        # delete the logged in user
        response = self.client.post(_createV1Url('delete_user'), {},
                                    content_type='application/json')
        contents = json.loads(str(response.content, encoding='utf-8'))
        self.assertEquals(contents['result'],expectedResult)
        
                
    def testCreateUser(self):
        self._createUser(self.user,None,None, expectSuccess=False,
                         message='email is required to create a user')
        self._createUser(self.user,self.password,self.email, expectSuccess=True)

        # XXX - TBD: try and create the same user and fail. As soon as we add
        # the code.

        # This is a temporary database, but this is good practice
        self._deleteUser(True)

    def testDeleteUser(self):
        # we already tested successful delete, so just test fail
        self._deleteUser(False)

class ItemViewTests(UserViewTests):
    fixtures = ['stores.json']

    bloomProd0 = ('http://www1.bloomingdales.com/shop/product/andrew-marc-gayle-luxe-down-fur-trim-hooded-coat?ID=1402983&CategoryID=19718','fur coat',None)
    bloomProd1 = ('http://m.bloomingdales.com/shop/product/gucci-black-mirror-sunglasses?ID=1538465&CategoryID=1004011','Gucci sunglasses',None)

    nonStore0 = ('http://www.lululemon/this/does/not/matter.html','fur coat',None)

    def _createItem(self, product, expectSuccess=True, message=None):
        data = {'product_url':product[0],
                'product_identifier':product[1],
                'product_limit_price':product[2],
        }

        jsonData = json.dumps(data)
        url = _createV1Url('add_item')
        response = self.client.post(url, jsonData,
                                    content_type='application/json')
        contents = json.loads(str(response.content, encoding='utf-8'))
        if expectSuccess:
            self.assertEquals(contents['result'],True)
        else:
            self.assertEquals(contents['result'],False)
            if message:
                self.assertEquals(contents['message'], message)

    def _getItems(self, expectSuccess=True, message=None):
        url = _createV1Url('get_items')
        response = self.client.post(url, json.dumps({}),
                                    content_type='application/json')
        contents = json.loads(str(response.content, encoding='utf-8'))
        if expectSuccess:
            self.assertEquals(contents['result'],True)
            return contents['product_items']
        else:
            self.assertEquals(contents['result'],False)
            if message:
                self.assertEquals(contents['message'], message)
            return None

    def _deleteItem(self, itemId, expectSuccess=True, message=None):
        data = {'product_id':itemId,
        }

        jsonData = json.dumps(data)
        url = _createV1Url('delete_item')
        response = self.client.post(url, jsonData,
                                    content_type='application/json')
        contents = json.loads(str(response.content, encoding='utf-8'))
        if expectSuccess:
            self.assertEquals(contents['result'],True)
        else:
            self.assertEquals(contents['result'],False)
            if message:
                self.assertEquals(contents['message'], message)

    def _deleteItems(self, itemIds, expectSuccess=True, message=None):
        data = {'product_ids':itemIds,
        }

        jsonData = json.dumps(data)
        url = _createV1Url('delete_multiple_items')
        response = self.client.post(url, jsonData,
                                    content_type='application/json')
        contents = json.loads(str(response.content, encoding='utf-8'))
        if expectSuccess:
            self.assertEquals(contents['result'],True)
        else:
            self.assertEquals(contents['result'],False)
            if message:
                self.assertEquals(contents['message'], message)

    def testCreateItem(self):
        self._createItem(self.bloomProd0, False, 'User is not logged in')
        self._createUser(self.user,self.password,self.email, expectSuccess=True)

        self._createItem(self.bloomProd0)
        self._createItem(self.nonStore0,False,'no store for url')
        self._createItem((self.bloomProd0[0],None,None),False,
                         'not enough information to create item')

        # This is a temporary database, but this is good practice
        self._deleteUser(True)

    def testGetDeleteItems(self):
        self._getItems(False, 'User is not logged in')
        self._createUser(self.user,self.password,self.email, expectSuccess=True)

        self._createItem(self.bloomProd0)
        self._createItem(self.bloomProd1)
        items = self._getItems()
        self.assertEquals(len(items),2,'Unexpected number of items')
        print('got items: %s' % items.keys())
        for itemId in items.keys():
            self._deleteItem(itemId)

        # This is a temporary database, but this is good practice
        self._deleteUser(True)
        
