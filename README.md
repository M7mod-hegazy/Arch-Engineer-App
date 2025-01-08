# My Django Project

## Overview
This is a Django project configured to use a PostgreSQL database. It is designed to be accessible from multiple PCs on different networks.

## Prerequisites
- Python 3.x
- PostgreSQL
- pip

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd my_django_project
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Configure the PostgreSQL database in `my_django_project/settings.py`:
   - Update the `DATABASES` setting to include your PostgreSQL database credentials.

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser (optional):
   ```
   python manage.py createsuperuser
   ```

## Running the Project
To start the development server, run:
```
python manage.py runserver 0.0.0.0:8000
```
This will allow access from other PCs on different networks.

## Accessing the Project
Open a web browser and navigate to:
```
http://<your-ip-address>:8000
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.