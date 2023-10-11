def show_more(name: str, url_prefix: str):
    return {"show_more": {"name": name, "url_prefix": url_prefix}}

def is_user_event(event):
  return event.get("event") == "user"