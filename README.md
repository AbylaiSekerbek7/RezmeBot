# RezMe — Telegram Booking Bot (ReserveMe)

RezMe is a Telegram bot that helps users **book venues in 1–2 minutes** (restaurants/cafés, karaoke, bowling, PlayStation clubs, lounge bars, etc.) without phone calls.  
Users select a category or area, choose date/time/people count, add a comment, and receive a curated list of venues with contact details.

> 🇷🇺 *“RezMe — твой персональный гид по бронированию заведений в один клик”*

---

## ✨ Key Features

### ✅ For Users
- **Booking flow** with inline buttons (category/area → date → time → people → comment)
- **Interactive calendar** for choosing the date
- Venue cards: **name, category, area, address, phone, Instagram link**
- “All venues” list from the internal database
- Simple and fast UX: works well both on **mobile and desktop Telegram**

### 🛠 Admin Panel
- `/admin` entry (admin-only)
- Quick access to:
  - **Statistics** (users, bookings, reviews)
  - **Users list**
  - **Bookings list**
  - **Reviews**
  - **Venues management** (add/remove venues)

### 🤖 Mini AI Assistant (In-chat Helper)
- Built-in assistant mode for answering user questions like:
  - “How to book a table?”
  - “What does this bot do?”
- Returns step-by-step instructions inside the chat

### ☁️ Deployment
- Deployed to **Northflank Cloud**
- Environment-based configuration (token, admins, DB settings)

---

## 🧭 How Booking Works (User Flow)

1. User clicks **“🔔 Забронировать”**
2. Chooses a **category** or **area**
3. Selects **date** (calendar), **time**, and **people count**
4. Adds a **comment** (optional: budget / preferences / occasion)
5. Bot shows **venue options** and collects booking details for confirmation

---

## 🧱 Tech Stack

- **Python 3.12**
- **Telegram Bot API** (Python bot framework — see `requirements.txt`)
- **SQLite** (`rezme.db`) + SQL schema in `models.sql`
- Modular project structure: handlers, keyboards, DB layer, config
- **Northflank** for deployment

> 📌 Exact libraries are listed in [`requirements.txt`](./requirements.txt)

---

## 📁 Demo

# Functional:

<img width="1421" height="828" alt="image" src="https://github.com/user-attachments/assets/520725a3-48f4-417c-ac61-9b9c37473094" />

<img width="1438" height="983" alt="image" src="https://github.com/user-attachments/assets/f603b998-9367-48d6-9a9f-62177853cea8" />

<img width="1434" height="982" alt="image" src="https://github.com/user-attachments/assets/4cbcf26c-299e-4bb0-acb4-b808f4b98a2e" />

<img width="1437" height="994" alt="image" src="https://github.com/user-attachments/assets/efedb01a-8926-4979-bddb-0aebfa5f066f" />

<img width="1438" height="989" alt="image" src="https://github.com/user-attachments/assets/fd107e46-8c93-4421-9b45-aa4c83098692" />

<img width="1433" height="984" alt="image" src="https://github.com/user-attachments/assets/f869c4e4-748a-4d5c-b6df-1bf321df32ca" />

<img width="1435" height="993" alt="image" src="https://github.com/user-attachments/assets/d86beec7-0d82-4766-ba6b-d0aa3db5d06e" />

<img width="1432" height="984" alt="image" src="https://github.com/user-attachments/assets/32ac5403-5867-4c67-874e-806b05ba8c70" />

# AI Assitant

<img width="1429" height="990" alt="image" src="https://github.com/user-attachments/assets/92d4ecb6-6262-4640-a692-cb7034ec33e9" />

# Admin Panel

<img width="1436" height="1029" alt="image" src="https://github.com/user-attachments/assets/7e2e28d0-8f3b-4476-971d-2aaf01d456b6" />

# All functions

<img width="1431" height="984" alt="image" src="https://github.com/user-attachments/assets/fe3394d1-dda1-41cf-aca3-f8b746e2caa2" />




