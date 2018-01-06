app.config(function($routeProvider,$locationProvider){$routeProvider.when("/",{templateUrl:'static/partials/auth.sign.html',controller:'authCtrl'}).when("/reg",{templateUrl:'static/partials/auth.reg.html',controller:'authCtrl'}).otherwise({redirectTo:'/'})
$locationProvider.html5Mode({enable:true,requireBase:false});})
app.controller('authCtrl',['$scope','$cookies','$log','localStorageService','authService',function($scope,$cookies,$log,localStorageService,authService){var vm=this;vm.scope=$scope;vm.user={email:'',pwd:'',remember:false}
vm.signed=0;vm.signIn=function(byPassValidation){if(byPassValidation||vm.frmSign.$valid){authService.login(vm.user).then(function(isSigned){if(isSigned){vm.signed=1;authService.getToken().then(function(token){localStorageService.set('token',token)
$log.info('token received: '+token.token)
$log.info('signed in')
document.location.href="/users"})}}).catch(function(er){if(er.status===400){vm.signed=er.data.code;vm.signErrorMsg=er.data.msg;$log.warn(er.data.msg);}})
$cookies.put('user_auth',JSON.stringify({email:vm.user.email,remember:vm.user.remember}))}}
vm.signUp=function(){if(vm.frmSignUp.$valid){vm.user.age=35;vm.user.gender='female';vm.user.first_name='no name';vm.user.last_name='no name';authService.register(vm.user).then(res=>{if(res.result){authService.requestAccountVerification(vm.user.email).then(res=>{})
vm.signIn(true);$log.info('registered')}}).catch(er=>{if(er.status===400){vm.signed=-1;vm.signErrorMsg=er.data.msg;$log.warn(er.data.msg);}})
$cookies.put('user_auth',JSON.stringify({email:vm.user.email,remember:vm.user.remember}))}}
if($cookies.get('user_auth')){var _user=JSON.parse($cookies.get('user_auth'));vm.user.email=_user.email;vm.user.remember=_user.remember;}}]);