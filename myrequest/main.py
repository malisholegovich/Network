import requests
from parsing_text import parse_html_tables

target_host = "http://hw1.alexbers.com"
user = {"user": "9bd3219396195529fcf1b0fcbf1a4067"}

req_kwargs = {
    "method": "GET",
    "url": target_host + "/",
    "cookies": user
}

expected_step = 1
prev_html = None

for _ in range(700):
    response = requests.request(**req_kwargs)
    raw_html = response.text
    parsed_data = parse_html_tables(raw_html)

    if not parsed_data.get("path"):
        print("Конец маршрута или финальный ответ\n", raw_html)
        break

    current_step_str = parsed_data.get("step")
    if current_step_str:
        current_step = int(current_step_str)
        if current_step < expected_step:
            print(f"\nШаги сбросились с {expected_step-1} на {current_step}")
            print("\nПРЕДЫДУЩИЙ ШАГ")
            if prev_html:
                print(prev_html)
            break
        expected_step = current_step + 1

    step_cookies = user.copy()

    if parsed_data.get("cookies"):
        step_cookies.update(parsed_data["cookies"])

    req_kwargs = {
        "method": parsed_data["method"],
        "url": target_host + parsed_data["path"],
        "cookies": step_cookies
    }

    if parsed_data.get("headers"):
        req_kwargs["headers"] = parsed_data["headers"]

    if parsed_data.get("query_params"):
        req_kwargs["params"] = parsed_data["query_params"]

    if parsed_data.get("is_file_upload"):
        files_payload = []
        for f in parsed_data["files"]:
            files_payload.append(
                (f["name"], (f["filename"], f["content"].encode('utf-8')))
            )
        req_kwargs["files"] = files_payload
    elif parsed_data.get("form_data"):
        req_kwargs["data"] = parsed_data["form_data"]

    prev_html = raw_html