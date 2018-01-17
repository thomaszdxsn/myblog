在同一个坑上面掉了两次。。。好记性不如烂笔头，将它记下来防止第三次掉坑。

这个坑就是`sqlalchemy.ext.baked.bakery`，也怪我自己学艺不精，
它的文档已经明确告知**这个ext(扩展)用于缓存编译后的SQL字符串**，也就是说，
它生成的对象并不是`sqlalchemy.orm.query.Query`，
而是`sqlalchemy.ext.baked.Result`，你不能继续在对它进行query操作，
比如不能在这个对象的基础上再进行分页(需要`offset()`，`limit()`*[]:
我在这里被坑了两次，每次半小时...

其实也可以实现对`sqlalchemy.ext.baked.Result`再次进行query操作，
但是这需要把字符串重新解析为对象，从实现的角度来看未免得不偿失。

总结：**只在确定SQL语句是最终需要的情况下，使用`sqlalchemy.ext.baked.bakery`**