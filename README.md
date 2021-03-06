# myblog


## 模版版本

本博客开发了若干套模版版本，大多是借鉴自其它博客：

- blog_von

    ![sample-1](http://p2gg7csfl.bkt.clouddn.com/ed52361a-2b12-4509-b832-49f013b6d6cc?imageMogr2/thumbnail/600x400)

    ![sample-2](http://p2gg7csfl.bkt.clouddn.com/d06c3ca8-d960-4307-bfcc-de6a109554ff?imageMogr2/thumbnail/600x400)

    ![sample-3](http://p2gg7csfl.bkt.clouddn.com/ed52361a-2b12-4509-b832-49f013b6d6cc?imageMogr2/thumbnail/600x400)

    这是一个极简风格的博客，借鉴自[von](http://paullaros.nl/von/)。原来的模版需要收费。


- blog_startbootstrap

    ![sample-1](http://p2gg7csfl.bkt.clouddn.com/5fb7cec6-5431-4e1e-bd82-d764e370a4eb?imageMogr2/thumbnail/600x400)

    简单的bootstrap4主题，借鉴自[startbootstrap](https://startbootstrap.com/template-overviews/blog-post/)，
    是该网站免费分享的一个bootstrap blog模版。




## 开发日志

- 2018-1-20

    - blog: 文章中的代码块显示优化，使用`Google:code-prettify`库，
    并且加入系统配置，可以切换代码块的皮肤
    - blog: 文章中的嵌套代码块有显示问题，TODO

- 2018-1-19

    - blog: 加入文章详情的显示
    - blog: 文章内容的markdown转换
    - blog: 加入文章评论的显示(内容，头像)，审核，和评论频率的限制

- 2018-1-18

    - admin: 增加系统配置，可以更改session过期时间，缓存过期时间，缓存开启等功能
    - admin: 使用封装的Qiniu SDK完成文章封面图片的上传，实现图片的缩略图
    - blog: 加入文章列表的显示

- 2018-1-17

    - admin: 增加文章分类、文章的CRUD

- 2018-1-15

    - api_v1: 资源新建/更新成功后会返回201状态码
    - api_v1: 资源删除成功后会返回204状态码
    - api_v1: 为资源的访问/操作加入验证登录的要求(需要持有session-id)，如果没有登录返回401状态码

- 2018-1-14

    - 完成项目的基础文件结构设计，数据库模型设计
    - api_v1: 增加分类、文章、标签、用户的CRUD API


## TODO

### Generic

- 加入用户注册和权限管理

### BLOG

- 记录在线人数，使用websocket来实现(每个页面都连接相同的ws接口).
- 可以相互之间评论

### ADMIN

博客的后台功能:

- 使用Vue，将后台以前后端分离的方式重构
- 加入一键清空缓存的功能
- 加入图片管理，然后文章图片的选择可以根据这个资源来选择
- 可以管理评论，评论黑名单

### STATS

统计模块负责统计博客文章的点击、点赞等数据:

- 使用REDIS统计博客前端文章的统计数据
- 使用REDIS定时统计服务器的系统数据(硬盘使用，内存使用，缓存占用...)
- 定时将REDIS的数据持久化到MySQL中
- 定时对REDIS数据进行清理

### API

RESTful API:

- `test_api`的测试用例显得有些乱，应该将它们分离，为相关联的用例单独建一个
`TestCase`以供存放
- 为资源的访问/操作加入权限控制，如果没有权限则返回403状态码

### SEO

网站的SEO:

- 实现Sitemap
- 实现RSS
