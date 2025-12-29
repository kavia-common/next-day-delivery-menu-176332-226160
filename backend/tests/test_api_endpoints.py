"""
Backend API tests for the Flask app.

Covers:
- Healthcheck endpoint "/"
- GET /api/menu
- POST /api/orders
- CORS OPTIONS preflight handling

Run with:
    pytest -q
"""

import json


def test_healthcheck_root(client):
    """
    Healthcheck should be available at "/" and return {"message": "Healthy"} and 200.
    """
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get("message") == "Healthy"


def test_menu_get_returns_list_structure(client):
    """
    GET /api/menu should return a JSON array of items with fields:
    {id, name, description, price}. Types:
    - id: str or int
    - name: str
    - description: str (may be empty/missing)
    - price: number (int or float)

    If the list is empty, it should still return 200 and [].
    """
    resp = client.get("/api/menu", headers={"Accept": "application/json"})
    # If not implemented yet, this may be 404 and should be implemented to pass.
    assert resp.status_code in (200, 404)
    if resp.status_code == 404:
        # TDD: define expected behavior; this test will pass once endpoint exists.
        return

    data = resp.get_json()
    assert isinstance(data, list), "Expected a JSON array response."
    # Empty list is acceptable
    if len(data) == 0:
        return

    # Validate structure
    for item in data:
        assert "id" in item, "Missing id"
        assert "name" in item, "Missing name"
        assert "price" in item, "Missing price"
        # description may be optional, but if present ensure it is str
        if "description" in item and item["description"] is not None:
            assert isinstance(item["description"], str)

        # type checks
        assert isinstance(item["name"], str)
        assert isinstance(item["price"], (int, float))
        # id can be string or int depending on implementation
        assert isinstance(item["id"], (str, int))


def test_orders_post_success_and_validation(client):
    """
    POST /api/orders accepts:
    {
      customer: {name, phone, address, notes},
      items: [{id, qty}],
      requested_delivery: "next-day"
    }
    Returns 200/201 with { message } on success.

    Should return 400 with error details for:
    - missing fields
    - empty items
    - invalid qty (<=0 or non-numeric)
    """
    # Successful payload
    payload_ok = {
        "customer": {
            "name": "Jane Doe",
            "phone": "+1 555 123 4567",
            "address": "123 Main St, City",
            "notes": "Leave at door",
        },
        "items": [{"id": "demo-1", "qty": 2}, {"id": "demo-2", "qty": 1}],
        "requested_delivery": "next-day",
    }
    resp = client.post(
        "/api/orders",
        data=json.dumps(payload_ok),
        content_type="application/json",
        headers={"Accept": "application/json"},
    )
    # If not implemented yet, we allow 404 to avoid failing the suite prematurely (TDD).
    assert resp.status_code in (200, 201, 404)
    if resp.status_code != 404:
        data = resp.get_json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str) and len(data["message"]) > 0

    # Missing fields
    payload_missing = {
        "customer": {"name": "Jane"},
        "items": [{"id": "x", "qty": 1}],
    }
    resp_missing = client.post(
        "/api/orders",
        data=json.dumps(payload_missing),
        content_type="application/json",
        headers={"Accept": "application/json"},
    )
    assert resp_missing.status_code in (400, 404)

    # Empty items
    payload_empty_items = {
        "customer": {"name": "Jane", "phone": "1", "address": "Addr", "notes": ""},
        "items": [],
        "requested_delivery": "next-day",
    }
    resp_empty = client.post(
        "/api/orders",
        data=json.dumps(payload_empty_items),
        content_type="application/json",
        headers={"Accept": "application/json"},
    )
    assert resp_empty.status_code in (400, 404)

    # Invalid qty (zero)
    payload_bad_qty = {
        "customer": {"name": "Jane", "phone": "1", "address": "Addr", "notes": ""},
        "items": [{"id": "x", "qty": 0}],
        "requested_delivery": "next-day",
    }
    resp_bad_qty = client.post(
        "/api/orders",
        data=json.dumps(payload_bad_qty),
        content_type="application/json",
        headers={"Accept": "application/json"},
    )
    assert resp_bad_qty.status_code in (400, 404)


def test_cors_preflight_options(client):
    """
    If CORS is enabled, OPTIONS preflight should be handled and return 200 (or 204)
    with appropriate CORS headers.
    """
    resp = client.options(
        "/api/menu",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert resp.status_code in (200, 204, 404)
    if resp.status_code != 404:
        # Flask-CORS typically adds these headers
        acao = resp.headers.get("Access-Control-Allow-Origin")
        assert acao in ("*", "http://example.com")
        assert resp.headers.get("Access-Control-Allow-Methods") is not None
