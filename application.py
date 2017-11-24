from flask import Flask
app = Flask(__name__)


@app.route('/')
@app.route('/catalog')
def show_catalog():
    return "List of categories."


@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/items/')
def show_category(category_name):
    return "List of items in that category."


@app.route('/catalog/<string:category_name>/<string:item_name>/')
def show_item(category_name, item_name):
    return "The selected item."


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
