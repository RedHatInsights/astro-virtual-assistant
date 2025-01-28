import normalizers
from common.config import app

functions_map = {
    "fun_cat_facts": {
        "console_request_args": {
            "app_name": "cat_facts",
            "path": "/get_facts",
            "method": "get",
            # app_name,path,method is required, but can contain a number of different variables here
        },
        "normalizer": normalizers.cat_facts_normalizer,
    }
}
