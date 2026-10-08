import re


def parse_html_tables(html_text):
    headers_pattern = r"Запрос должен иметь следующие заголовки:.*?(<table.*?>.*?</table>)"
    cookies_pattern = r"В запросе должны быть выставлены cookie:.*?(<table.*?>.*?</table>)"
    form_pattern = r"Запрос должен иметь следующие данные формы:.*?(<table.*?>.*?</table>)"
    query_pattern = r"При переходе выставьте следующие параметры запроса, указанные в таблице:.*?(<table.*?>.*?</table>)"

    files_table_pattern = r"Загрузите файлы по адресу.*?(<table.*?>.*?</table>)"
    p_file_path = r"Загрузите файлы по адресу.*?<code>(.*?)</code>"

    row_pattern = r"<td><code>(.*?)</code></td>\s*<td><code>(.*?)</code></td>"
    p_request = r"([A-Z]+)-запрос.*?<code>(.*?)</code>"
    p_request_an = r'<a\s+href=[\'"](.*?)[\'"]'
    p_step = r"<h1>Шаг #(\d+) \(из множества\)</h1>"

    def extract_dict(pattern, text):
        table_match = re.search(pattern, text, re.DOTALL)
        if table_match:
            table_html = str(table_match.group(1))
            rows = re.findall(row_pattern, table_html, re.DOTALL)
            return {key: value for key, value in rows}
        return None

    method = None
    path = None
    is_file_upload = False
    files_list = None

    file_path_match = re.search(p_file_path, html_text)
    if file_path_match:
        is_file_upload = True
        method = "POST"
        path = file_path_match.group(1)

        raw_files = extract_dict(files_table_pattern, html_text)
        if raw_files:
            files_list = []
            for fname, fcontent in raw_files.items():
                files_list.append({
                    "name": "file",
                    "filename": fname,
                    "content_type": "application/octet-stream",
                    "content": fcontent
                })

    if not is_file_upload:
        link_match = re.search(p_request_an, html_text)
        if link_match:
            method = "GET"
            path = link_match.group(1)
        else:
            req_match = re.search(p_request, html_text)
            if req_match:
                method = req_match.group(1)
                path = req_match.group(2)

    step_match = re.search(p_step, html_text)
    step_number = 0
    if step_match:
        step_number = step_match.group(1)
        print(f"Шаг {step_number}")

    result = {
        "step": step_number,
        "is_file_upload": is_file_upload,
        "files": files_list,
        "method": method,
        "path": path,
        "headers": extract_dict(headers_pattern, html_text) if not is_file_upload else None,
        "cookies": extract_dict(cookies_pattern, html_text) if not is_file_upload else None,
        "form_data": extract_dict(form_pattern, html_text) if not is_file_upload else None,
        "query_params": extract_dict(query_pattern, html_text) if not is_file_upload else None
    }

    return result
