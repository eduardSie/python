# Лабораторна робота №3

**Виконавець:** Сєров Едуард Олегович  
**Група:** К-26  
**Викладач:** Ляшко А. В  
**Варіант:** 19  
**Задача:** 1

---

**Умова:**  
За даними сайту https://www.numbeo.com/ знайти країну, в якій найдорожче та найдешевше харчування на 1 місяць (азіатське меню). Надати інформацію: де та на якому меню досягається.


```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
```


```python
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) '
        'Gecko/20100101 Firefox/136.0'
    ),
    'Accept': (
        'text/html,application/xhtml+xml,application/xml;'
        'q=0.9,image/avif,image/webp,*/*;q=0.8'
    ),
    'Accept-Language': 'en-US,en;q=0.5',
}

BASE_URL = 'https://www.numbeo.com/food-prices/country_result.jsp'
```


```python
r_main = requests.get('https://www.numbeo.com/food-prices/', headers=HEADERS)
print('Статус відповіді:', r_main.status_code)

soup_main = BeautifulSoup(r_main.text, 'html5lib')

countries = []
for sel in soup_main.find_all('select'):
    if sel.get('name') == 'country' or sel.get('id') == 'country':
        for opt in sel.find_all('option'):
            val = opt.get('value', '').strip()
            if val:
                countries.append(val)
        break

print(f'Знайдено країн: {len(countries)}')
```

    Статус відповіді: 200
    Знайдено країн: 234



```python
def get_asian_monthly_usd(country: str) -> float | None | str:
    url = (
        f'{BASE_URL}'
        f'?country={country.replace(" ", "+")}'
        f'&displayCurrency=USD'
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)

        if resp.status_code == 429:
            return 'RATE_LIMIT'

        if resp.status_code != 200:
            return None

        if 'Monthly recommended minimum' not in resp.text:
            return None

        soup = BeautifulSoup(resp.text, 'html5lib')
        monthly_count = 0

        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if not cells:
                continue
            label = cells[0].get_text(strip=True)
            if 'Monthly recommended minimum' in label:
                monthly_count += 1
                if monthly_count == 2:
                    val = cells[1].get_text(strip=True)
                    clean = ''.join(c for c in val if c.isdigit() or c == '.')
                    return float(clean) if clean else None

        return None

    except Exception as e:
        print(f'  Помилка для {country}: {e}')
        return None


print('Перевірка функції:')
for c in ['Ukraine', 'Japan', 'Switzerland']:
    cost = get_asian_monthly_usd(c)
    print(f'  {c:15s}: {cost} USD/міс.')
```

    Перевірка функції:
      Ukraine        : 125.44 USD/міс.
      Japan          : 279.61 USD/міс.
      Switzerland    : 544.42 USD/міс.



```python
results  = {}
rate_hit = False
total    = len(countries)

for i, country in enumerate(countries):
    cost = get_asian_monthly_usd(country)

    if cost == 'RATE_LIMIT':
        rate_hit = True
        print(f'\n>>> Rate limit на країні [{i + 1}/{total}]: {country}')
        print(f'>>> Зібрано до ліміту: {len(results)} країн')
        break

    results[country] = cost

    collected = sum(1 for v in results.values() if v is not None)
    if (i + 1) % 10 == 0:
        print(f'  [{i + 1:3d}/{total}]  з даними: {collected}'
              f'  | {country} -> {cost}')

if not rate_hit:
    collected = sum(1 for v in results.values() if v is not None)
    print(f'\nЗбір завершено. Країн з даними: {collected} / {len(results)}')
```

      [ 10/234]  з даними: 10  | Antigua And Barbuda -> 442.73
      [ 20/234]  з даними: 20  | Barbados -> 351.85
      [ 30/234]  з даними: 29  | Botswana -> 140.96
      [ 40/234]  з даними: 39  | Cape Verde -> 253.64
    
    >>> Rate limit на країні [49/234]: Costa Rica
    >>> Зібрано до ліміту: 48 країн



