from mysocket.all_func import create_standard_request, create_file_request, send_and_receive

target_host = "hw1.alexbers.com"
user = {"user": "9bd3219396195529fcf1b0fcbf1a4067"}
req = create_standard_request(
    host=target_host,
    path="/",
    method="GET",
    cookies=user,
)
expected_step = 1
prev_html = None

for _ in range(700):
    answer = send_and_receive(target_host, req)
    raw_html = answer[0]
    parsed_data = answer[1]

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

    if parsed_data.get("is_file_upload"):
        req = create_file_request(
            host=target_host,
            path=parsed_data["path"],
            files=parsed_data["files"],
            cookies=step_cookies
        )
    else:
        req = create_standard_request(
            host=target_host,
            path=parsed_data["path"],
            method=parsed_data["method"],
            cookies=step_cookies,
            custom_headers=parsed_data.get("headers"),
            form_data=parsed_data.get("form_data"),
            query_params=parsed_data.get("query_params"),
        )

    prev_html = raw_html