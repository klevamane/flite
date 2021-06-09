
# Flite  
  
[Flite](https://github.com/cowrywise/flite) is a wallet app built with [Django](https://www.djangoproject.com/) and [Django REST framework](https://www.django-rest-framework.org/). 
  
## Prerequisites! 🤔  
- Docker, Docker compose
  
## Running this application 
It has a minimal docker set up and you can run the project by    
1. Clone the repository 
2. change directory into the flite directory 
3. docker-compose up

## Running the tests
- docker-compose run django python manage.py test

## Running migrations
Running the application for the first time will also run the migrations in tandem.
To run migrations subsequently

- docker-compose run django python manage.py migrate

## Accessing the database with a DB client
You can access the postgres db (in docker) with your db client by using these credentials

- postgres (username, password)
- flite (database)
- localhost (host)
- 5432 (port)
> **Note**: make sure your system postgres is not running in the backround while trying to connect to the postgres db in docker

## Assumptions!   
- A registered user can only have one balance account
- P2P transfer status changes from `processing` but ultimately becomes `complete` when the transaction is successful
- I created a model for each transaction `Deposit` and `Withdraw` in order to follow the convention of transactions already in the code base
- The codebase has no code formatter currently, i assume that will be done in future, with that being said i made sure the newly added code where formatted as and follows pep8 style guide