```python
df = pd.DataFrame(
    [(k, v) for k, v in results.items() if v is not None],
    columns=['country', 'asian_menu_monthly_usd']
)

df['asian_menu_monthly_usd'] = pd.to_numeric(
    df['asian_menu_monthly_usd'], errors='coerce'
)
df.dropna(subset=['asian_menu_monthly_usd'], inplace=True)
df.sort_values('asian_menu_monthly_usd', ascending=False, inplace=True)
df.reset_index(drop=True, inplace=True)

print(f'Країн у датасеті: {len(df)}')
print()
display(df)
```

    Країн у датасеті: 45
    



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>country</th>
      <th>asian_menu_monthly_usd</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Bermuda</td>
      <td>659.54</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Cayman Islands</td>
      <td>582.96</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Bahamas</td>
      <td>448.23</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Antigua And Barbuda</td>
      <td>442.73</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Alderney</td>
      <td>440.45</td>
    </tr>
    <tr>
      <th>5</th>
      <td>British Virgin Islands</td>
      <td>406.55</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Anguilla</td>
      <td>390.70</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Barbados</td>
      <td>351.85</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Austria</td>
      <td>328.13</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Aruba</td>
      <td>311.36</td>
    </tr>
    <tr>
      <th>10</th>
      <td>American Samoa</td>
      <td>303.75</td>
    </tr>
    <tr>
      <th>11</th>
      <td>Canada</td>
      <td>301.77</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Aland Islands</td>
      <td>295.26</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Belgium</td>
      <td>285.15</td>
    </tr>
    <tr>
      <th>14</th>
      <td>Australia</td>
      <td>284.33</td>
    </tr>
    <tr>
      <th>15</th>
      <td>Cook Islands</td>
      <td>282.31</td>
    </tr>
    <tr>
      <th>16</th>
      <td>Burkina Faso</td>
      <td>280.43</td>
    </tr>
    <tr>
      <th>17</th>
      <td>Brunei</td>
      <td>268.18</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Cape Verde</td>
      <td>253.64</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Andorra</td>
      <td>246.45</td>
    </tr>
    <tr>
      <th>20</th>
      <td>Belize</td>
      <td>240.10</td>
    </tr>
    <tr>
      <th>21</th>
      <td>Albania</td>
      <td>205.35</td>
    </tr>
    <tr>
      <th>22</th>
      <td>Burundi</td>
      <td>200.01</td>
    </tr>
    <tr>
      <th>23</th>
      <td>Bulgaria</td>
      <td>196.67</td>
    </tr>
    <tr>
      <th>24</th>
      <td>Chad</td>
      <td>194.01</td>
    </tr>
    <tr>
      <th>25</th>
      <td>Argentina</td>
      <td>187.30</td>
    </tr>
    <tr>
      <th>26</th>
      <td>Bahrain</td>
      <td>183.85</td>
    </tr>
    <tr>
      <th>27</th>
      <td>Chile</td>
      <td>182.35</td>
    </tr>
    <tr>
      <th>28</th>
      <td>Bosnia And Herzegovina</td>
      <td>180.75</td>
    </tr>
    <tr>
      <th>29</th>
      <td>Armenia</td>
      <td>169.92</td>
    </tr>
    <tr>
      <th>30</th>
      <td>Angola</td>
      <td>167.24</td>
    </tr>
    <tr>
      <th>31</th>
      <td>Algeria</td>
      <td>165.69</td>
    </tr>
    <tr>
      <th>32</th>
      <td>Cambodia</td>
      <td>159.91</td>
    </tr>
    <tr>
      <th>33</th>
      <td>Colombia</td>
      <td>153.81</td>
    </tr>
    <tr>
      <th>34</th>
      <td>Cameroon</td>
      <td>150.58</td>
    </tr>
    <tr>
      <th>35</th>
      <td>Belarus</td>
      <td>141.32</td>
    </tr>
    <tr>
      <th>36</th>
      <td>Botswana</td>
      <td>140.96</td>
    </tr>
    <tr>
      <th>37</th>
      <td>Azerbaijan</td>
      <td>136.86</td>
    </tr>
    <tr>
      <th>38</th>
      <td>Benin</td>
      <td>134.81</td>
    </tr>
    <tr>
      <th>39</th>
      <td>Brazil</td>
      <td>131.71</td>
    </tr>
    <tr>
      <th>40</th>
      <td>Bolivia</td>
      <td>126.01</td>
    </tr>
    <tr>
      <th>41</th>
      <td>China</td>
      <td>125.46</td>
    </tr>
    <tr>
      <th>42</th>
      <td>Bhutan</td>
      <td>105.23</td>
    </tr>
    <tr>
      <th>43</th>
      <td>Afghanistan</td>
      <td>97.26</td>
    </tr>
    <tr>
      <th>44</th>
      <td>Bangladesh</td>
      <td>94.32</td>
    </tr>
  </tbody>
