import uuid

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

INVENTORY_URL = "http://localhost:5001"
ORDERS = {}  # In-memory, owned only by this service


@app.post("/orders")
def create_order():
    """Command: ask the system to create an order."""
    data = request.get_json(silent=True) or {}
    item, qty = data.get("item"), data.get("quantity", 1)
    if not item:
        return jsonify(error="'item' is required"), 400

    # Query the Inventory Service (never read its data directly)
    try:
        resp = requests.get(
            f"{INVENTORY_URL}/inventory/{item}",
            params={"quantity": qty},
            timeout=2,
        )
        resp.raise_for_status()
        available = resp.json()["available"]
    except (requests.ConnectionError, requests.Timeout):
        return jsonify(error="Inventory Service is unavailable. Please try again later."), 503
    except requests.RequestException:
        return jsonify(error="Unexpected error from Inventory Service."), 502

    if not available:
        return jsonify(status="rejected", reason=f"'{item}' is unavailable"), 409

    order_id = str(uuid.uuid4())
    ORDERS[order_id] = {"id": order_id, "item": item, "quantity": qty, "status": "created"}
    return jsonify(ORDERS[order_id]), 201


@app.get("/orders/<order_id>")
def get_order(order_id):
    """Query: look up an existing order."""
    order = ORDERS.get(order_id)
    return (jsonify(order), 200) if order else (jsonify(error="not found"), 404)


if __name__ == "__main__":
    app.run(port=8000)
