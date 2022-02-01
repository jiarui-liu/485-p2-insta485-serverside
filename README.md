# 485-p2-insta485-serverside

### Tasks:
- [x] /
- [x] /users/<user_url_slug>/
- [x] /users/<user_url_slug>/followers/
- [x] /users/<user_url_slug>/following/
- [x] /posts/<postid_url_slug>/
- [x] /explore/
- [x] /accounts/login/
- [x] /accounts/logout/
- [x] /accounts/create/
- [x] /accounts/delete/
- [x] /accounts/edit/
- [x] /accounts/password/
- [ ] Register for autograder
- [ ] deploy to AWS Server

### problems solution update:
- Comment is now ordered by commentid (update: piazza [@1172](https://piazza.com/class/kwzgyay4mpcwl?cid=1172) says it doesn't matter)
### Problems or Bugs:
#### Flask
- `run pytest -v` to see current bugs
  - `/accounts/create/` test failed: `assert 302 == 200`
  - pydocstyle test failed
  - pylint test failed