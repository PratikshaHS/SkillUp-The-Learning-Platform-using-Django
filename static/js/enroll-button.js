document.addEventListener('DOMContentLoaded', function() {
    // Initialize Stripe
    const stripePublicKey = document.body.getAttribute('data-stripe-public-key');
    if (!stripePublicKey) {
        console.error('Stripe public key is missing');
        return;
    }
    
    const stripe = Stripe(stripePublicKey);
    let elements;
    
    // Initialize Stripe Elements when needed
    function initializeStripeElements() {
        if (!elements) {
            elements = stripe.elements();
            // You can initialize card element here if needed
        }
    }
    
    // Handle paid course enrollment
    const enrollButton = document.getElementById('enrollButton');
    if (enrollButton) {
        enrollButton.addEventListener('click', handleEnrollClick);
    }
    
    // Handle free course enrollment
    const enrollFreeButton = document.getElementById('enrollFreeButton');
    if (enrollFreeButton) {
        enrollFreeButton.addEventListener('click', handleEnrollClick);
    }
    
    async function handleEnrollClick(e) {
        const button = e.currentTarget;
        const isAuthenticated = button.getAttribute('data-authenticated') === 'true';
        const courseId = button.getAttribute('data-course-id');
        const isFreeCourse = button.id === 'enrollFreeButton';
        
        // If not authenticated, let the default login modal behavior work
        if (!isAuthenticated) {
            return;
        }
        
        e.preventDefault();
        
        // Show loading state
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
        
        try {
            // For free courses, just enroll directly
            if (isFreeCourse) {
                await enrollInCourse(courseId);
                return;
            }
            
            // For paid courses, redirect to payment page
            window.location.href = `/payment/?course_id=${courseId}`;
            
        } catch (error) {
            console.error('Enrollment error:', error);
            showError('Enrollment failed: ' + (error.message || 'An error occurred'));
            button.disabled = false;
            button.innerHTML = originalText;
        }
    }
    
    async function enrollInCourse(courseId) {
        try {
            const response = await fetch(`/courses/enroll/${courseId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || 'Failed to enroll in course');
            }
            
            const data = await response.json();
            
            if (data.success) {
                window.location.href = data.redirect_url || `/courses/${courseId}/`;
            } else {
                throw new Error(data.message || 'Enrollment failed');
            }
        } catch (error) {
            console.error('Enrollment error:', error);
            throw error;
        }
    }
    
    function getCsrfToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }
    
    function showError(message) {
        // Remove any existing error messages
        const existingError = document.getElementById('enroll-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Create and show new error message
        const errorDiv = document.createElement('div');
        errorDiv.id = 'enroll-error';
        errorDiv.className = 'alert alert-danger mt-3';
        errorDiv.textContent = message;
        
        // Insert after the button
        const button = document.querySelector('.enroll-btn');
        if (button) {
            button.parentNode.insertBefore(errorDiv, button.nextSibling);
            
            // Scroll to the error message
            errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            // Fallback to alert if we can't find the button
            alert(message);
        }
    }
});
