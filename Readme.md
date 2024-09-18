## Getting started
* Install python with version 12.X.X 
* Create Virtual Env and then activate this env.
* Install all dependancy with command 
    ```
    pip install -r requirements.txt
    ```
* In this project we use aiven postgress database so no need to configure related to database just run server using command 
    ```
    python manage.py runserver
    ```
* if do any changes in db on your end then use command
    ```
    python manage.py makemigrations
    python manage.py migrate
    ```
Now you are good to go with django and python setup need to setup redis

### Setup radis
* Install ubuntu in your windows if using windows Os
* Configure ubuntu and set password (In my case the password is `admin` if you use different password than just change password on file `settings.py` line number 84 replace `admin` to `your_password`)

### Install redis in Ubuntu using below commond
Step 1:
```
sudo apt update
```
Step 2:
```
sudo apt install redis-server
```
Step 3:
```
sudo systemctl start redis-server
```
Step 4:
```
sudo systemctl enable redis-server
```
Step 5:
```
sudo systemctl status redis-server
```
Step 6:
```
redis-cli
```