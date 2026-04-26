# Лабораторна робота №3

**Виконавець:** Сєров Едуард Олегович  
**Група:** К-26  
**Викладач:** Ляшко А. В  
**Варіант:** 19  
**Задача:** 2

---

**Умова:**  
За даними сайту https://cppreference.com з'ясувати для `std::variant`:  
- Member types, Member functions, Non-member functions  
- Скільки перелічено конструкторів
- Для кожного конструктора — стандарти, в яких він існує  
- Конструктори, що існують у стандарті C++23


```python
import requests
from bs4 import BeautifulSoup
import re

URL = 'https://en.cppreference.com/w/cpp/utility/variant'

resp = requests.get(URL, headers={
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) '
                  'Gecko/20100101 Firefox/136.0'
})
print('Status:', resp.status_code)
soup = BeautifulSoup(resp.text, 'html5lib')
```

    Status: 200



```python
def split_operators(text):
    if text.count('operator') > 1:
        parts = re.findall(r'operator[^o]*', text)
        return [p.rstrip() for p in parts if p.strip()]
    return [text]


def extract_section(soup, heading_text):
    heading_tag = None
    for tag in soup.find_all(['h3', 'h5', 'h2']):
        span = tag.find('span', id=lambda x: x and
                        heading_text.replace(' ', '_') in x)
        if span or heading_text in tag.get_text():
            heading_tag = tag
            break

    if heading_tag is None:
        return {}

    result = {}
    current_category = ''

    for sibling in heading_tag.find_next_siblings():
        if sibling.name in ['h2', 'h3', 'h5'] and sibling != heading_tag:
            break

        if sibling.name != 'table':
            continue

        for row in sibling.find_all('tr'):
            classes = row.get('class', [])

            is_header = any('hdr' in c for c in classes)
            if not is_header:
                th = row.find('th')
                if th and th.get('colspan'):
                    is_header = True

            if is_header:
                current_category = row.get_text(strip=True)
                if current_category not in result:
                    result[current_category] = []
                continue

            if 't-dsc' in classes:
                cells = row.find_all('td')
                if not cells:
                    continue

                a_tags = cells[0].find_all('a')
                if a_tags:
                    seen = []
                    for a in a_tags:
                        raw = a.get_text(strip=True)
                        if not raw:
                            continue
                        for part in split_operators(raw):
                            if part and part not in seen:
                                seen.append(part)
                    names = ', '.join(seen)
                else:
                    names = cells[0].get_text(strip=True)

                if names:
                    if current_category not in result:
                        result[current_category] = []
                    result[current_category].append(names)

    return result


def print_section(title, data):
    print(f'\n{"=" * 60}')
    print(f'  {title}')
    print('=' * 60)
    if not data:
        print('  (відсутні)')
        return
    for category, items in data.items():
        if category:
            print(f'\n  [{category}]')
        print('  ' + ', '.join(items))
```


```python
member_types = extract_section(soup, 'Member types')
print_section('MEMBER TYPES', member_types)
```

    
    ============================================================
      MEMBER TYPES
    ============================================================
      (відсутні)



```python
member_functions = extract_section(soup, 'Member functions')
print_section('MEMBER FUNCTIONS', member_functions)
```

    
    ============================================================
      MEMBER FUNCTIONS
    ============================================================
      (constructor), (destructor), operator=, index, valueless_by_exception, emplace, swap, visit



```python
non_member_functions = extract_section(soup, 'Non-member functions')
print_section('NON-MEMBER FUNCTIONS', non_member_functions)
```

    
    ============================================================
      NON-MEMBER FUNCTIONS
    ============================================================
      visit, holds_alternative, get(std::variant), get_if, operator==, operator!=, operator<, operator<=, operator>, operator>=, operator<=>, std::swap(std::variant)



```python
CTOR_URL = 'https://en.cppreference.com/w/cpp/utility/variant/variant'

r_ctor = requests.get(CTOR_URL, headers={
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) '
                  'Gecko/20100101 Firefox/136.0'
})
print('Status (constructor page):', r_ctor.status_code)
soup_ctor = BeautifulSoup(r_ctor.text, 'html5lib')
```

    Status (constructor page): 200



