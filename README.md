# AuroNow - Salon & Barber Shop Booking Platform

AuroNow is a **web-based booking platform** for salons and barber shops. It allows **shop owners** to manage their business, services, and bookings, while **customers** can book appointments, leave reviews, and ask queries.

---

## 📁 Project Structure

```
AuroNow/                     # Root project directory
│── manage.py                # Django management script
│── requirements.txt         # Dependencies (Django, etc.)
│── db.sqlite3               # SQLite Database
│── README.md                # Project documentation
│── .gitignore               # Git ignored files
│── env/                     # Virtual environment (excluded from Git)
│
├── AuroNow/                 # Main Django project settings
│   │── __init__.py          
│   │── settings.py          # Project settings
│   │── urls.py              # Main URL routing
│   │── asgi.py              
│   │── wsgi.py              
│
├── shop/                     # Shop Owner Side
│   │── __init__.py      
│   │── models.py             # Models for shop owner, services, bookings, staff
│   │── views.py              # Views for managing shop operations
│   │── urls.py               # URL routing for shop owner features
│   │── admin.py              # Admin configurations
│   │── tests.py              
│   └── migrations/           # Database migrations for shop
│
├── user/                     # Customer Side
│   │── __init__.py      
│   │── models.py             # Models for customers, queries, reviews, booking
│   │── views.py              # Views for user operations
│   │── urls.py               # URL routing for users
│   │── admin.py              # Admin configurations
│   │── tests.py              
│   └── migrations/           # Database migrations for user
│
├── static/                   # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   ├── images/
│
├── templates/                # HTML templates for rendering pages
│   ├── base.html             # Base template
│   ├── shop_dashboard.html   # Owner Dashboard
│   ├── user_home.html        # Customer Frontend
│   ├── booking.html          # Booking Page
│   ├── reviews.html          # Reviews Page
│
└── media/                    # User-uploaded media (e.g., shop images)
```

---

## 📌 Database Structure

### 📍 `shop` (Owner Side)
- **ShopOwner** → Stores shop owner details  
- **ServiceCategory** → Defines categories of services  
- **Service** → Lists available services with price & duration  
- **ShopImage** → Stores up to 5 shop images  
- **Staff** → Keeps staff details  
- **Slot** → Defines time slots for booking appointments  
- **FAQ** → Stores frequently asked questions  
- **Advertisement** → Manages shop promotions & payment  

### 📍 `user` (Customer Side)
- **User** → Stores customer details  
- **BookAppointment** → Handles customer bookings  
- **RatingAndReviews** → Stores customer ratings & feedback  
- **Queries** → Tracks and answers customer queries  

---
## 📌 Features

✅ **For Shop Owners**
- Manage shop details  
- Add services, categories & pricing  
- Upload shop images  
- Set available slots for appointments  
- Manage staff  
- Respond to customer queries  
- Run advertisements & promotions  

✅ **For Customers**
- Book appointments  
- Search & filter services  
- Rate & review shops  
- Ask queries to shop owners  
- Manage past & upcoming bookings
---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/AuroNow.git
cd AuroNow
```

### 2️⃣ Create & Activate Virtual Environment
```bash
python -m venv env
env\Scripts\activate  # Windows
source env/bin/activate  # macOS/Linux
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Apply Migrations
```bash
python manage.py makemigrations shop
python manage.py makemigrations user
python manage.py migrate
```

### 5️⃣ Create Superuser
```bash
python manage.py createsuperuser
```
Follow the prompts to enter:
- Username
- Email
- Password

### 6️⃣ Run the Server
```bash
python manage.py runserver
```
Go to **http://127.0.0.1:8000/** in your browser.

---

## 📥 Pulling New Updates & Working on Features

When a new update is pushed, follow these steps to sync your local code:

### **1️⃣ Pull Latest Changes**

```bash
git pull origin main
```

### **2️⃣ Activate Virtual Environment**

```bash
source env/bin/activate  # Mac/Linux
env\Scripts\activate  # Windows
```

### **3️⃣ Install New Dependencies (if any)**

```bash
pip install -r requirements.txt
```

### **4️⃣ Apply Database Migrations**

```bash
python manage.py migrate
```

### **5️⃣ Run the Development Server**

```bash
python manage.py runserver
```

---

## 🔥 Contributing to AuroNow

To work on a new feature:

1️⃣ **Create a new branch:**

```bash
git checkout -b feature-branch-name
```

2️⃣ **Make changes & commit:**

```bash
git add .
git commit -m "Added new feature"
```

3️⃣ **Push to GitHub:**

```bash
git push origin feature-branch-name
```

4️⃣ **Create a Pull Request on GitHub** and request a review.

---

## 📌 Notes

- Always pull the latest changes before starting new work.
- Use branches for new features to avoid conflicts.
  
---
