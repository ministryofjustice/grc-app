
[Gender Recognition Certificate service](../README.md) >
[Developer documentation](README.md) >
Getting the code running

# Getting the code running

### Get the code:
* Clone this repo

* Open the Folder in your IDE  

### Get and edit the config files:

* Ask an existing developer for a copy of the files listed below and
  save them to the root folder of your local repository
  (the files are git ignored, so they shouldn't get committed - **check this!**)
  * `.env`
  * `.admin.env`
  * `.dashboard.env`


* In the `.admin.env` file, edit the line `DEFAULT_ADMIN_USER=` to use your email address


* Make sure you are a [team member of the GRC service on Gov.UK Notify](https://www.notifications.service.gov.uk/services/36bdb0a3-86e3-423d-b1ce-26fae1ead417/users)  
  The Admin website is about to send you an email, so you need to be able to receive it!  
  You need to be a team member of the service in order to receive emails in test environments.


* For One Login, you need to create a `private_key.pem` file under `grc > one_login > keys`. You can get this from your team or from the kubernetes secret `one_login_keys` under non-production environments.

### Fetch the project dependencies:
* Ensure that Docker is installed

* Open a Bash terminal in the root folder of the project

* Create a virtual environment and activate it

* Run `pip install -r requirements.txt`  
  This installs the Python dependencies

* Run `npm install`  
  This installs the Javascript dependencies

* Run `pybabel compile -d grc/translations`
  
  This compiles the welsh translations so it works on your local

### Build (and run) the code:
* Open a Bash terminal in the root folder of the project

* Run `docker-compose up --build`  
  * The public-facing website should be visible at http://localhost:3000/  
  * The admin website should be visible at http://localhost:3001/
  * The dashboard website should be visible at http://localhost:3002/
  * The JWKS url should be visible at http://localhost:3003/.well-known/jwks.json

### Just run the code:
* Open a Bash terminal in the root folder of the project

* Run `docker-compose up`
  * The public-facing website should be visible at http://localhost:3000/  
  * The admin website should be visible at http://localhost:3001/
  * The dashboard website should be visible at http://localhost:3002/
  * The JWKS url should be visible at http://localhost:3003/.well-known/jwks.json

### Login to the admin website:
* Visit the admin website http://localhost:3001/
* You should (within a few minutes) receive a welcome email with a temporary password
* Use this temporary password to login

Note: If you don't receive the welcome email to the admin website, check:
* Does the '.admin.env' file have your email address listed in the `DEFAULT_ADMIN_USER` setting?
* Are you a [team member of the GRC service on Gov.UK Notify](https://www.notifications.service.gov.uk/services/36bdb0a3-86e3-423d-b1ce-26fae1ead417/users)
* Connect to your local database, look in the `admin_user` table.  
  There should be exactly 1 row, with your email address in the `email` column.  
  If not, change the email address to be yours, then use the *Reset Password* functionality to change your password and login
