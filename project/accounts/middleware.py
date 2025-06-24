from django.shortcuts import redirect


class VerifyEmailMiddleware:
    """
    Middleware to check if the user has verified their email address.
    if the user is authenticated and has not verified their email address,
    redirect them to the verify_email_send_token view.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.email_verified:
            if not request.path.startswith("/accounts/register"):
                return redirect("accounts:verify_email_send_token")
        response = self.get_response(request)
        return response
