from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .models import Course, CourseVideo
from django.forms import inlineformset_factory

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            # Basic Information
            "title", "short_description", "description", "category",
            # Instructor
            "instructor", "instructor_bio",
            # Course Details
            "level", "duration", "start_date", "end_date",
            # Pricing
            "price", "discount_price",
            # Media
            "thumbnail", "promo_video",
            # Content
            "what_youll_learn", "requirements",
            # Status
            "is_published", "is_featured"
        ]
        widgets = {
            # Basic Information
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g., Complete Python Bootcamp"
            }),
            "short_description": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "A brief description of your course",
                "maxlength": "300"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Detailed course description"
            }),
            "category": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g., Web Development, Data Science"
            }),
            
            # Instructor
            "instructor": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Instructor's name"
            }),
            "instructor_bio": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Tell students about yourself and your experience"
            }),
            
            # Course Details
            "level": forms.Select(attrs={"class": "form-select"}),
            "duration": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
                "min": date.today().isoformat()
            }),
            "end_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            
            # Pricing
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            "discount_price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": 0,
                "placeholder": "0.00"
            }),
            
            # Media
            "thumbnail": forms.FileInput(attrs={
                "class": "form-control",
                "accept": "image/*"
            }),
            "promo_video": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://www.youtube.com/watch?v=..."
            }),
            
            # Content
            "what_youll_learn": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "List what students will learn in this course (one per line)"
            }),
            "requirements": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "List any requirements or prerequisites (one per line)"
            }),
            
            # Status
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        help_texts = {
            "short_description": "This appears in course cards and search results (max 300 characters)",
            "thumbnail": "Recommended size: 1280x720px (16:9 aspect ratio)",
            "promo_video": "A short video introducing your course (YouTube or Vimeo URL)",
            "what_youll_learn": "Enter each item on a new line",
            "requirements": "Enter each requirement on a new line"
        }

    def clean_short_description(self):
        short_description = self.cleaned_data.get('short_description', '').strip()
        if len(short_description) > 300:
            raise ValidationError("Short description cannot exceed 300 characters.")
        return short_description
        
    def clean_price(self):
        price = self.cleaned_data.get('price', 0)
        if price < 0:
            raise ValidationError("Price cannot be negative.")
        return price
        
    def clean_discount_price(self):
        discount_price = self.cleaned_data.get('discount_price')
        if discount_price is not None and discount_price < 0:
            raise ValidationError("Discount price cannot be negative.")
        return discount_price

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < date.today():
            raise ValidationError("Start date cannot be in the past.")
        return start_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        price = cleaned_data.get('price', 0)
        discount_price = cleaned_data.get('discount_price')

        # Validate dates
        if start_date and end_date:
            if end_date < start_date:
                self.add_error('end_date', "End date must be after start date.")
                
        # Validate pricing
        if discount_price is not None and price > 0 and discount_price >= price:
            self.add_error('discount_price', "Discount price must be lower than the regular price.")
                
        # Ensure required fields for published courses
        if cleaned_data.get('is_published') and not self.instance.is_published:
            required_fields = [
                'short_description', 'description', 'what_youll_learn',
                'requirements', 'instructor_bio', 'category', 'thumbnail'
            ]
            
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required when publishing the course.")
        
        return cleaned_data


class CourseVideoForm(forms.ModelForm):
    class Meta:
        model = CourseVideo
        fields = ['title', 'youtube_url', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Video Title'
            }),
            'youtube_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 1
            })
        }
        help_texts = {
            'youtube_url': 'Enter a valid YouTube URL (e.g., https://www.youtube.com/watch?v=...)'
        }

    def clean_youtube_url(self):
        url = self.cleaned_data.get('youtube_url')
        if url:
            if 'youtube.com' not in url and 'youtu.be' not in url:
                raise forms.ValidationError('Please enter a valid YouTube URL')
        return url


# Create a formset for course videos
CourseVideoFormSet = inlineformset_factory(
    Course, 
    CourseVideo, 
    form=CourseVideoForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)
