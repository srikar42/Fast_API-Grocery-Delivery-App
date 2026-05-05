from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from enum import Enum

app = FastAPI()

# ─── ENUM ─────────────────────────────
class DeliverySlot(str, Enum):
    morning = "Morning"
    evening = "Evening"
    pickup = "Self-Pickup"

# ─── MODELS ───────────────────────────
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)
    delivery_address: str = Field(..., min_length=10)
    delivery_slot: DeliverySlot = DeliverySlot.morning
    bulk_order: bool = False

class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)
    delivery_slot: DeliverySlot = DeliverySlot.morning

class NewItem(BaseModel):
    name: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    unit: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    in_stock: bool = True

# ─── DATA ─────────────────────────────
items = [
    {"id": 1, "name": "Milk", "price": 50, "unit": "litre", "category": "Dairy", "in_stock": True},
    {"id": 2, "name": "Rice", "price": 60, "unit": "kg", "category": "Grain", "in_stock": True},
    {"id": 3, "name": "Apple", "price": 120, "unit": "kg", "category": "Fruit", "in_stock": True},
    {"id": 4, "name": "Tomato", "price": 30, "unit": "kg", "category": "Vegetable", "in_stock": False},
    {"id": 5, "name": "Eggs", "price": 70, "unit": "dozen", "category": "Poultry", "in_stock": True},
    {"id": 6, "name": "Wheat", "price": 80, "unit": "kg", "category": "Grain", "in_stock": True}
]

cart = []
orders = []
order_counter = 1

# ─── HELPERS ──────────────────────────
def find_item(item_id):
    for i in items:
        if i["id"] == item_id:
            return i
    return None

def calculate_order_total(price, quantity, slot, bulk_order=False):
    original = price * quantity
    discount = 0.08 * original if bulk_order and quantity >= 10 else 0
    discounted = original - discount
    delivery = 40 if slot == "Morning" else 60 if slot == "Evening" else 0
    final = discounted + delivery
    return {
        "original": original,
        "discount": discount,
        "final": final
    }

# ─── BASIC ROUTES ─────────────────────
@app.get('/')
def home():
    return {"message": "Welcome"}

@app.get('/items')
def get_items():
    return {"items": items, "total": len(items)}

@app.get('/items/search')
def search_items(keyword: str):
    res = [i for i in items if keyword.lower() in i["name"].lower() or keyword.lower() in i["category"].lower()]
    return {"items": res, "total": len(res)}

@app.get('/items/sort')
def sort_items(sort_by: str = "price", order: str = "asc"):
    
    # validate sort_by
    if sort_by not in ["price", "name", "category"]:
        raise HTTPException(status_code=400, detail="Invalid sort_by field")

    # validate order
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order (use asc or desc)")

    reverse = True if order == "desc" else False

    sorted_items = sorted(items, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "total_items": len(sorted_items),
        "items": sorted_items
    }

@app.get('/items/page')
def paginate_items(page: int = 1, limit: int = 4):

    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="page and limit must be > 0")

    total_items = len(items)
    total_pages = (total_items + limit - 1) // limit   # full formula

    if page > total_pages:
        raise HTTPException(status_code=404, detail="Page not found")

    start = (page - 1) * limit
    end = start + limit

    paginated_items = items[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "items": paginated_items
    }

@app.get('/items/browse')
def browse_items(
    keyword: str = None,
    category: str = None,
    in_stock: bool = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    
    result = items

    #  1. Keyword search
    if keyword:
        result = [
            i for i in result
            if keyword.lower() in i["name"].lower()
            or keyword.lower() in i["category"].lower()
        ]

    #  2. Category filter
    if category:
        result = [i for i in result if i["category"].lower() == category.lower()]

    # 3. Stock filter
    if in_stock is not None:
        result = [i for i in result if i["in_stock"] == in_stock]

    # 🔃 4. Sorting (validate first)
    if sort_by not in ["price", "name", "category"]:
        raise HTTPException(400, "Invalid sort_by")

    if order not in ["asc", "desc"]:
        raise HTTPException(400, "Invalid order")

    result = sorted(
        result,
        key=lambda x: x[sort_by],
        reverse=(order == "desc")
    )

    # 5. Pagination
    total_items = len(result)
    total_pages = (total_items + limit - 1) // limit

    if page < 1 or limit < 1:
        raise HTTPException(400, "page and limit must be > 0")

    if page > total_pages and total_items != 0:
        raise HTTPException(404, "Page not found")

    start = (page - 1) * limit
    end = start + limit

    paginated = result[start:end]

    return {
        "filters": {
            "keyword": keyword,
            "category": category,
            "in_stock": in_stock
        },
        "sorting": {
            "sort_by": sort_by,
            "order": order
        },
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages
        },
        "results": paginated
    }


