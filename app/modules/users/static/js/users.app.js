app.config(function ($routeProvider, $locationProvider) {
    $routeProvider
        .when("/", {
            templateUrl: 'static/partials/user.tasks.html',
            controller: 'userCtrl'
        })
        .otherwise({
            redirectTo: '/'
        })

    $locationProvider.html5Mode({enable: true, requireBase: false});
})

var _tasks = null;
var _vm = null;


app.controller('userCtrl', ['$scope', '$cookies', '$log', 'taskService', 'taskNoteService', 'authService', 'moment', function ($scope, $cookies, $log, taskService, taskNoteService, authService, moment) {
    var vm = this;
    vm.alert = {
        color: 'red',
        message: 'You should do this',
        visible: false,
        caption: 'Oops!'
    }

    vm.scope = $scope;
    vm.selectedStage = 'todo';
    vm.draggingTask = null;
    vm.tasks = {
        backlog: {
            page: 0,
            tasks: [],
            selectedTasks: [],
            active: false,
            newTask: {
                content: '', tags: [], duration: 1, duration_type: 'day'
            },
            ui: {
                caption: "I like to Do",
                newTask: false,
                action: 'Do It',
                color: 'blue',
                fcolor: 'blue',
                selectingDate: false
            }
        }, todo: {
            page: 0,
            tasks: [],
            selectedTasks: [],
            active: true,
            newTask: {
                content: '', tags: [], duration: 1, duration_type: 'day'
            },
            ui: {
                caption: "I have to Do",
                newTask: false,
                action: 'Start',
                color: 'orange',
                fcolor: 'orange',
                selectingDate: false
            }
        }, progress: {
            page: 0,
            tasks: [],
            selectedTasks: [],
            active: false,
            ui: {
                caption: "I am Doing",
                newTask: false,
                action: 'Did It',
                color: 'yellow',
                fcolor: 'dark',
                selectingDate: false
            }
        }, done: {
            page: 0,
            tasks: [],
            selectedTasks: [],
            active: false,
            ui: {caption: "I Did It", newTask: false, action: '', color: 'green', fcolor: 'green', selectingDate: false}
        }
    };
    vm.stages = Object.keys(vm.tasks);
    vm.stages.forEach(s => {
        vm.tasks[s].newTask = {content: '', type: 'task', tags: [], duration: 1, duration_type: 'day'};
        vm.tasks[s].filter = {
            flag: 'all',
            sortedBy: '-time_updated',
            delayed: false,
            std: '',
            end: '',
            page: 0,
            query: '',
            stage: s
        };
        vm.tasks[s].count = {total: 0, delayed: 0};
        vm.tasks[s].ui.filterBox = false;
    });

    vm.newTask = function (stage) {
        vm.tasks[stage].newTask.owner = vm.user.email;
        if (typeof(vm.tasks[stage].newTask.tags[0]) !== "string") {
            vm.tasks[stage].newTask.tags = vm.tasks[stage].newTask.tags.map(t => {
                return t.text
            })
        }
        vm.tasks[stage].newTask.status = stage;

        taskService.updateHeadline(vm.tasks[stage].newTask);

        taskService.postTask(vm.tasks[stage].newTask).then(res => {
            vm.tasks[stage].tasks.unshift(new Task(res.task));
            vm.tasks[stage].ui.newTask = false

            vm.tasks[stage].newTask.tags.forEach(t => {
                if (vm.user.tags.indexOf(t) == -1)
                    vm.user.tags.shift(t)
            })

            vm.tasks[stage].newTask = {content: '', tags: [], duration: 1, duration_type: 'day'}

            vm.tasks[res.task.status].count.total++;
            if (res.task.time.delayed)
                vm.tasks[res.task.status].delayed.total++;
        })
    };

    vm.editTask = function (task) {
    }
    vm.cancelEditTask = function (task) {
    }
    vm.saveTask = function (task) {
    };

    vm.ignoreTasks = function (stage) {
        vm.tasks[stage].selectedTasks.forEach(t => {
            t.ignore(vm.ignoreTask)
        })
        vm.tasks[stage].selectedTasks = [];
    }
    vm.ignoreTask = function (task) {
        vm.tasks[task.status].count.total--;
        if (task.time.delayed)
            vm.tasks[task.status].delayed.total--;
    };

    vm.duplicateTask = function (index, task) {
        Object.assign(vm.tasks[task.status].newTask, task.duplicate());
        vm.newTask(task.status)
    };

    vm.moveTasks = function (stage, destStage = '') {
        vm.tasks[stage].selectedTasks.forEach(t => {
            t.move(destStage, vm.moveTask)
        })
        vm.tasks[stage].selectedTasks = [];
    }
    vm.moveTask = function (task) {
        var movedTask = Object.assign({}, task)
        movedTask = new Task(movedTask);
        vm.tasks[task.status].tasks.unshift(movedTask);
        movedTask.selected = false;
        movedTask.deleted = false;
        vm.tasks[task.status].count.total++;
        if (task.time.delayed)
            vm.tasks[task.status].delayed.total++;
    };

    vm.dragDrop = function (index, item, external, type, event, stage) {
        if (item.status == stage)
            return false
        item = vm.tasks[item.status].tasks.filter(t => t.task_id == item.task_id)[0];
        item.doIt(stage, vm.moveTask)
        return true;
    }

    vm.selectTask = function ($event, stage, task) {
        if ($event.ctrlKey || $event.metaKey) {
            task.selected = !task.selected;
            if (task.selected)
                vm.tasks[stage].selectedTasks.push(task);
            else
                vm.tasks[stage].selectedTasks.splice(vm.tasks[stage].selectedTasks.indexOf(task), 1);
        }
    }
    vm.unSelectTasks = function (stage) {
        vm.tasks[stage].tasks.forEach(t => t.selected = false);
        vm.tasks[stage].selectedTasks = [];
    }

    vm.logEvent = function (msg) {
        $log.log(msg);
    }
    vm.loadTags = function (query) {

        return vm.user.tags
    }

    vm.selectStage = function (status) {
        Object.keys(vm.tasks).forEach(function (t) {
            vm.tasks[t].active = false;
        });
        vm.tasks[status].active = true;
        vm.selectedStage = status;
    };

    vm.user = {}
    authService.me().then(res => {
        vm.user = res.me;
        if (!vm.user.account_verified) {
            vm.alert.caption = 'Oops! Your account is not verified!';
            vm.alert.message = "Please check your email to verify your account."
            vm.alert.visible = true;
        }
        vm.stages.forEach(stage => {
            taskService.loadTasks({
                email: vm.user.email,
                stage: stage,
                page: vm.tasks[stage].page,
            }).then(res => {
                vm.tasks[stage].count = res.count;
                res.tasks = res.tasks.map(t => {
                    let _task = t;
                    t.inEdit = false;
                    t.selected = false;
                    t.time.duration_type = t.time.duration_type || 'day';
                    t.stages = vm.stages;
                    let _taskObj = new Task(t);
                    return _taskObj;
                });

                vm.tasks[stage].tasks = res.tasks;
                vm.tasks[stage].delayed = res.tasks.filter(t => t.time.delayed).length;

                vm.tasks[stage].nextPage = res.nextPage;
                vm.tasks[stage].filter.email = vm.user.email;
                vm.tasks[stage].filter.stage = stage;
            })
        })
    });
    _vm = vm;
    _tasks = vm.tasks;
    vm.filterConfig = {
        query: ''
    }

    vm.toggleDateFilter = function (stage, force = false) {
        vm.tasks[stage].ui.selectingDate = !vm.tasks[stage].ui.selectingDate;
        if (force || vm.tasks[stage].ui.selectingDate === false) {
            vm.tasks[stage].ui.selectingDate = false;
            if (vm.tasks[stage].ui.selectingDate === false) {
                vm.tasks[stage].filter.std = '';
                vm.tasks[stage].filter.end = '';
            }
        }

    }
    vm.filter = function (stage) {
        $log.log(vm.tasks[stage].filter)
        taskService.loadTasks(vm.tasks[stage].filter).then(res => {
            vm.tasks[stage].tasks = res.tasks.map(t => {
                t.inEdit = false;
                t.selected = false;
                t.time.duration_type = t.time.duration_type || 'day';
                t.stages = vm.stages;
                let _taskObj = new Task(t);
                return _taskObj;
            });
            vm.tasks[stage].nextPage = res.nextPage;
            vm.tasks[stage].count = res.count;
        })
    }

    vm.clearFilter = function (stage) {
        vm.tasks[stage].filter = {
            flag: 'all',
            sortedBy: 'time',
            delayed: false,
            email: vm.user.email,
            std: '',
            end: '',
            page: 0,
            query: '',
            stage: stage,
        };
        vm.filter(stage)
    }

    vm.filterAll = function () {

        vm.stages.forEach(stage => {
            vm.tasks[stage].filter.query = vm.filterConfig.query;
            vm.filter(stage)
        })
    }

    vm.getLeftTime = function (task) {
        var dType = task.time.duration_type + 's';
        var d = moment.duration(task.time.left_hours, "hours")
        return moment.duration(d[dType](), dType).humanize()
    }

    vm.unixTimeStampToHumanize = function (time) {
        return moment.unix(time).format("ddd MMM-DD HH:mm:ss YYYY")
    }


    class Task {
        constructor(taskData) {
            Object.assign(this, taskData)
            this.headline = this.content.split(' ').splice(0, 3).join(' ')
            this.rest_content = this.content.split(' ').splice(3).join(' ')
            this.addingNote = false;
            this.notes = []
            this.newNote = ''
        }

        getHeadLine() {
            this.headline = this.content.split(' ').splice(0, 3).join(' ')
            this.rest_content = this.content.split(' ').splice(3).join(' ');
        }

        edit() {
            this.changes = {
                task_id: this.task_id,
                owner: this.owner,
                status: this.status,
                content: this.content,
                duration: this.time.duration,
                duration_type: this.time.duration_type || 'day',
                tags: this.tags,
                type: this.type
            }
            this.inEdit = true;

        }

        cancelEdit() {
            this.inEdit = false;
            delete this.changes;
        }

        save() {
            var _this = this;
            this.changes.tags = this.changes.tags.map(t => {
                return t.text
            });

            var _content = null;
            try {
                _content = $(this.changes.content)[0]
            }
            catch (e) {
                _content = $('<div>' + this.changes.content + '</div>')[0]
            }
            if (_content.childNodes[0].nodeType == 3) {
                this.headline = _content.childNodes[0].textContent.split(' ').splice(0, 3).join(' ');
                _content.childNodes[0].textContent = _content.childNodes[0].textContent.replace(this.headline, '');
                var strong = document.createElement("strong");
                strong.className = 'task-headline';
                strong.innerText = this.headline;
                _content.prepend(strong);
                this.changes.content = _content.innerHTML
            }

            taskService.putTask(this.owner, this.changes).then(res => {
                Object.assign(_this, res.task)
                _this.getHeadLine()
                _this.cancelEdit()
            })
        };

        ignore(callback) {
            var _this = this;
            taskService.deleteTask(this.owner, this).then(res => {
                _this.deleted = true;
                _this.selected = false;
                callback(_this);
            })
        }

        doIt(stage = '', callback = null) {
            var _this = this;
            stage = stage || (this.stages[this.stages.indexOf(this.status) + 1]);
            taskService.putTask(this.owner,
                {task_id: this.task_id, owner: this.owner, status: stage, type: this.type}).then(res => {
                _this.status = stage;
                _this.deleted = true;
                callback(_this);
            })
        }

        duplicate() {
            return {
                content: this.content,
                tags: this.tags,
                duration: this.time.duration,
                duration_type: this.time.duration_type
            }
        }

        openNotes() {
            if (!this.addingNote) {
                this.addingNote = true;
                if (!this.notesLoaded)
                    this.loadNote()

            }
            else{
                this.addingNote = false;
            }
        }

        loadNote(callback = null) {
            var _this = this;
            taskNoteService.loadNotes(this).then(res => {
                _this.notes = res.notes
                _this.notesLoaded = true
                if (callback)
                    callback(_this);
            })
        }

        addNote(note, callback = null) {
            var _this = this;
            taskNoteService.postNote(this, note).then(res => {
                _this.notes.unshift(res.note);
                if (callback)
                    callback(_this);
            })
        }

        removeNote(index, callback) {
            var _this = this;
            taskNoteService.deleteNote(this, index).then(res => {
                _this.notes = _this.notes.filter(n => n.index != index);
                if (callback)
                    callback(_this);
            })

        }

        editNote(index, note) {
            var _this = this;
            taskNoteService.editNote(index, note).then(res => {
                Object.assign(_this.notes.filter(n => n.index == index).note, res.note);
                if (callback)
                    callback(_this);
            })

        }

        note() {
            this.changes = {
                task_id: this.task_id,
                owner: this.owner,
                status: this.status,
                content: this.content,
                duration: this.time.duration,
                duration_type: this.time.duration_type || 'day',
                tags: this.tags,
                type: this.type
            }
            this.addingNote = true
        }


    }


}]);


