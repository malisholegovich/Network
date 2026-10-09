import re
from bs4 import BeautifulSoup


def parse_html_tables(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")

    method = None
    path = None
    is_file_upload = False
    files_list = None
    step_number = 0

    for h1 in soup.find_all('h1'):
        if "Шаг #" in h1.text:
            match = re.search(r"Шаг #(\d+)", h1.text)
            if match:
                step_number = int(match.group(1))
                break

    def extract_table_data(marker_text):
        text_element = soup.find(string=re.compile(marker_text))
        if not text_element:
            return None

        table = text_element.find_next('table')
        if not table:
            return None

        data = {}
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 2:
                key = cols[0].text.strip()
                val = cols[1].text.strip()
                data[key] = val
        return data if data else None

    file_marker = soup.find(string=re.compile("Загрузите файлы по адресу"))
    if file_marker:
        is_file_upload = True
        method = "POST"

        code_tag = file_marker.find_next('code')
        if code_tag:
            path = code_tag.text.strip()

        raw_files = extract_table_data("Загрузите файлы по адресу")
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
        a_tag = soup.find('a', href=True)
        if a_tag:
            method = "GET"
            path = a_tag['href']
        else:
            request_text = soup.find(string=re.compile(r"([A-Z]+)-запрос"))
            if request_text:
                m = re.search(r"([A-Z]+)-запрос", request_text)
                if m:
                    method = m.group(1)

                code_tag = request_text.find_next('code')
                if code_tag:
                    path = code_tag.text.strip()

    if step_number:
        print(f"Шаг {step_number}")

    result = {
        "step": step_number,
        "is_file_upload": is_file_upload,
        "files": files_list,
        "method": method,
        "path": path,
        "headers": extract_table_data("следующие заголовки") if not is_file_upload else None,
        "cookies": extract_table_data("выставлены cookie") if not is_file_upload else None,
        "form_data": extract_table_data("данные формы") if not is_file_upload else None,
        "query_params": extract_table_data("параметры запроса") if not is_file_upload else None
    }

    return result