@app.get('/items/{item_id}')
def get_item(item_id: int):
    item = find_item(item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item

# ─── ITEMS ADVANCED ───────────────────

@app.get('/items/filter')
def filter_items(category: str = None, max_price: int = None, unit: str = None, in_stock: bool = None):
    res = items
    if category is not None:
        res = [i for i in res if i["category"].lower() == category.lower()]
    if max_price is not None:
        res = [i for i in res if i["price"] <= max_price]
    if unit is not None:
        res = [i for i in res if i["unit"].lower() == unit.lower()]
    if in_stock is not None:
        res = [i for i in res if i["in_stock"] == in_stock]
    return {"items": res}

@app.post('/items')
def add_item(item: NewItem):
    if any(i["name"].lower() == item.name.lower() for i in items):
        raise HTTPException(400, "Duplicate")
    new = {**item.dict(), "id": len(items) + 1}
    items.append(new)
    return new

@app.put('/items/{item_id}')
def update_item(item_id: int, price: int = None, in_stock: bool = None):
    item = find_item(item_id)
    if not item:
        raise HTTPException(404, "Not found")
    if price is not None:
        item["price"] = price
    if in_stock is not None:
        item["in_stock"] = in_stock
    return item

@app.delete('/items/{item_id}')
def delete_item(item_id: int):
    item = find_item(item_id)
    if not item:
        raise HTTPException(404, "Not found")
    items.remove(item)
    return {"message": "Deleted"}

# ─── CART ─────────────────────────────
@app.post('/cart/add')
def add_cart(item_id: int = Query(...), quantity: int = Query(1)):
    item = find_item(item_id)
    if not item:
        raise HTTPException(404, "Not found")

    for c in cart:
        if c["item_id"] == item_id:
            c["quantity"] += quantity
            return c

    new = {"item_id": item_id, "name": item["name"], "price": item["price"], "quantity": quantity}
    cart.append(new)
    return new

@app.get('/cart')
def view_cart():
    total = sum(i["price"] * i["quantity"] for i in cart)
    return {"cart": cart, "total": total}

@app.delete('/cart/{item_id}')
def delete_cart(item_id: int):
    for i in cart:
        if i["item_id"] == item_id:
            cart.remove(i)
            return {"message": "removed"}
    raise HTTPException(404, "Not found")

@app.post('/cart/checkout')
def checkout(data: CheckoutRequest):
    global order_counter
    if not cart:
        raise HTTPException(400, "Empty cart")

    res = []
    total = 0

    for c in cart:
        pricing = calculate_order_total(c["price"], c["quantity"], data.delivery_slot.value)
        order = {
                "order_id": order_counter,
                "customer_name": data.customer_name,
                "item_name": c["name"],
                "quantity": c["quantity"],
                "delivery_slot": data.delivery_slot.value,
                "delivery_address": data.delivery_address,
                "pricing": pricing,
                "status": "confirmed"
            }        
        orders.append(order)
        res.append(order)
        total += pricing["final"]
        order_counter += 1

    cart.clear()
    return {"orders": res, "grand_total": total}

# ─── ORDERS ───────────────────────────

# SEARCH (must be above generic routes)
@app.get('/orders/search')
def search_orders(customer_name: str):
    result = [
        o for o in orders
        if customer_name.lower() in o.get("customer_name", "").lower()
    ]
    return {
        "orders": result,
        "total_found": len(result)
    }


# SORT
@app.get('/orders/sort')
def sort_orders(order: str = "asc"):

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order (asc/desc)")

    sorted_orders = sorted(
        orders,
        key=lambda x: x["pricing"].get("final_total", 0),
        reverse=(order == "desc")
    )

    return {
        "order": order,
        "total_orders": len(sorted_orders),
        "orders": sorted_orders
    }


# PAGINATION
@app.get('/orders/page')
def paginate_orders(page: int = 1, limit: int = 3):

    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="page and limit must be > 0")

    total_orders = len(orders)
    total_pages = (total_orders + limit - 1) // limit

    if page > total_pages and total_orders != 0:
        raise HTTPException(status_code=404, detail="Page not found")

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total_orders": total_orders,
        "total_pages": total_pages,
        "orders": orders[start:end]
    }


# GET ALL
@app.get('/orders')
def get_orders():
    return {
        "orders": orders,
        "total": len(orders)
    }


# CREATE ORDER
@app.post('/orders')
def place_order(order: OrderRequest):
    global order_counter

    item = find_item(order.item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if not item["in_stock"]:
        raise HTTPException(status_code=400, detail="Item is out of stock")

    pricing = calculate_order_total(
        item["price"],
        order.quantity,
        order.delivery_slot.value,
        order.bulk_order
    )

    new_order = {
        "order_id": order_counter,
        "customer_name": order.customer_name,
        "item_name": item["name"],
        "quantity": order.quantity,
        "unit": item["unit"],
        "delivery_slot": order.delivery_slot.value,
        "delivery_address": order.delivery_address,
        "pricing": pricing,
        "status": "confirmed"
    }

    orders.append(new_order)
    order_counter += 1

    return new_order