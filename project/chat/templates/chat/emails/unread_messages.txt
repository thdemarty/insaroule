{% load i18n %}{% translate "Hello" %} {{ user.username }},

{% blocktranslate trimmed with count=unread_count %}You have {{count}} unread messages on INSA'ROULE.{% endblocktranslate %}
{% for chat in chats %}
* {% blocktranslate trimmed with contact=chat.contact destination=chat.ride_end date=chat.ride_date|date:"j F Y"  %}
{{contact}} contacted you about the ride to {{destination}} on {{date}}{% endblocktranslate %}{% endfor %}

{% translate "To answer these messages, connect to your account." %}

{% include "emails/consent_footer.txt" %}