# Web Rest API Computer Vision Competitions 

[Live Application here](https://vision-competitions.herokuapp.com/)

```bash
heroku login
heroku git:remote -a vision-competitions
heroku buildpacks:set https://github.com/heroku/heroku-buildpack-apt.git
heroku buildpacks:add --index 2 heroku/python
git add .
git commit -am "make it better"
git push heroku master
```

```bash
heroku logs --tail
```

# ToDo
- [x] Working Signup/Login
- [x] Styles to "My submissions" at each table
- [x] Choose DB -> Show corresponding scores 
- [x] Upload and evaluate test files
   + [x] MNIST
   + [x] CIFAR10
- [x] Submission button only logged users
- [x] Tutorial: How to do a submission
- [x] Email Login (verify that the mail is correct in the signup)
- [x] Auto login after signup
