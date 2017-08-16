var app = angular.module('myApp', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);

app.controller('mainCtrl', ['$scope', function($scope){
    $scope.name = "Hey, I am here!"
}]);