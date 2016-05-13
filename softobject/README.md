# SoftObject

A class extending `SoftObject` will behave simliar to Javascript objects, returning `None` for attributes that do not
exist instead of throwing an `AttributeError`.

## Example

A normal object
```python
class C(object):
  pass

c = C()

c.bla
AttributeError: 'C' object has no attribute 'bla'
```

A soft object
```python
import softobject

class C(softobject.SoftObject):
  pass

c = C()

c.bla
None
```


