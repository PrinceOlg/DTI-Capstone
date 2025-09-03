from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Value, F, Q

class OwnershipDraftMixin:
    """
    Ensures that only the owning user can edit an object,
    and only if the object is still in draft status.
    """

    draft_only = True  # set to False if some forms can bypass draft restriction

    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        # Ownership check
        if hasattr(obj, "user") and obj.user != request.user:
            messages.error(request, "You cannot edit this item.")
            return redirect("/")

        # Status check (optional toggle)
        if self.draft_only and hasattr(obj, "status") and obj.status != "draft":
            messages.error(request, "You can only edit drafts.")
            return redirect("/")

        return super().post(request, *args, **kwargs)
    
class UserRoleMixin:
    @staticmethod
    def get_queryset_or_all(model, user):
        if user.role == "admin":
            qs = model.objects.filter(
                Q(status="draft", user=user) | ~Q(status="draft")
            )
        else:
            qs = model.objects.filter(user=user)
            
        return qs.only("pk", "id")  # Add other fields that __str__ methods need
    
    @staticmethod    
    def get_count_or_all(model, user):
        if user.role == "admin":
            return model.objects.filter(
                Q(status="draft", user=user) | ~Q(status="draft")
            ).count()
        else:
            return model.objects.filter(user=user).count()
