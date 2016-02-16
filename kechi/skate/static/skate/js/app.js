'use strict';

/* App Module */
var skateApp = angular.module('SkateApp', [
  'ngRoute',
  'SkateModule',
]);

skateApp.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/home', {
        templateUrl: '/skate/list-partial.html',
        // as ctrlr is more like naming the instance as opposed to an alias
        controller: 'SkateListCtrlr as ctrlr'
      }).
      when('/product/:productId', {
        templateUrl: '/skate/product-partial.html',
        controller: 'SkateProductCtrlr as ctrlr'
      }).
      otherwise({
        redirectTo: '/home'
      });
}]);
