from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .form import UserLoginForm, UserRegisterForm, ProfileForm
from django.contrib.auth.models import User
# 引入验证登录的装饰器
from django.contrib.auth.decorators import login_required
from .models import Profile
# Create your views here.
def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            # .cleaned_data 清理出合法的数据
            data = user_login_form.cleaned_data
            # 检查账号和密码是否正确匹配数据库中的某个用户
            # 如果有，则返回这个用户
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                # 将登录用户保存到session中，实现登录
                login(request, user)
                return redirect("article:article_list")
            else:
                return HttpResponse("账号或密码错误，请重新输入！！！")
        else:
            return HttpResponse("账号或密码不合法，请重新输入！！！")
    elif request.method == 'GET':
        user_login = UserLoginForm()
        context = {'form': user_login}
        return render(request, 'userprofile/login.html', context)
    else:
        return HttpResponse("请使用GET或POST请求！")

# 用户退出
def user_logout(request):
    logout(request)
    return redirect("article:article_list")

# 用户注册
def user_register(request):
    if request.method == "POST":
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            # 设置密码
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            # 保存数据后，立即登录并返回博客的首页
            login(request, new_user)
            return redirect('article:article_list')
        else:
            return HttpResponse("注册表单有误，请重新输入！！！")
    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        content = {'form':user_register_form}
        return render(request, 'userprofile/register.html', content)
    else:
        return HttpResponse("请使用GET或POST请求数据!")


@login_required(login_url='/userprofile/login/')
def user_delete(request, id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        # 验证登录用户和待删除用户是否相同
        if request.user == user:
            # 退出登录，删除数据并返回首页
            logout(request)
            user.delete()
            return redirect("article:article_list")
        else:
            return HttpResponse("你没有删除的权限！")
    else:
        return HttpResponse("仅接受POST请求！")


# 编辑用户信息
@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)
    profile = Profile.objects.get(user_id=id)
    if request.method == 'POST':
        # 验证修改数据者是否为本人用户
        if request.user != user:
            return HttpResponse("你没有权限修改此用户信息。")
        # 上传的文件保存在 request.FILES 中，通过参数传递给表单类
        profile_form = ProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            # 取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            # 如果 request.FILES 存在文件，则保存
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]
            profile.save()
            # 带参数的 redirect()
            return redirect("userprofile:edit", id=id)
        else:
            return HttpResponse("注册表单输入有误。请重新输入~")
    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = { 'profile_form': profile_form, 'profile': profile, 'user': user }
        return render(request, 'userprofile/edit.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")