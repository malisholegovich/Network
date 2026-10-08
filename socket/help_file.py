import socket
import re
p_step = r"<h1>Шаг #(\d+) \(из множества\)</h1>"
pattern = re.compile(p_step)
def parse_text(text: str):
    match = re.search(pattern, text)
    if match:
        step_number = match.group(1)
        print(f"Текущий номер шага: {step_number}")

s = socket.create_connection(("hw1.alexbers.com", 80))
r_head = (f"GET / HTTP/1.1",
          "Host: hw1.alexbers.com",)
r_conn = "Connection: close"

# куки по заданию
cookie = {
    "user" : "9bd3219396195529fcf1b0fcbf1a4067"
}
r_cookie = f"Cookie: {";".join([f"{k}={v}" for k, v in cookie.items()])}"

# заголовки по заданию
headers = {
    "primer": "primer"
}
r_headers = [f"{k}:{v}" for k, v in headers.items()]

# формы для пост запроса (r_form в конце запроса)
form_data = {
    "login": "test_user",
    "answer": "42"
}
r_form = "&".join([f"{k}={v}" for k, v in form_data.items()])
length = len(r_form.encode('utf-8'))
post = ("Content-Type: application/x-www-form-urlencoded",
        f"Content-Length: {length}",)
#  параметры запроса в сам url
query_params = {
    "user_id": "777",
    "secret": "my_pass"
}
r_query = "&".join([f"{k}={v}" for k, v in query_params.items()])

path = f"/next_step?{r_query}"
# загрузка файлов
boundary = "----aboba"
file1_str = (
    f"--{boundary}\r\n"
    'Content-Disposition: form-data; name="file1"; filename="first.txt"\r\n'
    "Content-Type: text/plain\r\n"
    "\r\n"
    "Текст первого файла\r\n"
)
# Обязательный закрывающий блок (обратите внимание на два дефиса в конце)
end_str = f"--{boundary}--\r\n"
body_str = file1_str + end_str
body_bytes = body_str.encode('utf-8')
body_length = len(body_bytes)
r_file = (f"Content-Type: multipart/form-data; boundary={boundary}",
          f"Content-Length: {body_length}")





request_str = "\r\n".join([*r_head,r_cookie,r_conn]) + "\r\n\r\n"
s.sendall(request_str.encode('utf-8'))
parse = s.recv(9000).decode()
print(parse)
parse_text(parse)
s.close()
