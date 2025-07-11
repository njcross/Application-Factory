# 🚗 Application Factory - Auto Service Ticket System

A modular Flask API using the Application Factory pattern to manage customer data, service tickets, mechanics, and inventory for an auto repair system.

---

## 🔧 Features

- JWT Authentication for customers
- CRUD operations for:
  - Customers
  - Service Tickets
  - Mechanics
  - Inventory
- Add/remove mechanics from service tickets
- Link inventory parts to tickets with quantity tracking
- Role-based access to routes
- Token-protected routes with customer-specific data access
- Caching support via Flask-Caching
- Pagination support on selected endpoints

---

## 🏁 Getting Started

### 🔨 Installation

1. **Clone the repo:**
   ```bash
   git clone https://github.com/njcross/Application-Factory.git
   cd Application-Factory
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   Create a `.env` file with:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   ```

5. **Run the application:**
   ```bash
   flask db upgrade
   flask run
   ```

---

## 🧪 Example Endpoints

### 🧍 Customers
- `POST /customers/register` – Register a new customer
- `POST /customers/login` – Authenticate and receive token
- `GET /customers?page=1` – Paginated list of customers
- `PUT /customers/<id>` – Update customer (token required)

### 🧾 Tickets
- `POST /tickets` – Create a service ticket (token required)
- `GET /tickets/<id>` – View ticket details
- `PUT /tickets/<ticket_id>/edit` – Add/remove mechanics
- `GET /my-tickets` – View tickets for the authenticated customer

### 🧑‍🔧 Mechanics
- `POST /mechanics` – Create a mechanic
- `GET /mechanics` – List of mechanics (cached)
- `GET /mechanics/most-active` – List mechanics by tickets worked on

### 🧰 Inventory
- `POST /inventory` – Add inventory item
- `PUT /inventory/<id>` – Update inventory item
- `PUT /tickets/<ticket_id>/add-part/<inventory_id>` – Add part to a ticket
- `GET /inventory` – List all inventory items

---

## 🔒 Authentication

Use the returned Bearer Token from the login route in the Authorization header for protected routes:

```http
Authorization: Bearer <your_token_here>
```

---

## 🧱 Tech Stack

- Python / Flask
- SQLAlchemy ORM with Type Annotations
- Marshmallow for serialization
- JWT for secure authentication
- Flask-Migrate for migrations
- SQLite (default, replaceable)

---

## 🧹 TODO

- Admin dashboard UI
- Mechanic scheduling
- Email notifications

---

## 📁 Project Structure

```
Application-Factory/
│
├── app/
│   ├── blueprints/
│   │   ├── customers/
│   │   ├── tickets/
│   │   ├── mechanics/
│   │   └── inventory/
│   ├── extensions.py
│   ├── models.py
│   └── __init__.py
│
├── migrations/
├── run.py
├── requirements.txt
└── README.md
```

---

