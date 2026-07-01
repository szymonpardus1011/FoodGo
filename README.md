# FoodGo 🍔📱

Modern web application for managing catering orders, designed and implemented with a **Mobile-First** approach to perfectly mimic a smartphone interface directly in the web browser.

---

## 🛠️ Tech Stack
* **Backend:** Python 3, Flask micro-framework
* **Database:** SQLite3 (Relational file-based database)
* **Frontend:** Vanilla HTML5, CSS3, Jinja2 templates (No external frameworks like Bootstrap used)
* **Security:** Werkzeug (Kryptograficzne haszowanie haseł)

---

## 🚀 Key Features

### 1. Customer Mode (Platforma Zamówień)
* Browsing dynamically generated menus from local restaurants.
* Interactive shopping cart system with automatic total amount calculation.
* Choice of payment method (Cash / Card) and order finalization.
* User profile management (username/password updates).

### 2. Restaurant Mode (Panel Zarządzania Menu)
* Full control over the restaurant's culinary offers.
* Ability to add new dishes with custom names, prices, and descriptions.
* Quick deletion of outdated menu positions from the SQLite3 database.

---

## 🔒 Security & System Control
* **Password Hashing:** Passwords are never stored in plain text. The application uses `werkzeug.security` with `generate_password_hash` and `check_password_hash` functions.
* **Session Security:** User sessions and cart contents are cryptographically signed on the client side using a secure server key.
* **Routing Context Control (Authorization):** Critical endpoints (like `/add`, `/delete`, `/cart`, `/profile`) are protected. Unauthorized users attempting direct URL access are immediately redirected to the login page.

---

## 📦 Local Deployment & Installation Guide

To run this project locally, ensure you have **Python 3.8+** installed, then follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/szymonpardus1011/FoodGo.git](https://github.com/szymonpardus1011/FoodGo.git)
   cd FoodGo

Install required dependencies:

pip install flask werkzeug

Launch the application server:

python app.py

Open your browser and navigate to: http://127.0.0.1:5000

