import socket
from parsing_text import parse_html_tables


def create_standard_request(host, path, method="GET", cookies=None, custom_headers=None, query_params=None,
                            form_data=None):
    if query_params:
        r_query = "&".join([f"{k}={v}" for k, v in query_params.items()])
        path = f"{path}?{r_query}"

    req_lines = [
        f"{method} {path} HTTP/1.1",
        f"Host: {host}",
        "Connection: close"
    ]
    if cookies:
        r_cookie = f"Cookie: {';'.join([f'{k}={v}' for k, v in cookies.items()])}"
        req_lines.append(r_cookie)

    if custom_headers:
        req_lines.extend([f"{k}: {v}" for k, v in custom_headers.items()])

    body_bytes = b""
    if form_data:
        r_form = "&".join([f"{k}={v}" for k, v in form_data.items()])
        body_bytes = r_form.encode('utf-8')
        req_lines.append("Content-Type: application/x-www-form-urlencoded")
        req_lines.append(f"Content-Length: {len(body_bytes)}")
    request_str = "\r\n".join(req_lines) + "\r\n\r\n"
    return request_str.encode('utf-8') + body_bytes


def create_file_request(host, path, files, cookies=None, custom_headers=None):
    boundary = "----aboba"
    body_parts = []

    for file_info in files:
        content_type = file_info.get("content_type", "application/octet-stream")
        part = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{file_info["name"]}"; filename="{file_info["filename"]}"\r\n'
            f'Content-Type: {content_type}\r\n'
            "\r\n"
            f'{file_info["content"]}\r\n'
        )
        body_parts.append(part)

    body_parts.append(f"--{boundary}--\r\n")

    body_str = "".join(body_parts)
    body_bytes = body_str.encode('utf-8')

    req_lines = [
        f"POST {path} HTTP/1.1",
        f"Host: {host}",
        "Connection: close",
        f"Content-Type: multipart/form-data; boundary={boundary}",
        f"Content-Length: {len(body_bytes)}"
    ]

    if cookies:
        r_cookie = f"Cookie: {';'.join([f'{k}={v}' for k, v in cookies.items()])}"
        req_lines.append(r_cookie)

    if custom_headers:
        req_lines.extend([f"{k}: {v}" for k, v in custom_headers.items()])

    request_str = "\r\n".join(req_lines) + "\r\n\r\n"
    return request_str.encode('utf-8') + body_bytes


def send_and_receive(host, request_bytes):
    s = socket.create_connection((host, 80))
    s.sendall(request_bytes)

    response = b""
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        response += chunk

    s.close()

    decoded_text = response.decode('utf-8', errors='ignore')

    return [decoded_text, parse_html_tables(decoded_text)]
