# Web Rest API Compouter Vision Competitions 

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