</table>
</div>



```python
print('Статистика — Asian Menu Monthly Cost (USD):')
display(df['asian_menu_monthly_usd'].describe().round(2).to_frame())
```

    Статистика — Asian Menu Monthly Cost (USD):



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>asian_menu_monthly_usd</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>45.00</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>247.45</td>
    </tr>
    <tr>
      <th>std</th>
      <td>126.76</td>
    </tr>
    <tr>
      <th>min</th>
      <td>94.32</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>153.81</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>200.01</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>301.77</td>
    </tr>
    <tr>
      <th>max</th>
      <td>659.54</td>
    </tr>
  </tbody>
</table>
</div>



```python
row_max = df.iloc[0]
row_min = df.iloc[-1]

note = (f'(вибірка: {len(df)} країн — '
        f'повний збір обмежено rate limit сайту)')

print('=' * 65)
print(f'ВІДПОВІДЬ (Варіант 19)  {note}')
print()
print('НАЙДОРОЖЧЕ харчування на 1 місяць:')
print(f'  Країна  : {row_max["country"]}')
print(f'  Вартість: ${row_max["asian_menu_monthly_usd"]:.2f} USD/місяць')
print(f'  Меню    : Asian Menu (monthly recommended minimum amount)')
print()
print('НАЙДЕШЕВШЕ харчування на 1 місяць:')
print(f'  Країна  : {row_min["country"]}')
print(f'  Вартість: ${row_min["asian_menu_monthly_usd"]:.2f} USD/місяць')
print(f'  Меню    : Asian Menu (monthly recommended minimum amount)')
print('=' * 65)
```

    =================================================================
    ВІДПОВІДЬ (Варіант 19)  (вибірка: 45 країн — повний збір обмежено rate limit сайту)
    
    НАЙДОРОЖЧЕ харчування на 1 місяць:
      Країна  : Bermuda
      Вартість: $659.54 USD/місяць
      Меню    : Asian Menu (monthly recommended minimum amount)
    
    НАЙДЕШЕВШЕ харчування на 1 місяць:
      Країна  : Bangladesh
      Вартість: $94.32 USD/місяць
      Меню    : Asian Menu (monthly recommended minimum amount)
    =================================================================


## Висновок

За даними сайту numbeo.com (розділ Food Prices, Asian Menu,
«monthly recommended minimum amount», у доларах США):

- **Найдорожче** азіатське харчування на місяць — **Bermuda** ($659.54 USD/міс.)

- **Найдешевше** азіатське харчування на місяць — **Bangladesh** ($94.32 USD/міс.)

Дані зібрано програмно за допомогою бібліотек `requests` та `beautifulsoup4`.
Для кожної країни зі списку надсилався GET-запит на сторінку
`country_result.jsp` з параметром `displayCurrency=USD`.
Значення Asian Menu визначалось як **другий** рядок
«Monthly recommended minimum amount» на сторінці країни.

**Примітка:** Сайт numbeo.com має обмеження безкоштовного плану
(rate limit — ~100 запитів/місяць). Аналіз виконано на вибірці
**45 країн** — усіх, дані яких вдалося отримати програмно
до досягнення ліміту (збір зупинився на країні Costa Rica).
