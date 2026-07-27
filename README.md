# Multi-Vendor E-Commerce Platform

A feature-complete, modern Multi-Vendor E-Commerce Platform built with **Python FastAPI**, **SQLAlchemy ORM (SQLite)**, **JWT Authentication**, and an interactive **Single Page Application (SPA)** frontend.

---

## 🌟 Key Features

- **JWT Dual Token Auth**: Access Token, Refresh Token, Token Blacklisting, Password Reset, Email Verification.
- **Multi-Vendor Architecture**: Vendor store profiles, vendor product management, sales analytics, vendor order line-item fulfillment.
- **Product Catalog**: Live search, category filtering, stock tracking, verified customer reviews & star ratings.
- **Multi-Vendor Cart & Checkout**: Single checkout for items from multiple vendors, proportional order splitting.
- **Coupons & Discounts**: Global and vendor-specific percentage or fixed amount discounts (`WELCOME10`, `VENDOR20`).
- **Mock Payment Gateway**: Credit Card, UPI, and PayPal checkout simulation with transaction logging.
- **Admin Panel**: Platform GMV analytics, 10% platform commission tracking, vendor approval & moderation, platform coupon manager.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, PyJWT, Pydantic V2, Uvicorn
- **Database**: SQLite (SQLAlchemy ORM)
- **Frontend**: HTML5, Vanilla CSS (Glassmorphism, Dark Mode, Micro-animations), Vanilla JavaScript

---

## 📁 Directory Structure

```
d:/PI/
├── requirements.txt         # Project dependencies
├── run.py                   # Server launcher script
├── app/
│   ├── main.py              # FastAPI app initialization & static mounts
│   ├── core/                # App config & JWT security algorithms
│   ├── database/            # SQLite SQLAlchemy connection & sessions
│   ├── models/              # User, Vendor, Product, Coupon, Order, Review, Wishlist, Token models
│   ├── schemas/             # Request & Response Pydantic schemas
│   ├── dependencies/        # Role-based authorization wrappers (RBAC)
│   ├── services/            # Auth, Product, Order, Coupon, and Admin business logic
│   ├── utils/               # Database seed script (seed_data.py)
│   ├── middleware/          # CORS & performance timing headers
│   └── api/                 # Modular REST API endpoints
└── static/
    ├── index.html           # Unified web application layout
    ├── css/styles.css       # Complete modern CSS design system
    └── js/app.js            # SPA logic, state management & API integration
```

---

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/NikeshTarur0/Multi-Vendor-E-Commerce-Platform.git
   cd Multi-Vendor-E-Commerce-Platform
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```

4. **Access in browser**:
   - Web App UI: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - API Documentation (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔑 Demo Account Credentials

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@ecommerce.com` | `admin123` |
| **Vendor (TechNexus)** | `vendor1@technexus.com` | `vendor123` |
| **Vendor (StyleCraft)** | `vendor2@stylecraft.com` | `vendor123` |
| **Customer** | `customer@gmail.com` | `customer123` |
