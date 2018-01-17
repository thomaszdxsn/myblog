激活缓存功能后，有时会出现缓存一个空字符串`""`的情况，
经过我多方查证，发现了是因为304状态码的原因.


Tornado的304状态是通过3个方法来处理的:

- `compute_etag`:

    每次响应时都会根据内容的hash计算一个`etag`值.
    
- `set_etag_header`

    使用这个方法将`etag`值加入到`response headers`中.
    
    在请求结束时自动调用这个方法.
    
- `check_etag_header`

    检查请求携带的`etag`是否和本次内容的`etag`值一样.
    
    如果一样，则返回True。并且应该返回304状态码，提示内容没有修改.
    

缓存问题就清晰了:

```python
# RequestHandler的代码中...
if self._status_code != 304:
    # 进行缓存...
```