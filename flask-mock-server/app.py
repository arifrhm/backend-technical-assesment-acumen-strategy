from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# Load customer data from JSON file
def load_customers():
    data_file = os.path.join(os.path.dirname(__file__), 'data', 'customers.json')
    with open(data_file, 'r') as f:
        return json.load(f)

customers = load_customers()


@app.route('/api/customers', methods=['GET'])
def get_customers():
    """
    Get paginated list of customers.
    Query params: page (default: 1), limit (default: 10)
    """
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    # Calculate pagination
    total = len(customers)
    start = (page - 1) * limit
    end = start + limit

    # Get paginated data
    paginated_customers = customers[start:end]

    return jsonify({
        "data": paginated_customers,
        "total": total,
        "page": page,
        "limit": limit
    })


@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """
    Get a single customer by ID.
    Returns 404 if customer not found.
    """
    customer = next((c for c in customers if c['customer_id'] == customer_id), None)

    if customer is None:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(customer)


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({
        "status": "healthy",
        "service": "flask-mock-server",
        "total_customers": len(customers)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