app.service('taskNoteService', ['$http', '$log', 'localStorageService', function ($http, $log, localStorageService) {
    var self = this;
    this.loadNotes = function (task, page = 0) {
        return $http.get(`/api/v1/tasks/notes/${task.owner}/${task.task_id}`, {
            params: {page: page},
            headers: {
                'Authorization': 'token ' + localStorageService.get('token').token
            }
        }).then(function (res) {
            return res.data;
        }).catch(function (httpError) {
            $log.error('Error in Load Notes: ' + httpError.status + " : " + JSON.stringify(httpError.data));
            throw httpError
        })
    }
    this.postNote = function (task, note) {
        return $http.post(`/api/v1/tasks/notes/${task.owner}/${task.task_id}`, {content:note}, {
            headers: {
                'Authorization': 'token ' + localStorageService.get('token').token
            }
        }).then(function (res) {
            return res.data;
        }).catch(function (httpError) {
            $log.error('Error in Post Note: ' + httpError.status + " : " + JSON.stringify(httpError.data));
            throw httpError
        })
    }
    this.putNote = function (task, index) {
    }
    this.deleteNote = function (task, index) {
        return $http.delete(`/api/v1/tasks/notes/${task.owner}/${task.task_id}/${index}`, {
            headers: {
                'Authorization': 'token ' + localStorageService.get('token').token
            }
        }).then(function (res) {
            return res.data;
        }).catch(function (httpError) {
            $log.error('Error in Delete Task: ' + httpError.status + " : " + JSON.stringify(httpError.data));
            throw httpError
        })
    }

}]);


