# Smart Bank 360 – Backend

This is the **Django + Django REST Framework backend** for [Smart Bank 360](https://github.com/collins965/smart-bank-API.git) — a full-stack digital banking platform built for the Kenyan market.

The backend handles authentication, transactions, M-Pesa deposits, loan management, investment tracking, and all business logic for secure digital banking.


## Tech Stack

-  Python 3.x
-  Django 5+
-  Django REST Framework (DRF)
-  Simple JWT for Authentication
-  PostgreSQL or SQLite
-  Python-Decouple for environment management
-  CORS Headers
-  M-Pesa Daraja Integration (C2B STK Push)


## Folder Structure
backend/
├── smartbank/ # Project settings
├── accounts/ # User auth, KYC
├── core/ # Balances, transfers, transactions
├── loans/ # Loan requests and repayments
├── investments/ # Stock/crypto tracking
├── savings/ # Smart saving vaults
├── mpesa/ # M-Pesa API integration
├── notifications/ # Alerts and messages
├── admin_panel/ # Admin-only APIs
├── static/ # Static files
├── media/ # Uploaded media
├── manage.py
└── requirements.txt
