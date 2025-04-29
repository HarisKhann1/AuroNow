from django.contrib import admin
from shops.models import ShopOwner, ServiceCategory, Service, ShopImage, Staff, Slot, FAQ, Advertisement, ShopTiming, PasswordResetToken


class ShopOwnerAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'shop_name', 'phone', 'address', 'password', 'latitude', 'longitude')
    search_fields = ('email', 'name', 'shop_name', 'phone')

class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('shop','name')
    search_fields = ('name'),
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('shop','category', 'name', 'price', 'duration')
    search_fields = ('shop', 'name')

class ShopImageAdmin(admin.ModelAdmin):
    list_display = ('shop', 'shop_image')
    search_fields = ('shop_image',)

class StaffAdmin(admin.ModelAdmin):
    list_display = ('phone', 'shop', 'name', 'role')
    search_fields = ('shop', 'name', 'role')

class SlotAdmin(admin.ModelAdmin):
    list_display = ('id','shop', 'date', 'start_time', 'end_time', 'is_booked')
    search_fields = ('shop', 'service', 'date', 'is_booked')

class FAQAdmin(admin.ModelAdmin):
    list_display = ('shop', 'question', 'answer')
    search_fields = ('shop', 'question', 'answer')

class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('shop', 'amount_paid', 'start_date', 'end_date')
    search_fields = ('shop'),

admin.site.register(ShopOwner, ShopOwnerAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ShopImage, ShopImageAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Slot, SlotAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(Advertisement, AdvertisementAdmin)
admin.site.register(ServiceCategory, ServiceCategoryAdmin)
admin.site.register(ShopTiming)
admin.site.register(PasswordResetToken)
