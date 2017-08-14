var app = angular.module('kportal', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);

app.controller('mainCtrl', ['$scope', function($scope){
    $scope.name = "test"
}])