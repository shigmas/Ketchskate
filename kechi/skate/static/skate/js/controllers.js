'use strict';

/* Controllers */

var SkateModule = angular.module('SkateModule', []);

SkateModule.factory('SkateService', function($http) {
    var svc = {}
    var _setHeader = function() {
        $http.defaults.headers.post['X-CSRFTOKEN'] = Cookies.get('csrftoken');
    }

    var _getList = function(ctrlr) {
        _setHeader()
        $http.post('/skate/v1/get_items/', {}).
                   // New style
            then(function(data, status, headers, config) { 
                // after we login, set the header again for a new csrf token
                ctrlr.product_list = data['data']['product_items']
                console.log('fetched items: ',
                            Object.keys(ctrlr.product_list).length)
            },function(data, status, headers, config) { 
                // after we login, set the header again for a new csrf token
                $scope.errorMessage = 'error'
            });
    }
    svc.getList = _getList

    svc.getStores = function(ctrlr) {
        _setHeader()
        $http.post('/skate/v1/get_stores/', {}).
                   // New style
            then(function(data, status, headers, config) { 
                // after we login, set the header again for a new csrf token
                ctrlr.stores = data['data']['stores']
                console.log('fetched stores: ',
                            Object.keys(ctrlr.stores).length)
            },function(data, status, headers, config) { 
                // after we login, set the header again for a new csrf token
                $scope.errorMessage = 'error'
            });
    }

    svc.saveProduct = function(ctrlr, prodIdentifier, prodUrl) {
        _setHeader()
        $http.post('/skate/v1/add_item/',
                   {'product_url': prodUrl,
                    'product_identifier': prodIdentifier}).
            // New style
            then(function(data, status, headers, config) { 
                // after we login, set the header again for a new csrf token
                console.log('Saved Product')
                _getList(ctrlr)
            },function(data, status, headers, config) { 
                // after we login, set the header again for a new csrf token
                $scope.errorMessage = 'error'
            });
    }

    svc.deleteProducts = function(ctrlr, prodIds) {
        _setHeader()
        $http.post('/skate/v1/delete_multiple_items/',
                   {'product_ids': prodIds}).
            // New style
            then(function(data, status, headers, config) { 
                // after we login, set the header again for a new csrf token
                console.log('Deleted ids')
                _getList(ctrlr)
            },function(data, status, headers, config) { 
                // after we login, set the header again for a new csrf token
                $scope.errorMessage = 'error'
            });
    }
    /*
    svc.getProduct = function(ctrlr, productId) {
        $http.post('/skate/v2/get_item/', {'id':eventId}).
                   // New style
            then(function(data, status, headers, config) { 
                // after we login, set the header again for a new csrf token
                ctrlr.vote_list = data['data']['vote_list']
                ctrlr.vote = data['data']['vote']
            },function(data, status, headers, config) { 
                // after we login, set the header again for a new csrf token
                $scope.errorMessage = 'error'
            });
    }
*/

    return svc
});

SkateModule.controller('SkateListCtrlr', ['SkateService',
    function(SkateService) {
        var self = this
        /* Get this called to populate the product list */
        SkateService.getList(self)
        SkateService.getStores(self)

        this.addNewProduct = function() {
            console.log('adding')
 
            if (this.product.identifier &&
                this.product.url) {
                SkateService.saveProduct(this, this.product.identifier,
                                         this.product.url)
                self.errorMessage = ""
            } else  {  
                self.errorMessage = "invalid value"
            }
            
        }

        this.deleteProducts = function() {
            // Get the id's to delete
            //console.log("product_list: " + Object.keys(this.product_list))
            var productKey
            var idsToDelete = []
            for (productKey in this.product_list) {
                var product = this.product_list[productKey]
                //console.log("checked ident: " + product['urlPath'])
                //console.log("checked state: " + product.isChecked)
                if (product.isChecked == 'YES') {
                    console.log('item checked: ' + product.urlPath)
                    idsToDelete.push(productKey)
                }
            }
            console.log('deleting ' + idsToDelete)
            SkateService.deleteProducts(this, idsToDelete)
        }
    }
]);

SkateModule.controller('SkateEventCtrlr', ['SkateService',
                                                   '$routeParams',
    function(SkateService, $routeParams) {
        var self = this
        SkateService.getInfo(self)
        SkateService.getEvent(self, $routeParams.eventId)

        this._verifyValue = function(val) {
            return val >= 0 && val <= 5
        }



        this.submitVote = function() {
            console.log('voting')
 
            if (this._verifyValue(this.vote.crust) &&
                this._verifyValue(this.vote.sauce) &&
                this._verifyValue(this.vote.service) &&
                this._verifyValue(this.vote.creativity) && 
                this._verifyValue(this.vote.overall)) {
                SkateService.setVote(this, $routeParams.eventId, this.vote)
                self.errorMessage = ""
                // Update the vote_list with the new info
                //for (var vote in this.vote_list) {
                for (var i = 0 ; i < this.vote_list.length ; ++i) {
                    if (this.vote_list[i].login == this.login) {
                        console.log('match')
                        this.vote_list[i] = this.vote
                    }
                }
            } else  {  
                self.errorMessage = "invalid value"
            }
            
        }
    }
]);
