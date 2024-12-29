# Online Library Management System

## Project Overview

This is a web-based library management system built with Django, featuring separate modules for administrators and students. The system allows for efficient management of books, student accounts, and borrowing processes.

## Features

### Admin Module

- **Admin Dashboard:**
  - View Borrowed books
  - View All Books
  - View All Users
  - Track book status and availability

- **Book Management:**
  - Add new books with details (title, author, genre, etc.)
  - Update existing book information
  - Delete books from the system
  - Upload book cover images

- **Student Management:**
  - Search students by their student ID
  - View student details and borrowing history
  - Monitor student activities

- **Password Change:**
  - Admin can change their own password
  - Secure authentication system

- **Authorization:**
  - Role-based access control
  - Only admin has the authority to perform administrative tasks

### Student Module

- **User Registration:**
  - Students can create their accounts
  - Email verification system
  - Secure password management

- **Browse Books:**
  - View all available books
  - Search books by title, author, or genre
  - View detailed book information
  - See book availability status

- **Borrow Books:**
  - Request to borrow available books
  - Set borrowing duration
  - Receive confirmation notifications

- **User Dashboard:**
  - Personalized student dashboard
  - View currently borrowed books
  - Track return dates
  - Return books to shelf functionality
  - Borrowing history

- **Profile Management:**
  - Update personal information
  - Change password
  - View account status

- **Borrowed Book Details:**
  - View detailed borrowing information
  - Check return deadlines
  - Extension requests (if implemented)

## Technologies Used

- **Backend:** Django 4.2.4
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, Bootstrap
- **Authentication:** Django Authentication System
- **Additional:** Jazzmin (Admin Interface)

## Installation Guide

### Prerequisites

1. Python (3.8 or higher)
2. PostgreSQL
3. pip (Python package manager)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd library-management-system
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure PostgreSQL**
   - Create a new PostgreSQL database
   - Update database settings in `settings.py`

5. **Configure Environment Variables**
   Create a `.env` file in the project root:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DB_NAME=your-db-name
   DB_USER=your-db-user
   DB_PASSWORD=your-db-password
   DB_HOST=localhost
   DB_PORT=5432
   ```

6. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Create Required Folders**
   ```bash
   mkdir media
   mkdir media/books/images
   ```

9. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

10. **Access the Application**
    - Main site: http://127.0.0.1:8000/
    - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### Admin Access
1. Login to admin panel using superuser credentials
2. Manage books, users, and borrowing records
3. Monitor system activities

### Student Access
1. Register a new account
2. Login with credentials
3. Browse and borrow books
4. Manage profile and borrowed books

## Project Structure
```
library_management/
├── books/              # Book management app
├── students/           # Student management app
├── genre/              # Genre management app
├── status/            # Book status management
├── media/             # Media files storage
│   └── books/images/  # Book cover images
├── static/            # Static files
├── templates/         # HTML templates
└── LMS/               # Main project directory
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django Documentation
- Bootstrap Documentation
- PostgreSQL Documentation
- Jazzmin Theme Contributors