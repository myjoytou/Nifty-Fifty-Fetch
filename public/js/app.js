/**
 * Created by vivek on 3/12/16.
 */

angular.module('myApp', ['ui.router', 'flash'])

    .config(['$stateProvider', '$urlRouterProvider', function ($stateProvider, $urlRouterProvider) {
        $stateProvider
            .state('home', {
                url: '/home',
                templateUrl: 'static/templates/home.html',
                controller: 'homeCtrl'
            });
        $urlRouterProvider.otherwise('home');
    }])

    .constant('appSettings', appConfig)

    .service('apiService',['$http', '$q', 'appSettings', function ($http, $q, appSettings) {
        var apiService = {};
        var apiBase = appSettings.apiBase;
        var get = function (module) {
            var deferred = $q.defer();
            $http.get(apiBase + module, {}, { headers: { 'Content-Type': 'application/json' } }).success(function (response) {
                deferred.resolve(response.data);
            }).catch(function (data) {
                console.log('there was some error');
                deferred.reject(data.statusText);
            });
            return deferred.promise;
        };
        apiService.get = get;
        return apiService;
    }])

    .controller('homeCtrl', ['$scope', 'apiService', 'Flash', function ($scope, apiService, Flash) {
        $scope.niftyFifty = {};
        $scope.getData = function () {
            apiService.get('get_data').then(function (response) {
                $scope.niftyFifty.liveFeed = response;
                var id = Flash.create('success', 'Data refreshed successfully!', 3000);
            },
                function (error) {
                    Flash.create('error', 'Oh snap something bad happened!', 3000);
                }
            )
        };
        $scope.getData();
    }]);