def elem(tag, value='', classes='', id='', href='', attribute_string=''):
    classes = f' class="{classes}"' if classes else ''
    id = f' id="{id}"' if id else ''
    href = f' href="{href}"' if href else ''

    return f'<{tag}{classes}{href}{id} {attribute_string}>{value if value else ""}</{tag}>'

def elems(tag, *values): 
    if len(values) == 0:
        raise 'No values provided!'
    for val in values:
        return ''.join((elem(tag, x) for x in values))

# print(elem('a'))
# print(elem('a', 'chicken!'))
# print(elem('a', value='chicken!', href='https://google.com'))
# print(elem('a', value='chicken!', classes='bollocks twat'))

# print(elems('td', 'val1', 'val2'))