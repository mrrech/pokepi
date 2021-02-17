# Pokepi

REST API to expose a Shakesperean description for any Pokemon, given its name.

```
GET /pokemon/<name> HTTP/1.1
...
Content-Type: application/json

HTTP/1.1 200 OK
...
Content-Type: application/json

{
  "name": "<name>",
  "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
  do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
  minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
  commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit
  esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
  non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
}
```
