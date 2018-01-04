app.directive('taskEditor', function ($compile, $log) {
    return {
        templateUrl: 'static/partials/user.task.editor.html',
        restrict: 'AE',
        scope: {
            taskChangesObj: '=',
            save: '&',
            cancel: '&',
            tags: '&',
            cardClass: '@'
        },
        controller: ['$scope', function ($scope) {
            $scope.summernoteOption =
                {
                    airMode: true,
                    toolbar:
                        [
                            ['edit', ['undo', 'redo']],
                            ['headline', ['style']],
                            ['style', ['bold', 'italic', 'underline', 'superscript', 'subscript', 'strikethrough', 'clear']],
                            ['fontface', ['fontname']],
                            ['textsize', ['fontsize']],
                            ['fontclr', ['color']],
                            ['alignment', ['ul', 'ol', 'paragraph', 'lineheight']],
                            ['height', ['height']],
                            ['table', ['table']],
                            ['insert', ['link', 'picture', 'video', 'hr']],
                            ['view', ['fullscreen', 'codeview']],
                            ['help', ['help']]
                        ]
                }
            $scope.summernoteInit = function (obj) {
                console.log('Summernote is launched');
            }

        }],
        compile: function (element, attrs) {
            return function (scope, element) {
                var template = '<trix-editor angular-trix ng-model="taskChangesObj.content"\n' +
                    'class="k-form form-control w-100 mb-2 k-border-dark-yellow k-border-width-3 k-blue-focus"></textarea>';
                template = '<summernote on-init="summernoteInit(this)" config = "summernoteOption" ng-model="taskChangesObj.content" ></summernote>';
                var x = angular.element(template)
                var d = angular.element(element[0].querySelector('.editor-container'))
                d.prepend(x);
                $compile(x)(scope);
            }
        }
    }
}).directive('taskViewer', function ($compile, $log)  {
    return {
        templateUrl: 'static/partials/user.task.viewer.html',
        restrict: 'AE',
        controller: ['$scope', function ($scope) {
            $scope.summernoteOption =
                {
                    airMode: true,
                    placeholder: 'Add a note here...',
                    toolbar:
                        [
                            ['edit', ['undo', 'redo']],
                            ['headline', ['style']],
                            ['style', ['bold', 'italic', 'underline', 'superscript', 'subscript', 'strikethrough', 'clear']],
                            ['fontface', ['fontname']],
                            ['textsize', ['fontsize']],
                            ['fontclr', ['color']],
                            ['alignment', ['ul', 'ol', 'paragraph', 'lineheight']],
                            ['height', ['height']],
                            ['table', ['table']],
                            ['insert', ['link', 'picture', 'video', 'hr']],
                            ['view', ['fullscreen', 'codeview']],
                            ['help', ['help']]
                        ]
                }
            $scope.summernoteInit = function (obj) {
                console.log('Summernote is launched for a note');
            }

        }]
    }
}).directive('noteViewer', function () {
    return {
        templateUrl: 'static/partials/user.note.viewer.html',
        restrict: 'AE'
    }
});

