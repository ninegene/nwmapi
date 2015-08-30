# REST API

## Http Status Codes 

In general:
* 2xx range indicate success
* 4xx range indicate client error
* 5xx range indicate app server error

### Summary
```
200 - OK - Everything worked as expected.
201 - Created - A new resource is created successful.
302 - Found - A common redirect response; you can GET the representation at the URI in the location response header. 
304 - Not Modified - Your client’s cached version of the representation is still up to date.
400 - Bad Request - Bad input parameter. Often missing a required parameter.
401 - Unauthorized - Bad or missing authentication credentials.
403 - Forbidden - The supplied authentication credential are not sufficient to access the resource.
404 - Not Found - The requested resource doesn't exist.
405 - Request method not expected (generally should be GET or POST).
409 - Conflict - Another resource already exists or conflict with the resource you are creating or updating
415 - Unsupported Media Type - The request Content-Type header is not application/json.
429 - Too Many Request - Too many simultaneous request.
500 - Server Error - Error creating or updating the resource. Please try again
503 - Service Unavailable - Service temporarily unable. Please wait for a bit and try again.
```
Based on:
* http://docs.stormpath.com/rest/product-guide/#retrieving-resources
* http://docs.stormpath.com/rest/product-guide/#errors
* https://stripe.com/docs/api#errors
* https://www.dropbox.com/developers/core/docs#error-handling

## Learn REST API
* https://parse.com/docs/rest/guide/
* http://www.restapitutorial.com/httpstatuscodes.html

## Auth Example Implementations
* https://developer.atlassian.com/docs/atlassian-platform-common-components/rest-api-development/rest-and-os_authtype
* https://developer.gooddata.com/api#/introduction/use-cases

## Good RESP APIs 
* https://stripe.com/docs/api
* http://docs.stormpath.com/rest/product-guide/#rest-api-general-concepts

