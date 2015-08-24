## Falcon Framework Gotchas

### Generate XML response in browser
Need to set error serializer to always return json representation because if the request header from
browser is "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", api returns xml
 response body.

```
def json_error_serializer(req, exception):
    """Override default serialize to always return json representation

       Args:
            req: The request object.

        Returns:
            A ``tuple`` of the form (*media_type*, *representation*), or (``None``, ``None``)
            if the client does not support any of the available media types.
    """
    return 'application/json', exception.to_json()


app.set_error_serializer(json_error_serializer)
```

### No response body when HTTPError is raised
If description is missing in instances of HTTPError or child class of HTTPError, has_representation 
 attribute is set to False and no response body is created as a result.
 
```
    # Won't generate response body
    if user is None:
        raise falcon.HTTPNotFound(title="User Not Found")
           
    # Will generate response body
    if user is None:
        raise falcon.HTTPNotFound(title="User Not Found",
                                  description='Fail to lookup user')
                                  
                                  
                                  
                                  
class OptionalRepresentation(object):
    """Mixin for ``HTTPError`` child classes that may have a representation.

    This class can be mixed in when inheriting from ``HTTPError`` in order
    to override the `has_representation` property, such that it will
    return ``False`` when the error instance has no description
    (i.e., the `description` kwarg was not set).

    You can use this mixin when defining errors that do not include
    a body in the HTTP response by default, serializing details only when
    the web developer provides a description of the error.

    Note:
        This mixin class must appear before ``HTTPError`` in the base class
        list when defining the child; otherwise, it will not override the
        `has_representation` property as expected.

    """
    @property
    def has_representation(self):
        return super(OptionalRepresentation, self).description is not None


class HTTPNotFound(OptionalRepresentation, HTTPError):
    """404 Not Found.
    ...

class HTTPMethodNotAllowed(OptionalRepresentation, HTTPError):
    """405 Method Not Allowed.
    ...
```