# Backend
## Установка
```bash
cd backend
```

```bash
python -m venv venv
```

```bash
venv\Scripts\activate
```


```bash
pip install -r requirements.txt
```

## Запуск api
```bash
uvicorn backend.app.main:app --reload
```

## Запуск тестов
```bash
pytest backend/tests/test_api.py -v
```
