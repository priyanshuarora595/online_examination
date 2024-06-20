# Online Examination

## Pre-requiste

You need `Python 3.11.5` to run this project.

## How to use

- **Instructions**

  - Install the Requirements:
    `pip install -r requirements.txt`
  - Then, make database migrations:
    `python manage.py makemigrations`
    `python manage.py migrate`
  - And finally, run the application:
    `python manage.py runserver`

> Note: Existing admin account creds : admin:admin
>
>
> Note: For creating admin accounts, create django superuser with `python manage.py createsuperuser`
