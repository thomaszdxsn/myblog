# myblog

下面是各个模块的介绍，它们都位于`app/`文件夹之下.

## BLOG -- 博客


## ADMIN -- 网站的后台

### PATCH

下面的改动使用常规的jQuery和Bootstrap4作为前端技术:

- 增加文章分类、文章的CRUD(2018-1-17)
- 使用封装的Qiniu SDK完成文章封面图片的上传，实现图片的缩略图(2018-1-18)
- 增加系统配置，可以更改session过期时间，缓存过期时间，缓存开启等功能(2018-1-18)

## API_V1 -- RESTFul API(版本1.0)

uri: `/api/v1/<resource>/(<id>)*`

- user
- category
- post
- tag
- image

### PATCH

- 资源新建/更新成功后会返回201状态码(2018-1-15)
- 资源删除成功后会返回204状态码(2018-1-15)
- 为资源的访问/操作加入验证登录的要求(需要持有session-id)，如果没有登录返回401状态码(2018-1-15)

## TODO

### Generic

- 加入用户注册和权限管理

### BLOG

- 记录在线人数，使用websocket来实现(每个页面都连接相同的ws接口).

### ADMIN

博客的后台功能:

- 使用Vue，将后台以前后端分离的方式重构
- 加入一键清空缓存的功能
- 加入图片管理，然后文章图片的选择可以根据这个资源来选择

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
