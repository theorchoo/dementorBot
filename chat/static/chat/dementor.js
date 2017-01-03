/**
 * Created by ordagan on 06/12/2016.
 */

var dementor = angular.module('dementor', []);

/**
 * dashboard controller
 */
dementor.controller('MainController', ['$scope','$http','$q',
    function($scope,$http,$q) {

        // initiation
        $scope.bactive = false;

        $scope.showResponse = false;
        $scope.user_input = '';
        $scope.answer = '';
        $scope.last_user_input = "";
        $scope.conversation = [
            { "isBot": true, "text": "Hello, i'm DementorBot, tell me something about you..","lastof":true}
        ];
        $scope.last_res = { };
        $scope.evil_list = [];
        $scope.keywords = [];
        $scope.score = 0;
        $scope.path = [];
        $scope.sentences = [];
        $scope.sowed = [];

        $scope.saw_path = function () {
            $scope.sowed = [];
            for (var i=0; i<$scope.sentences.length; i++) {
                $scope.sowed.push($scope.path[1+i]);
                $scope.sowed.push($scope.sentences[i].text);
            }
            $scope.sowed.push($scope.path[$scope.path.length-2]);
            $scope.sowed.push($scope.evil_answer);
        };

        $scope.is_on_path = function () {
            for (var i in $scope.last_res.keywords) {
                if ($scope.path.indexOf($scope.last_res.keywords[i]) != -1) {
                    return true;
                }
            }
            for (var j in $scope.last_res.entities) {
                if ($scope.path.indexOf($scope.last_res.entities[j]) != -1) {
                    return true;
                }
            }
            for (var k in $scope.last_res.taxonomy) {
                t = $scope.last_res.taxonomy[j].substring($scope.last_res.taxonomy[j].indexOf('/'));
                if ($scope.path.indexOf(t) != -1) {
                    return true;
                }
            }
            return false;
        };

        $scope.ask = function () {
            if ($scope.user_input == '') {
                return
            }
            $scope.answer = '';

            var q = $scope.user_input;
            $scope.user_input = '';
            $scope.last_user_input = q;

            if (!$scope.conversation[$scope.conversation.length-1].isBot) {
                $scope.conversation[$scope.conversation.length-1].lastof = false;
            }
            $scope.conversation.push({"isBot":false, "text" : q, "lastof":true});

            $http.post('/api/watson', [q])
                .then (function (data) {
                    $scope.last_res = data.data;
                    console.log(data.data);
                    if ($scope.last_res.keywords.length == 0 &&
                        $scope.last_res.entities.length == 0 &&
                        $scope.last_res.taxonomy.length == 0) {
                            $scope.evil_list = "";
                            $scope.keywords = "";
                            $scope.score = "";
                            $scope.path = "";
                            $scope.sentences = "";
                            if ($scope.last_user_input.endsWith("?")) {
                                $scope.answer = $scope.evil_answer = "I'm not gonna even answer. tell me something else!";
                            } else {
                                $scope.answer = $scope.evil_answer = "You are boring. tell me something interesting...";
                            }
                            $scope.conversation.push({"isBot":true, "text" : $scope.answer, "lastof":true});
                            scroll();
                    } else {

                    // if ($scope.is_on_path()) {
                    //
                    // } else {
                    //
                    // }
                    $http.post('/api/find', data.data)
                        .then(function (data2) {
                            console.log(data2.data);
                            $scope.evil_list = data2.data.evil_list;
                            $scope.keywords = data2.data.keywords;
                            $scope.score = data2.data.score;
                            $scope.path = data2.data.path;
                            $scope.sentences = data2.data.sentences;
                            $scope.evil_answer = $scope.evil_list[$scope.evil_list.length - 2];
                            if ($scope.evil_list.length > 4 && $scope.score > 1.5) {
                                if ($scope.answer == $scope.sentences[0].text) {
                                    $scope.answer = $scope.sentences[1].text;
                                } else {
                                    $scope.answer = $scope.sentences[0].text;
                                }
                            } else {
                                $scope.answer = $scope.evil_answer;
                            }
                            $scope.saw_path();
                            $scope.conversation.push({"isBot":true, "text" : $scope.answer, "lastof":true});
                            scroll();
                        });
                    }
                });
            scroll();
        }
}]);

var scroll = function () {
    var objDiv = document.getElementById("context");
    objDiv.scrollTop = objDiv.scrollHeight + 500;
};