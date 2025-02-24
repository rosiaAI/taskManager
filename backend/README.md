# Backend
## Установка
```bash
python -m venv venv
```

```bash
source venv/bin/activate
```

```bash
cd backend
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
