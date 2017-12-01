from flask import Flask, render_template, url_for, flash

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
    # Redirect if required
    if request.path == '/':
        redirect_url = '/catalog/'
        return redirect(redirect_url, 302)

    # Get the catalog
    catalog = session.query(Category.name).all()

    return render_template('catalog.html', catalog=catalog)


@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/items/')
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
    if not request.path.endswith('/items/'):
        redirect_url = request.path + 'items/'
        return redirect(redirect_url, 302)

    # Get the items
    items = session.query(Item.name).filter(
        Item.category_id == Category.id,
        Category.name == category_name
    ).all()

    return render_template('category.html', category_name=category_name, items=items)


@app.route('/catalog/<string:category_name>/items/<string:item_name>/')
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


@app.route('/catalog/<string:category_name>/new/', methods=['GET', 'POST'])
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

        redirect_url = '/catalog/%s/items/' % category_name
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


@app.route('/catalog/<string:category_name>/items/<string:item_name>/edit/', methods=['GET', 'POST'])
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

            redirect_url = '/catalog/%s/items/%s/edit/' % (category_name, item_name)
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

        redirect_url = '/catalog/%s/items/' % category_name
        return redirect(redirect_url)
    else:
        return render_template('edit_item.html', item_name=item_name, category_name=category_name)


@app.route('/catalog/<string:category_name>/items/<string:item_name>/delete/', methods=['GET', 'POST'])
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

        redirect_url = '/catalog/%s/items/' % category_name
        return redirect(redirect_url)
    else:
        return render_template('delete_item.html', item_name=item_name, category_name=category_name)


if __name__ == '__main__':
    app.secret_key = 'catalog_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
