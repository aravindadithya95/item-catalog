# Item Catalog
This project is a web application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

This project is part of the [Full Stack Web Developer Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004) at _Udacity_.

## Getting Started
### Setting up the environment
- Make sure you have **Python 2.x** installed in your machine.
- Install VirtualBox from [here](https://www.virtualbox.org/wiki/Downloads) and vagrant from [here](https://www.vagrantup.com/downloads.html).
- Download or clone a local copy of this [repository](https://github.com/udacity/fullstack-nanodegree-vm) and download or clone the Item Catalog repository into the vagrant directory.
- To go into the vagrant environment, run the following commands from anywhere within the vagrant directory.
```
vagrant up
vagrant ssh
```

### Setting up the application
- Run `python models.py` to setup the database.
- Run `python populate_db.py` to populate the database with data.

### Setting up authentication
The app uses OAuth for authentication, with Google and Facebook as OAuth providers.

To use your own credentials:
- Register the app with [Google](https://console.developers.google.com) and replace the credentials in the `client_secrets.json` file.
- Register the app with [Facebook](https://developers.facebook.com) and replace the credentials in the `fb_client_secrets.json` file.

### Starting the server
- Run `python views.py` to start the Flask web server.
- You can now access the application at [http://localhost:5000](http://localhost:5000).

### Accessing the JSON endpoints
- Login to the application to get an API link on the nav bar, where you can claim API key valid for ten minutes.
- You can access an endpoint using *curl* like:
```
curl -H "Authorization: Bearer <API_KEY>" <ENDPOINT>
```
- There are three types of endpoints to access:
```
http://localhost:5000/api/v1/catalog
http://localhost:5000/api/v1/catalog/<CATEGORY_NAME>/items
http://localhost:5000/api/v1/catalog/<CATEGORY_NAME>/items/<ITEM_NAME>
```
