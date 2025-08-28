{% load i18n %}{% translate "Hello" %} {{ user.username }},

{% blocktranslate trimmed count counter=unread_count %}
You have an unread message on INSA'ROULE.
{% plural %}
You have {{ counter }} unread messages on INSA'ROULE.
{% endblocktranslate %}
{% for chat in chats %}
* {% blocktranslate trimmed with contact=chat.contact destination=chat.ride_end date=chat.ride_date|date:"j F Y"  %}
{{contact}} contacted you about the ride to {{destination}} on {{date}}{% endblocktranslate %}{% endfor %}

{% translate "To answer these messages, connect to your account." %}

{% include "emails/consent_footer.txt" %}