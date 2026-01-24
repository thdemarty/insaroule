from django.contrib.auth.views import PasswordContextMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_not_required
from django.views.decorators.csrf import csrf_protect

from accounts.forms import UsernameSendForm


@method_decorator(login_not_required, name="dispatch")
class UsernameSendView(PasswordContextMixin, FormView):
    email_template_name = "registration/username_send/email.html"
    extra_email_context = None
    form_class = UsernameSendForm
    from_email = None
    html_email_template_name = None
    subject_template_name = "registration/username_send/username_send_subject.txt"
    success_url = reverse_lazy("username_send_done")
    template_name = "registration/username_send/index.html"
    title = "Username Send"
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)


INTERNAL_RESET_SESSION_TOKEN = "_username_send_token"


class UsernameSendDoneView(PasswordContextMixin, TemplateView):
    template_name = "registration/username_send/done.html"
    title = "Username sent"
