from bs4 import BeautifulSoup, Comment, Tag, NavigableString

def clean_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    void_elements = {'area', 'base', 'col', 'embed', 'hr', 'img', 'input',
                     'link', 'meta', 'param', 'source', 'track', 'wbr'}
    for tag in soup.find_all(void_elements):
        tag.decompose()

    for br in soup.find_all("br"):
        br.replace_with(" ")

    def preserve_text_before_removal(tag):
        # If the tag contains heading tags, don't strip it
        if any(child.name and child.name.startswith("h") for child in tag.find_all()):
            return
        if tag.name == "a":
            tag.replace_with(NavigableString(tag.get_text(" ", strip=True)))
        elif tag.contents:
            tag.replace_with(NavigableString(tag.get_text(" ", strip=True)))

    for tag in soup.find_all(["div", "span", "a"]):
        if not tag.get_text(strip=True):
            tag.extract()
        else:
            preserve_text_before_removal(tag)

    for tag in soup.find_all(True):
        if tag.name in ["td", "th"]:
            tag.attrs = {k: v for k, v in tag.attrs.items() if k in ["colspan", "rowspan"]}
        else:
            tag.attrs = {}

    def merge_single_nested_tags(tag):
        while len(tag.contents) == 1 and isinstance(tag.contents[0], Tag):
            inner_tag = tag.contents[0]
            tag.replace_with(inner_tag)
            tag = inner_tag

    for tag in soup.find_all(True):
        merge_single_nested_tags(tag)

    return str(soup)

def ensure_thead_between_table_and_tbody(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for table in soup.find_all("table"):
        tbody = table.find("tbody")
        thead = table.find("thead")

        if tbody and not thead:
            new_thead = soup.new_tag("thead")
            tbody.insert_before(new_thead)

            for tr in table.find_all('tr', recursive=False):
                tr.extract()
                new_thead.append(tr)

    return str(soup)

def ensure_tbody_after_thead(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for table in soup.find_all("table"):
        thead = table.find("thead")
        tbody = table.find("tbody")

        if not tbody:
            tbody = soup.new_tag("tbody")

        if thead:
            if tbody not in table.contents:
                thead.insert_after(tbody)
            elif table.contents.index(tbody) < table.contents.index(thead):
                tbody.extract()
                thead.insert_after(tbody)
        else:
            if tbody not in table.contents:
                table.insert(0, tbody)

    return str(soup)

def multiple_tbody_in_table(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")

    for table in tables:
        tbodies = table.find_all("tbody")

        if len(tbodies) > 1:
            
            
            for tbody in tbodies:
                for td in tbody.find_all("td"):
                    colspan = td.get("colspan")
                    if colspan and int(colspan) > 5:
                        th = soup.new_tag("th", **td.attrs)
                        th.string = td.get_text(strip=True)
                        td.replace_with(th)

            
            first_tbody = tbodies[0]

            
            for tbody in tbodies[1:]:
                for element in tbody.find_all(["tr", "th"]):
                    first_tbody.append(element)

            
            for tbody in tbodies[1:]:
                tbody.unwrap()  

    return str(soup)

def build_block_tree(html_content):
    cleaned_html = clean_html(html_content)
    fixed_html = ensure_thead_between_table_and_tbody(cleaned_html)
    fixed_html = ensure_tbody_after_thead(fixed_html)
    fully_processed_html = multiple_tbody_in_table(fixed_html)

    return fully_processed_html  

sample_html_path = "./mcmaster_html/tables_67fc719093950cd451f6f498110fb922.html"

def call_build_block():
    with open(sample_html_path, "r", encoding="utf-8") as file:
        sample_html = file.read()

    block_tree_html = build_block_tree(sample_html)

    
    return block_tree_html











