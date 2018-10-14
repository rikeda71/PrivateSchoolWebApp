from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User, PDFFile, Shift


class MyUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', )


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('last_name', 'first_name')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser', 'is_active')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('email', 'last_name', 'first_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'last_name', 'first_name')
    ordering = ('email',)
    filter_horizontal = ()


class PDFFileAdmin(admin.ModelAdmin):

    field_sets = (
        (None, {'fields': ('id', 'attach', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('attach', 'created_at'),
        }),
    )

    list_display = ('id', 'attach', 'created_at')
    list_display_links = ('id', 'created_at')
    search_fields = ('created_at', )


class ShiftAdmin(admin.ModelAdmin):

    field_sets = (
        (None, {'fields': ('pdf_id', 'user_id', 'day')}),
        (_('Personal info'), {'fields': ('segment', 'student_name', 'subject_name', 'student_grade')}),
    )

    list_display = ('user_id', 'day', 'segment', 'subject_name', 'student_grade')
    list_display_links = ('user_id', 'day', 'segment')
    search_fields = ('segment', 'student_name', 'subject_name', 'student_grade')


admin.site.register(User, MyUserAdmin)
admin.site.register(PDFFile, PDFFileAdmin)
admin.site.register(Shift, ShiftAdmin)
