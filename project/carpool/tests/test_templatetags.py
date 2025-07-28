from django.test import TestCase
from carpool.templatetags.duration import duration


class TemplateTagsTestCase(TestCase):
    def test_duration_template_tag(self):
        from datetime import timedelta

        # Less than an hour
        self.assertEqual(duration(timedelta(minutes=30)), "30min")
        self.assertEqual(duration(timedelta(minutes=0)), "0min")

        # Exactly one hour
        self.assertEqual(duration(timedelta(hours=1)), "1h")
        self.assertEqual(duration(timedelta(hours=1, minutes=0)), "1h")

        # More than one hour
        self.assertEqual(duration(timedelta(hours=1, minutes=30)), "1h30")
        self.assertEqual(duration(timedelta(hours=2, minutes=5)), "2h05")
