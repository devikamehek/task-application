from django.shortcuts import render,redirect
from django.views.generic import View,FormView,TemplateView,ListView,DetailView,UpdateView,CreateView
from todo.forms import RegistrationForm,LoginForm,TaskForm,TaskChangeForm,PasswordResetForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from todo.models import Task
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy


# static files in django
# static
# image/css/js/audio/video

# PSRV- render a form to html template- FormView

# decorator 
def sign_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            messages.error(request,"You must Login to Perform this Action!!!!!!!")
            return redirect("signin")
        return fn(request,*args,**kwargs)
    return wrapper




# Create your views here.
class SignUpView(CreateView):
    model=User
    form_class=RegistrationForm
    template_name="register.html"
    success_url=reverse_lazy("signin")

    def form_valid(self, form):
        messages.success(self.request,"Account created succesfully")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request,"Failed to create account")
        return super().form_invalid(form)

    # def get(self,request,*args,**kwargs):
    #     form=self.form_class
    #     return render(request,self.template_name,{"form":form})
    # def post(self,request,*args,**kwargs):
    #     form=self.form_class(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         messages.success(request,"Account created succesfully")
    #         return redirect("signin")
    #     messages.error(request,"Failed to create account")
    #     return render(request,self.template_name,{"form":form})
    





class SignInView(View):
    model=User
    template_name="login.html"
    form_class=LoginForm


    def get(self,request,*args,**kwargs):
        form=self.form_class
        return render(request,self.template_name,{"form":form})
    def post(self,request,*args,**kwargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            usr=authenticate(request,username=uname,password=pwd)
            if usr:
                login(request,usr)
                messages.success(request,"login succesfull")
                return redirect("index")
        messages.error(request,"invalid creadentials")
        return render(request,self.template_name,{"form":form})
    





# @sign_required is the original way of calling decorator but it is for function
# here it is class thus we call method_decorator in django
@method_decorator(sign_required,name="dispatch")
class IndexView(TemplateView):
    template_name="index.html"

    # def get(self,request,*args,**kwargs):
    #     return render(request,self.template_name)
    






@method_decorator(sign_required,name="dispatch")
class TaskCreateView(CreateView):
    model=Task
    form_class=TaskForm
    template_name="task-add.html"
    success_url=reverse_lazy("task-list")

    def form_valid(self, form):
        form.instance.user=self.request.user
        messages.success(self.request,"Task has been created succesfully")
        return super().form_valid(form)

    

    # def get(self,request,*args,**kwargs):
    #     form=self.form_class
    #     return render(request,self.template_name,{"form":form})
    
    # def post(self,request,*args,**kwargs):
    #     form=self.form_class(request.POST)
    #     if form.is_valid():
    #         form.instance.user=request.user
    #         form.save()
    #         messages.success(request,"Task added succesfully")
    #         return redirect("task-list")
    #     messages.error(request,"Failed to create task")
    #     return render(request,self.template_name,{"form":form})
    






@method_decorator(sign_required,name="dispatch")
class TaskListView(ListView):
    model=Task
    template_name="task-list.html"
    context_object_name="tasks"

# we have to change querryset
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by("-created_date")

    # def get(self,request,*args,**kwargs):
    #     qs=Task.objects.filter(user=request.user).order_by("-created_date")
    #     return render(request,self.template_name,{"tasks":qs})
    





@method_decorator(sign_required,name="dispatch")
class TaskDetailView(DetailView):
    model=Task
    template_name="task-detail.html"
    context_object_name="task"

    # def get(self,request,*args,**kwargs):
    #     id=kwargs.get("pk")
    #     qs=Task.objects.get(id=id)
    #     return render(request,self.template_name,{"task":qs})
    








@method_decorator(sign_required,name="dispatch")
class TaskEditView(UpdateView):
    model=Task
    form_class=TaskChangeForm
    template_name="task-edit.html"
    success_url=reverse_lazy("task-list")

    def form_valid(self, form):
        messages.success(self.request,"Task has been Edited Succesfully")
        return super().form_valid(form)
    
    

    # def get(self,request,*args,**kwargs):
    #     id=kwargs.get("pk")
    #     obj=Task.objects.get(id=id)
    #     form=self.form_class(instance=obj)
    #     return render(request,self.template_name,{"form":form})
    # def post(self,request,*args,**kwargs):
    #     id=kwargs.get("pk")
    #     obj=Task.objects.get(id=id)
    #     form=self.form_class(instance=obj,data=request.POST)
    #     if form.is_valid():
    #         form.save()
    #         messages.success(request,"Task changed succesfully")
    #         return redirect("task-list")
    #     messages.error(request,"Failed to update Task")
    #     return render(request,self.template_name,{"form":form})
    






@sign_required
def task_delete_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    obj=Task.objects.get(id=id)
    if obj.user == request.user:
        Task.objects.get(id=id).delete()
        messages.success(request,"Task Removed Succesfully")
        return redirect("task-list")
    else:
        messages.error(request,"You do not have Permission to Perform This Action")
        return redirect("signin")
        
 
    




def signin_out_view(request,*args,**kwargs):
    logout(request)
    return redirect("signin")
  



class PasswordResetView(FormView):
    model=User
    template_name="password-reset.html"
    form_class=PasswordResetForm


    def post(self,request,*args,**kwargs):
        form=self.form_class(request.POST)

        if form.is_valid():
            username=form.cleaned_data.get("username")
            email=form.cleaned_data.get("email")
            psw1=form.cleaned_data.get("password1")
            psw2=form.cleaned_data.get("password2")

            if psw1==psw2:
                try:
                    usr=User.objects.get(username=username,email=email)
                    usr.set_password(psw1)
                    usr.save()
                    messages.success(request,"Password Changed Succesfully")
                    return redirect("signin")
                except Exception as e:
                    messages.error(request,"Invalid Credentials")
                    return render(request,self.template_name,{"form":form})
            else:
                messages.error(request,"Password Mismatch")
                return render(request,self.template_name,{"form":form})

    # get,post method
    # get method- already defined in FormView class

# def get method is already defined in FormView class thats y we are not using get here
# if we are deriving from  View then we need to write get method


