# AuroNow - Salon & Barber Shop Booking Platform

## 🚀 Project Overview

AuroNow is a web-based platform designed to streamline salon and barber shop bookings, providing real-time scheduling, personalized recommendations, and business analytics for shop owners.

## 📂 Project Structure

```
AuroNow/
│── manage.py                # Django management script
│── requirements.txt         # Dependencies
│── .gitignore               # Files to ignore in Git
│── README.md                # Project documentation
│
├── AuroNow/                 # Main project configuration
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL routing
│
├── authentication/          # User authentication
├── shops/                   # Salon & barber shop management
├── bookings/                # Appointment system
├── reviews/                 # Ratings & reviews
├── dashboard/               # Shop owner analytics (if added)
│
├── static/                  # CSS, JS, images
├── templates/               # HTML templates
├── media/                   # User-uploaded files
```

---

## 🛠 Installation Guide

Follow these steps to set up AuroNow on your local machine.

### **1️⃣ Clone the Repository**

```bash
git clone <repository-url>
cd AuroNow
```

### **2️⃣ Create a Virtual Environment**

```bash
python -m venv env
```

### **3️⃣ Activate the Virtual Environment**

- **Windows**:
  ```bash
  env\Scripts\activate
  ```
- **Mac/Linux**:
  ```bash
  source env/bin/activate
  ```

### **4️⃣ Install Dependencies**

```bash
pip install -r requirements.txt
```

### **5️⃣ Run Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

### **6️⃣ Create a Superuser (Optional, for Admin Panel)**

```bash
python manage.py createsuperuser
```

### **7️⃣ Run the Server**

```bash
python manage.py runserver
```

Access the site at [**http://127.0.0.1:8000/**](http://127.0.0.1:8000/)

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

Happy Coding! 🚀

