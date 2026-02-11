# Learning Management System (LMS)

A comprehensive Django-based Learning Management System for managing students, courses, and educational content with a modern, user-friendly interface.

## 🚀 Features

### Student Management
- **CRUD Operations**: Create, Read, Update, and Delete student records
- **Advanced Search**: Search students by name or phone number
- **Responsive Interface**: Modern Bootstrap-based UI with icons and visual feedback
- **Data Validation**: Form validation with helpful error messages

### Course Platform
- **Course Management**: Create and manage courses with different difficulty levels
- **Category Organization**: Organize courses by categories
- **Publishing Control**: Publish/unpublish courses as needed
- **Pricing Support**: Set course prices with decimal precision

### User Authentication
- **User Registration**: New user signup with profile management
- **Secure Login**: Built-in Django authentication system
- **Profile Management**: Edit user profiles and change passwords
- **Session Management**: Automatic login/logout handling

### Dashboard & Analytics
- **Statistics Overview**: View total students, courses, and users
- **Recent Activity**: Track recently added students
- **Quick Actions**: Fast access to common tasks
- **Visual Indicators**: Color-coded cards and progress indicators

## 🛠️ Technology Stack

- **Backend**: Django 5.1.4
- **Frontend**: Bootstrap 5.3.7 with Bootstrap Icons
- **Database**: SQLite (default, easily configurable)
- **Styling**: Custom CSS with Bootstrap components
- **Icons**: Bootstrap Icons for modern UI elements

## 📁 Project Structure

```
myproject/
├── myapp/                  # Student management app
│   ├── models.py          # Student model
│   ├── views.py           # CRUD views with statistics
│   ├── forms.py           # Student forms
│   └── urls.py            # URL routing
├── CoursePlatform/        # Course management app
│   ├── models.py          # Course model with levels and categories
│   ├── views.py           # Course CRUD operations
│   ├── forms.py           # Course forms
│   └── urls.py            # Course URL routing
├── userAuth/              # User authentication app
│   ├── views.py           # Registration and profile views
│   ├── forms.py           # User forms
│   └── models.py          # User-related models
├── templates/             # HTML templates
│   ├── base.html          # Base template with navigation
│   ├── home.html          # Landing page
│   ├── dashboard.html     # Statistics dashboard
│   ├── CRUD/              # Student management templates
│   ├── CoursePlatform/    # Course templates
│   └── accounts/          # Authentication templates
├── static/                # Static files (CSS, JS, Images)
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project**
   ```bash
   cd myproject
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## 📱 Usage Guide

### Navigation
- **Home**: Overview of the system with quick access to main features
- **Students**: Manage student records with search and filter options
- **Courses**: Create and manage educational courses
- **Dashboard**: View system statistics and recent activity

### Student Management
1. **Add Students**: Click "Add New Student" from any student page
2. **Search Students**: Use the search bar to find students by name or phone
3. **Edit Students**: Click the edit icon next to any student record
4. **Delete Students**: Click the delete icon (with confirmation)

### Course Management
1. **Create Courses**: Add new courses with title, description, and pricing
2. **Set Difficulty**: Choose from Beginner, Intermediate, or Advanced levels
3. **Organize by Category**: Group courses by subject or topic
4. **Publish Control**: Toggle course visibility

### User Accounts
1. **Register**: Create new user accounts from the registration page
2. **Login**: Access personalized features with user authentication
3. **Profile**: Update user information and change passwords
4. **Logout**: Secure session termination

## 🎨 UI/UX Features

### Modern Design
- **Bootstrap 5**: Responsive, mobile-first design
- **Bootstrap Icons**: Consistent iconography throughout the app
- **Color-coded Elements**: Visual hierarchy with meaningful colors
- **Card-based Layout**: Clean, organized content presentation

### User Experience
- **Intuitive Navigation**: Clear menu structure with icons
- **Search & Filter**: Easy content discovery
- **Form Validation**: Real-time feedback and error handling
- **Responsive Design**: Works on desktop, tablet, and mobile

### Accessibility
- **Screen Reader Support**: Proper ARIA labels and semantic HTML
- **Keyboard Navigation**: Full keyboard accessibility
- **High Contrast**: Clear visual distinction between elements
- **Helpful Text**: Form hints and validation messages

## 🔧 Configuration

### Database Settings
The application uses SQLite by default. To use a different database, update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # or mysql, etc.
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Static Files
Static files are served from the `static/` directory. For production, configure proper static file serving.

### Time Zone
The application is configured for Asia/Kolkata timezone. Update in `settings.py` if needed:

```python
TIME_ZONE = 'Your/Timezone'
```

## 📊 Models Overview

### Student Model
```python
class Students(models.Model):
    firstname = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, null=True, blank=True)
    phone = models.IntegerField()
```

### Course Model
```python
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructor = models.CharField(max_length=120)
    level = models.CharField(max_length=20, choices=LEVELS)
    category = models.CharField(max_length=100, blank=True)
    is_published = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # ... additional fields
```

## 🚀 Deployment

### Production Checklist
1. Set `DEBUG = False` in settings.py
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving (WhiteNoise or CDN)
4. Configure email backend for password resets
5. Set secure secret key
6. Enable HTTPS
7. Configure allowed hosts

### Environment Variables
Consider using environment variables for sensitive settings:
- `SECRET_KEY`
- `DATABASE_URL`
- `DEBUG`
- `ALLOWED_HOSTS`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

For questions or issues:
1. Check the Django documentation
2. Review the code comments
3. Create an issue in the repository
4. Contact the development team

## 🔄 Version History

### v1.0.0 (Current)
- Initial release with student and course management
- Modern Bootstrap UI with responsive design
- User authentication and profile management
- Dashboard with statistics and analytics
- Search and filter functionality
- Form validation and error handling

---

**Built with ❤️ using Django and Bootstrap**
# #   R e p o s i t o r y   S t a t u s 
 
 
