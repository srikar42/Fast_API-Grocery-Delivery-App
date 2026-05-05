![FastAPI](https://img.shields.io/badge/FastAPI-Backend-blue)
![REST API](https://img.shields.io/badge/REST-API-green)
![Cart System](https://img.shields.io/badge/Cart-System-orange)
![Orders](https://img.shields.io/badge/Orders-Processing-purple)
![Pagination](https://img.shields.io/badge/Pagination-Enabled-yellow)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

# 🛒 FastAPI Grocery Backend

A complete backend system for a grocery delivery application built using FastAPI.
This project demonstrates real-world backend features including cart management, order processing, and advanced query handling.

---

## 🚀 Features

* RESTful APIs built with FastAPI
* Pydantic-based request validation
* Full CRUD operations for items
* Cart system (add, remove, view items)
* Checkout workflow (cart → orders)
* Bulk order discount logic (8% for large quantities)
* Delivery charge calculation (slot-based)
* Search, filter, sort, and pagination for items
* Order management with search, sorting, and pagination
* Interactive API testing using Swagger UI

---

## 🧠 Core Functionalities

### 📦 Items

* Add, update, delete items
* Filter by category, price, stock
* Search by keyword
* Sort and paginate results

### 🛒 Cart

* Add items to cart
* Merge quantities
* Remove items
* View cart with totals

### 💳 Checkout

* Convert cart into orders
* One order per item
* Calculate final cost with delivery charges

### 📑 Orders

* Place orders directly
* Search by customer name
* Sort by total cost
* Paginate results

---

## 🛠 Tech Stack

* Python
* FastAPI
* Pydantic

---

## ▶️ Run Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open API docs:

```
http://127.0.0.1:8000/docs
```

---

## 📸 API Preview

Swagger UI examples are included in the repository screenshots.

---

## 📁 Project Structure

```
grocery-api/
│
├── main.py
├── requirements.txt
├── README.md
└── screenshots/
```

---

## ⚠️ Limitations

* Uses in-memory data (no database)
* No authentication or user management
* Not designed for production use

---

## 🎯 Future Improvements

* Integrate database (SQLite/PostgreSQL with SQLAlchemy)
* Add authentication (JWT)
* Modular project structure (routers, services)
* Dockerize the application

---

## 📌 Author

Bhanu Sai Prakash Bandaru

Aspiring Data Scientist | FastAPI
