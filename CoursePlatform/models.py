from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class CourseVideo(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    youtube_url = models.URLField(help_text="Enter YouTube video URL")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.title} - {self.course.title}"

    def get_embed_url(self):
        """Convert YouTube URL to embed URL"""
        from urllib.parse import urlparse, parse_qs
        url_data = urlparse(self.youtube_url)
        if 'youtube.com' in url_data.netloc:
            if url_data.path == '/watch':
                video_id = parse_qs(url_data.query).get('v', [''])[0]
                return f"https://www.youtube.com/embed/{video_id}"
        elif 'youtu.be' in url_data.netloc:
            video_id = url_data.path[1:]
            return f"https://www.youtube.com/embed/{video_id}"
        return self.youtube_url


class Course(models.Model):
    LEVELS = [
        ("BEGINNER", "Beginner"),
        ("INTERMEDIATE", "Intermediate"),
        ("ADVANCED", "Advanced"),
    ]

    DURATION_CHOICES = [
        (4, "4 Weeks"),
        (8, "8 Weeks"),
        (12, "12 Weeks"),
        (16, "16 Weeks"),
        (24, "6 Months"),
        (52, "1 Year"),
    ]

    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=300, blank=True, help_text="A short description (max 300 characters)")
    description = models.TextField(blank=True, help_text="Detailed course description")
    what_youll_learn = models.TextField(blank=True, help_text="What students will learn in this course")
    requirements = models.TextField(blank=True, help_text="Prerequisites or requirements for this course")
    
    instructor = models.CharField(max_length=120, default="Your Name")
    instructor_bio = models.TextField(blank=True, help_text="Instructor's bio and qualifications")
    
    level = models.CharField(max_length=20, choices=LEVELS, default="BEGINNER")
    category = models.CharField(max_length=100, blank=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True, choices=DURATION_CHOICES, help_text="Course duration in weeks")

    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    promo_video = models.URLField(blank=True, help_text="Link to course promo video (YouTube/Vimeo)")
    
    students_enrolled = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
        
    def get_duration_display(self):
        if not self.duration:
            return "Self-paced"
        if self.duration < 12:
            return f"{self.duration} Week{'s' if self.duration > 1 else ''}"
        elif self.duration == 12:
            return "3 Months"
        elif self.duration == 24:
            return "6 Months"
        elif self.duration == 52:
            return "1 Year"
        return f"{self.duration} Weeks"
        
    def get_discount_percentage(self):
        if self.discount_price and self.price:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
        
        # Update course enrollment count
        self.course.students_enrolled = self.course.enrollments.filter(status='active').count()
        self.course.save()
