# 485-p2-insta485-serverside

### Tasks:
- [x] /
- [x] /users/<user_url_slug>/
- [x] /users/<user_url_slug>/followers/
- [x] /users/<user_url_slug>/following/
- [ ] /posts/<postid_url_slug>/
- [ ] /explore/
- [x] /accounts/login/
- [x] /accounts/logout/
- [ ] /accounts/create/
- [ ] /accounts/delete/
- [ ] /accounts/edit/
- [ ] /accounts/password/
- [ ] Register for autograder
- [ ] deploy to AWS Server

### Problems or Bugs:
#### SQL
- `NOT NULL`: 
#### Flask
- post file upload to where? 
- time of post seems to have a problem, whether database problem or website problem remains unknown.
- password: do we need to use hash?
- Comment ordered by created or commentid? 
- "If someone tries to access a `user_url_slug` that does not exist in the database, then `abort(404)`": Not sure if the functionality has been fully realized
- specific form of url in `<form action="<FIXME_FOLLOWING_URL_HERE>?target=<FIXME_CURRENT_PAGE_URL_HERE>" method="post" enctype="multipart/form-data">`, especially the one following `?target=`.
- `flask.abort(403)` https://eecs485staff.github.io/p2-insta485-serverside/#access-control
- should we add `abort(404)` for Index `GET /`?