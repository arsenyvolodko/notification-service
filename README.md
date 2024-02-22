# Notification Service

`django` `djangorestframework` `celery` `aiohttp` `asyncio`

## Общее описание

Web-сервис для управления рассылками посредством как REST API, так и UI-интерфейса и получения статистики.
Ccылка на **web-сервис: [notification_service](http://91.201.113.17/).**

В рамках дополнительных заданий были реализованы:
- **№6: web-интерфейс: см. [notification_service](http://91.201.113.17/)** (сервис просит авторизоваться, можно просто зарегистрироваться для взиаимодействия с сервисом)
- **№7: интеграция с внешним OAuth2** сервисом авторизации для административного интерфейса.
- **№9: откладывание запросов при неуспешном обращении к серверу** неуспешном обращении к сервису при попытке отправки сообщения повторная попытка совершается через 5 минут
- **№11: учет часовых поясов** реализовано без дополнительного поля в моделе. Время рассылки указывается в соответсвии со временем, в которое сообщение должно прийти пользователю с учетом его часового пояса. То есть, если время начала рассылки - X, то пользователям в разных часовых поясах будут приходить сообщения после наступления времени X в их часовом поясе

### Доп информация

- **Асинхронность** - для отправки сообщений используется `celery` и `aiohttp`. При отправке сообщения через `aiohttp` используется `asyncio` для асинхронной отправки сообщений.
- При обновлении атрибутов клиента или рассылки, а также при удалении клиента или рассылки, добавляется новые задания в очередь, а старые корректно пропускаются, что не сказывается на статистике.
- В качестве базы данных используется `PostgreSQL` развернутый на личном сервере.
- Все возможности доступны через REST API, а также через web-интерфейс, реализованный с использованием HTML и JavaScript.
- При обновлении атрибутов клиента или рассылки достаточно указать только те атрибуты, которые необходимо обновить. Остальные атрибуты останутся без изменений.



## API Endpoints

BASE_URL = `http://91.201.113.17:3000/`
### Клиенты

- **Добавление нового клиента**
  - `clients/create/`
  - Тело запроса: JSON с атрибутами клиента

- **Обновление атрибутов клиента**
  - `PATCH /clients/update/{client_id}`
  - `{client_id}` - идентификатор клиента
  - Тело запроса: JSON с атрибутами клиента для обновления

- **Удаление клиента**
  - `DELETE /clients/delete/{client_id}`
  - `{client_id}` - идентификатор клиента

### Рассылки

- **Добавление новой рассылки**
  - `POST /mailing/create/`
  - Тело запроса: JSON с атрибутами рассылки

- **Обновление атрибутов рассылки**
  - `PATCH /mailing/update/{mailing_id}`
  - `{mailing_id}` - идентификатор рассылки
  - Тело запроса: JSON с атрибутами рассылки для обновления

- **Удаление рассылки**
  - `DELETE /mailing/delete/{mailing_id}`
  - `{mailing_id}` - идентификатор рассылки

### Статистика

- **Получение общей статистики по рассылкам**
  - `GET /stats/`

- **Получение детальной статистики по конкретной рассылке**
  - `GET /stats/{mailing_id}`
  - `{mailing_id}` - идентификатор рассылки

### Примеры взаимодействия с API

#### Создание клиента

```python
import requests
import json

data = {
    "phone_number": 9101459028,
    "tag": "tag",
    "timezone": "Europe/Moscow"
}

headers = {'Content-Type': 'application/json'}
url = 'http://91.201.113.17:3000/clients/create/'

response = requests.post(url, data=json.dumps(data), headers=headers)
```

#### Создание рассылки

```python
import requests
import json
from datetime import datetime, timedelta

data = {
    "start_time": (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ'),
    "end_time": (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%SZ'),
    "text": "text",
    "tags_filter": [],
    "codes_filter": [910, 911]
}

headers = {'Content-Type': 'application/json'}
url = 'http://91.201.113.17:3000/mailing/create/'

response = requests.post(url, data=json.dumps(data), headers=headers)
```

#### Получение статистики

```python
import requests

url_for_all_stats = 'http://91.201.113.17:3000/stats/'
url_for_specific_stats = 'http://91.201.113.17:3000/stats/85'

response_all_stats = requests.get(url_for_all_stats)
response_specific_stats = requests.get(url_for_specific_stats)
```



