📋 *Ваши напоминания:*

{% for event in events %}
*{{ loop.index }}\. \[ID: {{ event.id }}\]* {{ event.description | escape_md }}
   ⏰ `{{ to_msk(event.event_datetime) }}` \(МСК\)
   🔄 {{ (event.repeat_interval.value if event.repeat_interval else "Однократное") | escape_md }}

{% endfor %}