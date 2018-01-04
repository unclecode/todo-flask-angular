var app = angular.module('todoApp', ["ngRoute", 'ngCookies', 'ngMessages', 'LocalStorageModule','ngTagsInput', 'dndLists', 'angularMoment', 'angularTrix', 'ngSanitize', 'summernote']);

app.run(function ($rootScope, $templateCache) {
    $rootScope.$on('$viewContentLoaded', function () {
        $templateCache.removeAll();
    });
});

app.config(['$interpolateProvider', 'localStorageServiceProvider',
    function ($interpolateProvider, localStorageServiceProvider) {
        $interpolateProvider.startSymbol('{a');
        $interpolateProvider.endSymbol('a}');
        localStorageServiceProvider
            .setPrefix('todo')
            .setStorageType('sessionStorage')
            .setNotify(true, true)
    }]);

app.controller('mainCtrl', ['$scope', function ($scope) {
    $scope.name = "Hey, I am here!"
}]);


app.service('authService', ['$http', '$log', function ($http, $log) {
    var self = this;
    this.login = function (user) {
        return $http.post('/auth/login', user).then(function (res) {
            return res.data.result;
        }).catch(function (httpError) {
            $log.error('Error in Login: ' + httpError.status + " : " + JSON.stringify(httpError.data));
            throw httpError
        })
    }
    this.me = function () {
        return $http.get('/auth/me').then(function (res) {
            return res.data;
        }).catch(function (httpError) {
            $log.error('Error in Me: ' + httpError.status + " : " + JSON.stringify(httpError.data));
            throw httpError
        })
    }
    this.register = function (user) {
        return $http.post('/api/v1/users/', user).then(function (res) {
            return res.data;
        }).catch(function (httpError) {
            $log.error('Error in Login: ' + httpError.status + " : " + JSON.stringify(httpError.data));
            throw httpError
        })
    }
    this.getToken = function () {
        return $http.get('/auth/token').then(function (res) {
            if (res.status == 200) {
                self.authToken = res.data;
                setTimeout(self.getToken, self.authToken.expiration);
                $http.defaults.headers.common['Authentication'] = 'token ' + self.authToken.token;
                return self.authToken
            }

        }).catch(function (httpError) {
            $log.error('Error in Request Token: ' + httpError.status + " : " + JSON.stringify(httpError.data));
            throw httpError
        })

    }
    this.requestAccountVerification = function (email) {
        return $http.get('/auth/request_verification/' + email).then(function (res) {
            if (res.status == 200) {
                return res.data
            }
        }).catch(function (httpError) {
            $log.error('Error in Request Verification: ' + httpError.status + " : " + JSON.stringify(httpError.data));
            throw httpError
        })
    }
    this.logOut = function () {
        return $http.get('/auth/logout').then(function (res) {
            return res.result;
        });
    }
}]);


app.directive('confirmPassword', function ($q) {
    return {
        require: 'ngModel',
        link: function ($scope, $attr, $elem, ctrl) {
            ctrl.$validators.confirmPassword = function (value) {
                return ctrl.$$scope.vm.user.pwd == value
            };
        }
    }
});

app.directive('contenteditable', function() {
      return {
        require: 'ngModel',
        restrict: 'A',
        link: function(scope, elm, attr, ngModel) {

          function updateViewValue() {
            ngModel.$setViewValue(this.innerHTML);
          }
          //Binding it to keyup, lly bind it to any other events of interest
          //like change etc..
          elm.on('keyup', updateViewValue);

          scope.$on('$destroy', function() {
            elm.off('keyup', updateViewValue);
          });

          ngModel.$render = function(){
             elm.html(ngModel.$viewValue);
          }

        }
    }
});

[['ngEsc', 27], ['ngEnter', 13]].forEach(x => {
    app.directive(x[0], function () {
        return function (scope, element, attrs) {
            element.bind("keydown keypress", function (event) {
                if (event.which === x[1]) {
                    scope.$apply(function () {
                        scope.$eval(attrs[x[0]]);
                    });

                    event.preventDefault();
                }
            });
        };
    });
})


app.filter('titlecase', function () {
    return function (input) {
        return input.charAt(0).toUpperCase() + input.substr(1);
    }
});

class Car {
    constructor(x) {
        this.x = x
    }

    doSomething() {
        return 5
    }
}