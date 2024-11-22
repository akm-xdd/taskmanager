# task_app/admin.py
from django.contrib import admin
from .models import Task, Invitation
from django.core.mail import send_mail
from decouple import config

class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'invited_by', 'created_at', 'accepted')
    actions = ['send_invitations']

    def send_invitations(self, request, queryset):
        for invitation in queryset:
            if not invitation.accepted:
                link = request.build_absolute_uri(f'/register/{invitation.code}/')
                subject = 'You are invited to join the Task Management App'
                message = f'Click the link to register: {link}'
                from_email = config('EMAIL_HOST_USER')
                recipient_list = [invitation.email]

                # Send email
                send_mail(subject, message, from_email, recipient_list)

        self.message_user(request, "Invitation emails sent.")

    send_invitations.short_description = "Send Invitation Emails"

admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Task)