```python
constructors = []

dcl_table = soup_ctor.find('table', class_='t-dcl-begin')

if dcl_table:
    num = 1
    for row in dcl_table.find_all('tr', class_='t-dcl'):
        cells = row.find_all('td')
        if not cells:
            continue

        decl_text = cells[0].get_text(' ', strip=True)
        decl_text = re.sub(r'\s+', ' ', decl_text).strip()

        std_spans = row.find_all('span', class_=re.compile(r't-mark-rev'))
        standards = [s.get_text(strip=True) for s in std_spans]

        if not standards and len(cells) >= 2:
            rev_text = cells[-1].get_text(strip=True)
            if 'C++' in rev_text:
                standards = [rev_text]

        constructors.append({
            'num'        : num,
            'declaration': decl_text,
            'standards'  : standards if standards else ['(since C++17)']
        })
        num += 1

print(f'Знайдено конструкторів: {len(constructors)}\n')
for c in constructors:
    print(f'  ({c["num"]}) {c["declaration"]}')
    print(f'       Стандарти: {", ".join(c["standards"])}')
    print()
```

    Знайдено конструкторів: 8
    
      (1) constexpr variant ( ) noexcept ( /* see below */ ) ;
           Стандарти: (since C++17)
    
      (2) constexpr variant ( const variant & other ) ;
           Стандарти: (since C++17)
    
      (3) constexpr variant ( variant && other ) noexcept ( /* see below */ ) ;
           Стандарти: (since C++17)
    
      (4) template < class T > constexpr variant ( T && t ) noexcept ( /* see below */ ) ;
           Стандарти: (since C++17)
    
      (5) template < class T, class ... Args > constexpr explicit variant ( std:: in_place_type_t < T > , Args && ... args ) ;
           Стандарти: (since C++17)
    
      (6) template < class T, class U, class ... Args > constexpr explicit variant ( std:: in_place_type_t < T > , std:: initializer_list < U > il, Args && ... args ) ;
           Стандарти: (since C++17)
    
      (7) template < std:: size_t I, class ... Args > constexpr explicit variant ( std:: in_place_index_t < I > , Args && ... args ) ;
           Стандарти: (since C++17)
    
      (8) template < std:: size_t I, class U, class ... Args > constexpr explicit variant ( std:: in_place_index_t < I > , std:: initializer_list < U > il, Args && ... args ) ;
           Стандарти: (since C++17)
    



```python
def exists_in_cpp23(standards):
    removed = any(re.search(r'until C\+\+(?:17|20|23)', s) for s in standards)
    only_26 = (any('since' in s for s in standards) and
               all(re.search(r'since C\+\+26', s)
                   for s in standards if 'since' in s))
    return not removed and not only_26


cpp23_ctors = [c for c in constructors if exists_in_cpp23(c['standards'])]

print(f'Конструктори, що існують у C++23 ({len(cpp23_ctors)} з {len(constructors)}):\n')
for c in cpp23_ctors:
    print(f'  ({c["num"]}) {c["declaration"]}')
    print(f'       Стандарти: {", ".join(c["standards"])}')
    print()
```

    Конструктори, що існують у C++23 (8 з 8):
    
      (1) constexpr variant ( ) noexcept ( /* see below */ ) ;
           Стандарти: (since C++17)
    
      (2) constexpr variant ( const variant & other ) ;
           Стандарти: (since C++17)
    
      (3) constexpr variant ( variant && other ) noexcept ( /* see below */ ) ;
           Стандарти: (since C++17)
    
      (4) template < class T > constexpr variant ( T && t ) noexcept ( /* see below */ ) ;
           Стандарти: (since C++17)
    
      (5) template < class T, class ... Args > constexpr explicit variant ( std:: in_place_type_t < T > , Args && ... args ) ;
           Стандарти: (since C++17)
    
      (6) template < class T, class U, class ... Args > constexpr explicit variant ( std:: in_place_type_t < T > , std:: initializer_list < U > il, Args && ... args ) ;
           Стандарти: (since C++17)
    
      (7) template < std:: size_t I, class ... Args > constexpr explicit variant ( std:: in_place_index_t < I > , Args && ... args ) ;
           Стандарти: (since C++17)
    
      (8) template < std:: size_t I, class U, class ... Args > constexpr explicit variant ( std:: in_place_index_t < I > , std:: initializer_list < U > il, Args && ... args ) ;
           Стандарти: (since C++17)
    


## Висновок

За даними сайту https://en.cppreference.com/w/cpp/utility/variant:

**Member types:** відсутні — `std::variant` не визначає власних типів-членів.  
**Member functions:** `(constructor), (destructor), operator=, index, valueless_by_exception, emplace, swap, visit`
**Non-member functions:** `visit, holds_alternative, get, get_if, operator==, operator!=, operator<, operator<=, operator>, operator>=, operator<=>, std::swap`

**Конструктори:** усього 8. Усі введені у стандарті C++17 і не вилучені —  
тому всі 8 конструкторів існують у стандарті **C++23**.

Дані зібрано програмно за допомогою бібліотек `requests` та `beautifulsoup4`.
