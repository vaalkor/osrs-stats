def concat_iterable(iterable):
    return ''.join([str(x) for x in iterable])

def concat_vals(*values):
    print(len(values))
    return ''.join([str(x) for x in values])

def elem(tag, *values, classes='', id='', href='', attribute_string='', src=''):
    classes = f' class="{classes}"' if classes else ''
    id = f' id="{id}"' if id else ''
    href = f' href="{href}"' if href else ''
    src = f' src="{src}"' if src else ''

    print(values)
    return f'<{tag}{classes}{href}{id}{src} {attribute_string}>{concat_iterable(values)}</{tag}>'

def elems(tag, *values):
    if len(values) == 0:
        raise 'No values provided!'
    for val in values:
        return ''.join((elem(tag, x) for x in values))

# print(elem('a'))
# print(elem('table', \
#         elem('tr', elems('th', 'Skill', 'XP Gain', 'Level Gain')), \
#         elem('tr', elems('td', 'Strength', '4235345', '83 => 85')),
#         elem('tr', elems('td', 'Attack', '53', '80 => 83')),
#         elem('tr', elems('td', 'Defense', '345', '90 => 95'))
#         ))

# print(join_any([1,2,3,4,5,6,7,8,9,10]))
