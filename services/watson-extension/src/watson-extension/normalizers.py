# Sample normalizer to format data that will come in from console_request
def cat_facts_normalizer(data):
    cat_fact = data.get("fact")
    return {"cat_fact": cat_fact}
