`gravatar`是一个全球通用的个人头像服务，如果在这个网站上面申请注册了自己的头像/资料
以后，可以在任意其它网站上面获取你的这些信息.

server端通过以下步骤来实现：

1. 创建hash值：

首先需要创建用户的hash值，我们假定使用用户的email字段：

```python
import hashlib

user = get_user()

hash_value = hashlib.md5(user.email.lower()encode()).hexdigest()
```

2. 生成用户头像URL:

可以请求用户头像，在本地存储或者直接在HTML使用这个URL：

```python
import requests
from urllib.parse import urlencode

image_api = 'https://www.gravatar.com/avatar/{hash}'
size = 40   # 40px

image_url = image_api.format(hash=hash_value) + '?'\
        + urlencode({'s': str(size)})
image_response = requests.get(image_url)
```

3. 获取用户个人信息

API: https://www.gravatar.com/HASH

