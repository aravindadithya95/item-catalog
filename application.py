from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

from database_setup import Base, User, Category, Item

from flask import make_response

app = Flask(__name__)

# Connect to the database
engine = create_engine('postgresql:///catalog')
Base.metadata.bind = engine

# Create a database session
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog')
def show_catalog():
    catalog = session.query(Category.name).all()
    output = ''
    for category in catalog:
        output += category.name + '<br>'
    return output


@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/items/')
def show_category(category_name):
    items = session.query(Item.name).filter(
        Item.category_id == Category.id,
        Category.name == category_name
    ).all()
    output = ''
    for item in items:
        output += item.name + '<br>'
    return output


@app.route('/catalog/<string:category_name>/items/<string:item_name>/')
def show_item(category_name, item_name):
    item_name = item_name.replace('-', ' ')
    try:
        item = session.query(Item.name, Item.description).filter(
            Item.category_id == Category.id,
            Category.name == category_name,
            Item.name == item_name
        ).one()
    except NoResultFound:
        response = make_response("Item not found.", 404)
        return response

    output = item.name + "<br>" + item.description
    return output


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
