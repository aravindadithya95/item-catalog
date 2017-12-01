from flask import Flask, render_template, url_for, flash

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

from database_setup import Base, User, Category, Item

from flask import make_response, request, redirect

from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)

# Connect to the database
engine = create_engine('postgresql:///catalog')
Base.metadata.bind = engine

# Create a database session
DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state

    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps("Invalid state parameter"), 401)
        return response

    # Obtain the one-time-use authorization code
    code = request.data

    # Upgrade the authorization code into a credentials object
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps("Failed to upgrade the authorization code."), 401)
        response.headers['content-type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['content-type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['content-type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['content-type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = '''
        <h1>Welcome, %s!</h1>
        <img src="%s"
             style = "width: 300px; height: 300px;
                      border-radius: 150px; -webkit-border-radius: 150px;
                      -moz-border-radius: 150px;" alt="Profile Picture">
    ''' % (login_session['username'], login_session['picture'])

    flash("You are now logged in as %s." % login_session['username'], 'success')

    return output


@app.route('/disconnect')
def disconnect():
    # Check if the user is connected
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps("Current user not connected."), 401)
        response.headers['content-type'] = 'application/json'
        return response

    # Revoke access token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print url
    print login_session['gplus_id']
    print access_token
    print login_session['username']
    print login_session['email']
    print result

    # Reset user session
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps("Successfully disconnected."), 200)
        response.headers['content-type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps("Failed to revoke token for given user.", 400))
        response.headers['content-type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalog')
def show_catalog():
    # Redirect if required
    if request.path == '/':
        redirect_url = '/catalog'
        return redirect(redirect_url, 302)

    # Get the catalog
    catalog = session.query(Category.name).all()

    return render_template('catalog.html', catalog=catalog)


@app.route('/catalog/<string:category_name>')
@app.route('/catalog/<string:category_name>/items')
def show_category(category_name):
    # Check if category exists
    try:
        session.query(Category.id).filter_by(
            name=category_name
        ).one()
    except NoResultFound:
        response = make_response("Invalid category name.", 404)
        return response

    # Redirect if required
    if not request.path.endswith('/items') or request.path == 'catalog/items':
        redirect_url = request.path + '/items'
        return redirect(redirect_url, 302)

    # Get the items
    items = session.query(Item.name).filter(
        Item.category_id == Category.id,
        Category.name == category_name
    ).all()

    return render_template('category.html', category_name=category_name, items=items)


@app.route('/catalog/<string:category_name>/items/<string:item_name>')
def show_item(category_name, item_name):
    # Get the item information
    try:
        item = session.query(Item.name, Item.description).filter(
            Item.name == item_name,
            Item.category_id == Category.id,
            Category.name == category_name
        ).one()
    except NoResultFound:
        response = make_response("Item not found.", 404)
        return response

    return render_template(
        'item.html',
        item_name=item_name,
        item_description=item.description,
        category_name=category_name
    )


@app.route('/catalog/<string:category_name>/new', methods=['GET', 'POST'])
def new_item(category_name):
    if request.method == 'POST':
        # Form data
        name = request.form['name']
        description = request.form['description']
        user_id = 1

        if not name:
            response = make_response("Invalid POST request.", 400)
            return response

        # Get Category ID
        try:
            category_id = session.query(Category.id).filter_by(
                name=category_name
            ).one().id
        except NoResultFound:
            response = make_response("Invalid POST request", 400)
            return response

        # Check if item already exists in that category
        try:
            result = session.query(Item).filter(
                Item.name == name,
                Item.category_id == category_id
            ).one()
        except NoResultFound:
            pass
        else:
            response = make_response("Item already exists in that category.", 409)
            return response

        # Add item
        new_item = Item(
            name=name,
            description=description,
            category_id=category_id,
            user_id=user_id
        )
        session.add(new_item)
        session.commit()

        flash("Menu Item (%s) added." % name, 'success')

        redirect_url = '/catalog/%s/items' % category_name
        return redirect(redirect_url)
    else:
        # Check if the category exists
        try:
            session.query(Category.id).filter_by(
                name=category_name
            ).one()
        except NoResultFound:
            response = make_response("Invalid category name.", 404)
            return response

        return render_template('new_item.html', category_name=category_name)


@app.route('/catalog/<string:category_name>/items/<string:item_name>/edit', methods=['GET', 'POST'])
def edit_item(category_name, item_name):
    if request.method == 'POST':
        # Form data
        name = request.form['name']
        description = request.form['description']

        if not name:
            response = make_response("Invalid POST request.", 400)
            return response

        # Check if the new name already exists in that category
        try:
            item_to_edit = session.query(Item.id).filter(
                Item.name == name,
                Item.category_id == Category.id,
                Category.name == category_name
            ).one()
        except NoResultFound:
            pass
        else:
            flash("Item already exists in that category.", 'error')

            redirect_url = '/catalog/%s/items/%s/edit' % (category_name, item_name)
            return redirect(redirect_url)

        # Get the item
        try:
            item_to_edit = session.query(Item).filter(
                Item.name == item_name,
                Item.category_id == Category.id,
                Category.name == category_name
            ).one()
        except NoResultFound:
            response = make_response('Item not found.', 404)
            return response

        # Edit item
        item_to_edit.name = name
        item_to_edit.description = description
        session.add(item_to_edit)
        session.commit()

        flash("Menu Item (%s) edited." % item_name, 'success')

        redirect_url = '/catalog/%s/items' % category_name
        return redirect(redirect_url)
    else:
        return render_template('edit_item.html', item_name=item_name, category_name=category_name)


@app.route('/catalog/<string:category_name>/items/<string:item_name>/delete', methods=['GET', 'POST'])
def delete_item(category_name, item_name):
    if request.method == 'POST':
        # Get the item
        try:
            item_to_delete = session.query(Item).filter(
                Item.name == item_name,
                Item.category_id == Category.id,
                Category.name == category_name
            ).one()
        except NoResultFound:
            response = make_response('Item not found.', 404)
            return response

        # Delete item
        session.delete(item_to_delete)
        session.commit()

        flash("Menu Item (%s) deleted." % item_name, 'success')

        redirect_url = '/catalog/%s/items' % category_name
        return redirect(redirect_url)
    else:
        return render_template('delete_item.html', item_name=item_name, category_name=category_name)


if __name__ == '__main__':
    app.secret_key = 'catalog_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
