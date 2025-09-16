# TARUMT Student Assistant App

## 📑 Table of Contents
- [Project Overview](#-project-overview)  
- [Environment Setup](#-environment-setup)  
- [Database Setup](#-database-setup)  
- [Running the Application](#-running-the-application)  
- [Login Information](#-login-information)  
- [Features](#-features)  
- [User Manual](#-user-manual-summary)  
- [Technology Stack](#-technology-stack)  
- [Future Improvements](#-future-improvements)  
- [License](#-license)  
- [Authors](#-authors)  

---

## 📌 Project Overview
The TARUMT Student Assistant App is a desktop application built using **Python (PyQt5)**. It provides TARUMT students with essential academic tools in one platform:
- **Note Organizer** – manage personal notes.  
- **Discussion Room Booking** – book and manage study rooms.  
- **Academic Tools** – calculate GPA, set academic goals, and review history.  

---

## ⚙️ Environment Setup

### Prerequisites
Make sure the following are installed:
- Python 3.7 or higher  
- `pip` (Python package manager, comes with Python)  

### Installation Steps
1. Clone or download the project.  
2. Install required dependencies:  
   ```bash
   pip install PyQt5
   ```  

---

## 🗄️ Database Setup
The system uses **SQLite** for storing users, notes, bookings, and calculations.

- To **initialize the database**, run:
  ```bash
  python database/init_db.py
  ```
  ⚠️ **Warning**: Running this script will reset all existing data.  

- To **view the database**, you can use:
  - [DB Browser for SQLite](https://sqlitebrowser.org/)  
  - or an SQLite extension in your code editor (e.g., VS Code).  

---

## 🚀 Running the Application
After setup, start the application with:
```bash
python main.py
```

---

## 🔑 Login Information
Sample accounts for testing:

- **Student ID:** 24WMD0624 | **Name:** Eun Eun Bond | **Password:** pass123  
- **Student ID:** 24WMD0345 | **Name:** Yu Yu Bond | **Password:** abc456  
- **Student ID:** 24WMD0188 | **Name:** Tong Tong Bond | **Password:** 123456  

---

## 📚 Features
- **Note Organizer:** Create and manage personal study notes.  
- **Room Booking:** Book discussion rooms, check availability, and cancel bookings.  
- **Academic Tools:** GPA calculator, Goal calculator, History, and Grading Scheme.  
- **Secure Login:** Ensures data privacy with Student ID authentication.  

---

## 📖 User Manual (Summary)

### 1. Login
- Enter **Student ID** and **Password** from the sample accounts above.  
- Example: `24WMD0188` / `123456`.  

### 2. Main Dashboard
- Access **Note Organizer**, **Room Booking**, **Academic Tools**, and **Q&A (coming soon)**.  
- Use the **☰ Slide Menu** for quick navigation.  

### 3. Note Organizer
- Create, edit, and delete personal study notes.

### 4. Room Booking
- **My Bookings:** View or cancel your own reservations.  
- **New Booking:** Select room, date, time, student list, and submit.  
- **Timetable:** Check availability (green = available, red = booked).  
- **Guidelines:** Read rules and policies.  

### 5. Academic Tools
- **GPA Calculator:** Enter courses, credits, and grades → auto-calculate GPA & CGPA.  
- **Goal Calculator:** Find required GPA to reach a target CGPA.  
- **View History:** See past calculations & details.  
- **Grading Scheme:** Reference table for marks → grades → quality points.  

### 6. Slide Menu (☰)
- **Home:** Return to dashboard.  
- **Notes:** Manage notes.  
- **Booking Guidelines:** View booking rules.  
- **My Bookings:** View history / cancel.  
- **Logout:** Sign out.  

---

## 🛠️ Technology Stack
- **Python 3.7+** – Core programming language  
- **PyQt5** – GUI framework for building the interface  
- **SQLite** – Database for storing notes, bookings, and GPA calculations  

---

## 🚀 Future Improvements
- **Q&A Section:** Currently under development  
- **Dark Mode:** Provide a modern theme for better user experience  
- **Cloud Sync:** Allow syncing notes and bookings across devices  
- **Enhanced Security:** Add password reset and encryption features  

---

## 📄 License
This project is created for **academic purposes at TARUMT**.  
Not intended for commercial distribution.  

---

## 👥 Authors
- Lai Jia Tong (24WMD03620)  
- Chong Zhi Yi (24WMD03561)  
- Chong Wei Ni (24WMD03850)  
