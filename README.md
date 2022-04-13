# DJRoomba

This project contains one (at the moment) django app

## JOM (Joke of the Month)

This small project is a weekend project where a telegram bot (in polling mode) is integrated with django. The goal is to have a bot where every member of a group chat can forward a funny jokes, and the bot organizes a contest where each participant gets to vote. It is important first to declare the group members and Telegram IDs in the admin.

## How to use

Have a `.env` file with the required variables declared in the `docker-compose.yml` then:

```
docker-compose up
```

To change seasons you can run:

```
docker exec -ti djroomba python3 manage.py runscript vote_joke
```

## TODO

* Find a better solution to changing seasons
* Write some tests
* Add some views displaying top jokes of last seasons or something
* Improve support for a user being in multiple groups simultaneously