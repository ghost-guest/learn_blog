from django.shortcuts import render, redirect
# 导入 HttpResponse 模块
from django.http import HttpResponse
from .models import ArticlePost
from comment.models import Comment
from .form import ArticlePostForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
# 引入验证登录的装饰器
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import markdown
# 视图函数
def article_list(request):
    # 取出所有的文章
    # 根据GET请求中查询条件
    # 返回不同排序的对象数组
    search = request.GET.get('search')
    order = request.GET.get('order')
    if search:
        if order == "total_views":
            articles = ArticlePost.objects.filter(
                Q(title__icontains=search)|
                Q(body__icontains=search)
            ).order_by("-total_views")
        else:
            articles = ArticlePost.objects.filter(
                Q(title__icontains=search)|
                Q(body__icontains=search)
            )
    else:
        search = ''
        if order == 'total_views':
            articles = ArticlePost.objects.all().order_by("-total_views")
        else:
            articles = ArticlePost.objects.all()
    #print("文章的内容所有: " ,articles)
    # 每页显示一片文章
    paginator = Paginator(articles, 3)
    # 获取URL的页码
    page = request.GET.get('page')
    # 将导航对应的页码返回给articles
    articles = paginator.get_page(page)
    # 需要传给模板的对象
    context = {'articles': articles, 'order':order, 'search':search}
    # render 载入模板并返回context对象
    return render(request, 'article/list.html', context)

# 文章详情
def article_detail(request, id):
    # 取出相应的文章
    article = ArticlePost.objects.get(id=id)
    # 流量+1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    # print("文章的内容：", article)
    # 将Markdown语法渲染成HTML格式
    md = markdown.Markdown(
        extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)
    # 取出文章评论
    comments = Comment.objects.filter(article=id)
    # 将文章内容传递给模板
    content = {'article': article, 'toc': md.toc, 'comments':comments}
    # 载入模板，并返回content对象
    return render(request, 'article/detail.html', content)

# 写文章的视图
def create_article(request):
    # 判读用户是否提交数据
    if request.method == 'POST':
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据单不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中ID=1的用户为作者
            # 如果进行删除数据表的操作，可能找不到ID=1的用户
            # 此时需要重新创建用户，并传入此用户的ID
            new_article.author = User.objects.get(id=request.user.id)
            # 将文章保存到数据库中
            new_article.save()
            # 返回文章的列表
            return redirect('article:article_list')

        # 如果数据不合法返回错误信息
        return HttpResponse("表单内容有误，请重新填写。")
        # 如果用户请求获取数据
    else:
        # 创建表单实例
        article_form = ArticlePostForm()
        # 赋值上下文
        content = {'article_post_form':article_form}
        # 返回模板
        return render(request, 'article/create.html', content)

# 删除文章
def article_delete(request, id):
    # 根据ID获取需要删除的文章
    article = ArticlePost.objects.get(id=id)
    # 调用delete方法删除
    article.delete()
    # 返回文章的列表
    return redirect('article:article_list')


# 修改文章
# 提醒用户登录
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    # 获取需要修改的文章
    article = ArticlePost.objects.get(id=id)
    #判断用户是不是post提交表单
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    if request.method == 'POST':
        # 将提交的表单赋值到实例对象中 
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足数据
        # print("post请求的内容：", request.POST)
        if article_post_form.is_valid():
            # 保存新写入的数据
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.save()
            # 返回到修改的文章中
            return redirect('article:article_detail', id=id)
        else:
            return HttpResponse('传入的数据内容不合法！')
    else:
        # 创建表单类实体
        article_post_form = ArticlePostForm()
        # 赋值上下文，将文章对象article也传入，以便提取旧的内容
        content = {'article':article, 'article_post_form':article_post_form}
        # 将相应返回到模板中
        return render(request, 'article/update.html', content)
