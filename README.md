# DJRoomba

This project contains several django apps, mostly telegram bots. The goal is to aggregate several bots, scripts and ideas in the same application having a shared database, user management, infrastructure, etc. This was developed with my very specific needs in mind and is not intended to be any kind of product, but if some part of it is useful to you you are welcome to use it.

## How to use

Have a `.env` file with the required variables declared in the `docker-compose.yml` then:

```
docker-compose up
```

To perform the migrations on the production database:

```
docker-compose run django python manage.py migrate
```

## JOM (Joke of the Month)

This small project consists of a telegram bot (in polling mode) integrated with django. The goal is to have a bot where every member of a group chat can forward a funny jokes, and the bot organizes a contest where each participant gets to vote. It is important first to declare the group members and Telegram IDs in the admin.

To change seasons you can run:

```
docker exec -ti djroomba python3 manage.py runscript vote_joke
```

This line can be added to cron in order to automatically change seasons at a specified time

```
# this runs the first day of each month
0 0 1 * * (/usr/bin/docker exec djroomba python3 manage.py runscript vote_joke) >> /home/cronlog.txt 2>&1
```

## Matrix

The matrix app controls a [matrix of 32x32 addressable leds](https://github.com/jserrats/matrix). The application is composed of a telegram bot which receives images, and a web interface used to manage them.

## TODO

* Find a better solution to changing seasons
* Write some tests
* Add some views displaying top jokes of last seasons or something
* Improve support for a user being in multiple groups simultaneously