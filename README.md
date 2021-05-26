# The Bank App

This is a app written in python using Django framework. It immitates a secure bank system.

## Quick start

Running the application requires locally installed Docker (https://docs.docker.com/installation/).

Clone this repository:

    $ mkdir my-clone
    $ cd my-clone/
    $ git clone https://gitlab.com/ewa.utr/quotes-app.git

Run the project in your python virtual enviroment:

    $ python manage.py runserver

To enable the functionalities such as notifications and two facttor authentication, run a Redis image using [Docker](https://docs.docker.com/installation/):

    $ docker run -p 6379:6379 -d redis:5

Lastly, enable sending emails run the rqworker server with thiis command:

    $ python manage.py rqworker

## Authentication

The Bank App has a two factor authentication feature enabled with [Django Two-Factor Authentication](https://django-two-factor-auth.readthedocs.io/en/stable/). The app requires a use of a tool such as Google Authenticator to log in.

## Employee's View

Once a user is categorized as 'staff', they are granted access to an employee view. From there, it is possible to perform management actions, such as creating and deleting customers, editing their ranks and generating new bank accounts for the costumers.

## Customer's View

If a user does not belong to a staff, they are directed to a customer's dashboard. From there, it is possible to view all accounts that belong to the logged in customer and their activity, manage loans, make transfers to local for foregn banks.

## External ransfers

In order to test a functionality of sending transfers to another banks, make sure to simulate anothe bank's instance by running a copy of the project on a `0.0.0.0:8003` server
