from django.contrib import admin
from auroUser.models import User, BookAppointment, RatingAndReviews, Queries

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'phone']
    search_fields = ['email', 'name', 'phone']

class BookAppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'shop', 'service', 'appointment_date', 'status']
    search_fields = ['user', 'shop', 'service', 'appointment_date', 'status']

class RatingAndReviewsAdmin(admin.ModelAdmin):
    list_display = ['user', 'shop', 'rating', 'review']
    search_fields = ['user', 'shop', 'rating', 'review']

class QueriesAdmin(admin.ModelAdmin):
    list_display = ['user', 'shop', 'question', 'response']
    search_fields = ['user', 'shop', 'question', 'response']

admin.site.register(User, UserAdmin)
admin.site.register(BookAppointment, BookAppointmentAdmin)
admin.site.register(RatingAndReviews, RatingAndReviewsAdmin)
admin.site.register(Queries, QueriesAdmin)
