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
* http://restful-api-design.readthedocs.org/en/latest/methods.html
* https://parse.com/docs/rest/guide/
* http://www.restapitutorial.com/httpstatuscodes.html

## Auth Example Implementations
* https://developer.atlassian.com/docs/atlassian-platform-common-components/rest-api-development/rest-and-os_authtype
* https://developer.gooddata.com/api#/introduction/use-cases

## Good RESP APIs 
* https://stripe.com/docs/api
* http://docs.stormpath.com/rest/product-guide/#rest-api-general-concepts

## REST Authentication and Authorization and OAuth
* https://stormpath.com/blog/token-auth-spa/
* http://jeremymarc.github.io/2014/08/14/oauth2-with-angular-the-right-way/
* https://code.exacttarget.com/apis-sdks/rest-api/using-the-api-key-to-authenticate-api-calls.html
* http://security.stackexchange.com/questions/63314/authenticating-rest-api-using-access-token
* https://docs.shopify.com/api/authentication/oauth
* https://developer.paypal.com/docs/integration/direct/make-your-first-call/
* https://developer.salesforce.com/page/Digging_Deeper_into_OAuth_2.0_on_Force.com


## Refresh Token vs Non-expiring Access Token
* http://jeremymarc.github.io/2014/08/14/oauth2-with-angular-the-right-way/
* http://stackoverflow.com/questions/11357176/do-oauth2-access-tokens-for-a-mobile-app-have-to-expire
* http://stackoverflow.com/questions/13851157/oauth2-and-google-api-access-token-expiration-time

## General Authentication
* http://stackoverflow.com/questions/549/the-definitive-guide-to-form-based-website-authentication

## OAuth Json Web Token
* https://developer.atlassian.com/static/connect/docs/latest/concepts/understanding-jwt.html
* https://www.npmjs.com/package/learn-json-web-tokens
* https://auth0.com/blog/2014/01/27/ten-things-you-should-know-about-tokens-and-cookies/
* https://auth0.com/blog/2014/01/15/auth-with-socket-io/
* http://www.sitepoint.com/using-json-web-tokens-node-js/
* http://www.seedbox.com/en/blog/2015/06/05/oauth-2-vs-json-web-tokens-comment-securiser-un-api/
* https://github.com/jpadilla/pyjwt
* https://github.com/auth0/node-jsonwebtoken