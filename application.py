from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

from database_setup import Base, User, Category, Item

from flask import make_response, request, redirect

app = Flask(__name__)

# Connect to the database
engine = create_engine('postgresql:///catalog')
Base.metadata.bind = engine

# Create a database session
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog/')
def show_catalog():
    catalog = session.query(Category.name).all()
    output = ''
    for category in catalog:
        output += category.name + '<br>'
    return output


@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/items/')
def show_category(category_name):
    # Redirect to a standard URL if required
    category_name_lcase = category_name.lower()
    if category_name != category_name_lcase:
        redirect_url = request.url.replace(category_name, category_name_lcase)
        return redirect(redirect_url, 302)

    items = session.query(Item.name).filter(
        Item.category_id == Category.id,
        func.lower(Category.name) == category_name
    ).all()

    output = ''
    for item in items:
        output += item.name + '<br>'
    return output


@app.route('/catalog/<string:category_name>/items/<string:item_name>/')
def show_item(category_name, item_name):
    # Redirect to a standard URL if required
    category_name_lcase = category_name.lower()
    item_name_lcase = item_name.lower()
    if category_name != category_name_lcase or item_name != item_name_lcase:
        redirect_url = '/catalog/%s/items/%s/' % (
            category_name_lcase, item_name_lcase
        )
        return redirect(redirect_url)

    item_name = item_name.replace('-', '_')
    try:
        items = session.query(Item.name, Item.description).filter(
            Item.category_id == Category.id,
            func.lower(Item.name).like(item_name)
        ).all()
    except NoResultFound:
        response = make_response("Item not found.", 404)
        return response

    for item in items:
        if item.name.lower().replace(' ', '-') == item_name.replace('_', '-'):
            output = item.name + "<br>" + item.description
            return output

    response = make_response("Item not found.", 404)
    return response


@app.route('/catalog/<string:category_name>/new/')
def new_item(category_name):
    return "The page to add a new item to the category."


@app.route('/catalog/<string:category_name>/<string:item_name>/edit/')
def edit_item(category_name, item_name):
    return "The page to edit the selected item."


@app.route('/catalog/<string:category_name>/<string:item_name>/delete/')
def delete_item(category_name, item_name):
    return "The page to delete the selected item."


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
