# Blog Project with Django REST Framework

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Usage](#usage)
6. [API Endpoints](#api-endpoints)
7. [Database Schema](#database-schema)
8. [Contributing](#contributing)
9. [License](#license)

---

## Overview

This project is a **blogging platform** built using Django and Django REST Framework (DRF). It allows users to create, read, update, and delete blog posts, as well as interact with posts through voting (upvote/downvote) and commenting. The API is designed to be RESTful and supports modern web applications.

---

## Features

- **Blog Management**:
  - Create, update, delete, and retrieve blog posts.
  - Each blog post includes a title, description, author, and comments.

- **Voting System**:
  - Users can upvote or downvote blog posts.
  - Toggle votes between upvote and downvote.
  - Prevent duplicate votes from the same user.

- **Commenting System**:
  - Users can add comments to blog posts.
  - Nested replies for comments (optional, depending on implementation).

- **Pagination**:
  - Paginate comments and blog lists for better performance.

- **Authentication**:
  - User authentication using `User` model in the users app.
  - Only authenticated users can vote, comment, or create/update/delete blogs.

- **Documentation**:
  - API documentation generated using drf-spectacular.

---

## Prerequisites

Before running this project, ensure you have the following installed:

- Python 3.10.12+ ([Download Python](https://www.python.org/downloads/))
- pip (comes with Python)
- virtualenv (optional but recommended)
- PostgreSQL or another supported database (SQLite is used by default for development)
- Git ([Download Git](https://git-scm.com/))

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mohammadnaderinasab01/django_practice_project_blog_with_drf.git
   cd django_practice_project_blog_with_drf

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Set Up Environment Variables**:
Create a .env file in the root directory and add the following variables:
   ```bash
   DJANGO_SECRET_KEY=your_secret_key_here
   ```

5. **Apply migrations**:
   ```bash
   python manage.py migrate

6. **Run the Development Server**:
   ```bash
   python manage.py runserver
