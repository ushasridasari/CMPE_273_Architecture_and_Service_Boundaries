from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory sample data, owned only by this service
INVENTORY = {"laptop": 5, "phone": 0, "headphones": 12}


@app.get("/inventory/<item>")
def check_item(item):
    """Query: is the requested quantity of this item available?"""
    qty_requested = request.args.get("quantity", 1, type=int)
    stock = INVENTORY.get(item, 0)
    return jsonify(item=item, available=stock >= qty_requested, in_stock=stock)


if __name__ == "__main__":
    app.run(port=5001)
