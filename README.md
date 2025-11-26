# 🎵 RAGAM — Music Streaming Platform
A full-stack music streaming web application with multi-user roles, playlist management, album creation, and an admin-controlled content management system.

---

## 🚀 Overview
**RAGAM** is a feature-rich music streaming platform built during Jan–Feb 2024.  
The platform supports **three roles** — **Users, Creators, and Admins** — each with dedicated features.  
It allows streaming, playlist creation, song ratings, album uploads, and full moderation capabilities.

The project is designed using **Flask** and **Jinja2**, backed by **SQLite** with **SQLAlchemy ORM**, ensuring efficient CRUD operations and a clean, modular architecture.

---

## 🧩 Features

### 👤 User Features
- Create and manage playlists  
- Stream songs with chunked file delivery  
- Rate songs  
- Explore music uploaded by creators  
- Secure login/signup with Flask-Login  

### 🎙️ Creator Features
- Upload songs and albums  
- Manage uploaded songs  
- Preview user interactions  

### 🛠️ Admin Features
- Approve/reject creator uploads  
- Manage users and content  
- Delete inappropriate songs/albums  
- View overall platform statistics  

---

## 🏗️ Tech Stack

### **Backend**
- Python (Flask)
- Jinja2 templating
- SQLite database
- SQLAlchemy ORM
- Flask-Login
- Werkzeug password hashing

### **Frontend**
- HTML, CSS
- Bootstrap
- Jinja2 dynamic rendering