app.service('taskService', ['$http', '$log', 'localStorageService', function ($http, $log, localStorageService) {
    var self = this;
    //this.loadTasks = function (email, status = '', page = 0, flag = '', std = '', end = '') {
    this.loadTasks = function (filter) {
        //return $http.get(`/api/v1/tasks/${filter.email}?stage=${filter.stage}&page=${filter.page || 0}&flag=${filter.flag || 'all'}&std=${filter.std || ''}&end=${filter.end || ''}&query=${encodeURIComponent(filter.query || '')}`, {
        var _filter = Object.assign({}, filter)
        //_filter.query = encodeURIComponent(_filter.query || '');
        return $http.get(`/api/v1/tasks/${filter.email}`, {
            params: _filter,
            headers: {
                'Authorization': 'token ' + localStorageService.get('token').token
            }
        }).then(function (res) {
            return res.data;
        }).catch(function (httpError) {
            $log.error('Error in Load Tasks: ' + httpError.status + " : " + JSON.stringify(httpError.data));
            throw httpError
        })
    }
    this.postTask = function (newTask) {
        return $http.post(`/api/v1/tasks/${newTask.owner}`, newTask, {
            headers: {
                'Authorization': 'token ' + localStorageService.get('token').token
            }
        }).then(function (res) {
            return res.data;
        }).catch(function (httpError) {
            $log.error('Error in Post Task: ' + httpError.status + " : " + JSON.stringify(httpError.data));
            throw httpError
        })
    }
    this.putTask = function (owner, newTask) {
        return $http.put(`/api/v1/tasks/${newTask.owner}/${newTask.task_id}`, newTask, {
            headers: {
                'Authorization': 'token ' + localStorageService.get('token').token
            }
        }).then(function (res) {
            return res.data;
        }).catch(function (httpError) {
            $log.error('Error in Put Task: ' + httpError.status + " : " + JSON.stringify(httpError.data));
            throw httpError
        })
    }
    this.deleteTask = function (owner, newTask) {
        return $http.delete(`/api/v1/tasks/${newTask.owner}/${newTask.task_id}`, {
            headers: {
                'Authorization': 'token ' + localStorageService.get('token').token
            }
        }).then(function (res) {
            return res.data;
        }).catch(function (httpError) {
            $log.error('Error in Delete Task: ' + httpError.status + " : " + JSON.stringify(httpError.data));
            throw httpError
        })
    }
    this.updateHeadline = function (task) {
        var _content = null;
        try {
            _content = $(task.content)[0]
        }
        catch (e) {
            _content = $('<div>' + task.content + '</div>')[0]
        }
        if (_content.childNodes[0].nodeType == 3) {
            this.headline = _content.childNodes[0].textContent.split(' ').splice(0, 3).join(' ');
            _content.childNodes[0].textContent = _content.childNodes[0].textContent.replace(this.headline, '');
            var strong = document.createElement("strong");
            strong.className = 'task-headline';
            strong.innerText = this.headline;
            _content.prepend(strong);
            task.content = _content.innerHTML
        }
    }

}]);
//aa


