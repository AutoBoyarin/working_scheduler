1. Загружается конфигурация из `.env`/`.env.local`.
2. Инициализируется PostgreSQL (создаются необходимые таблицы) и клиент MinIO.
3. Из БД выбирается пачка платных объявлений (`BATCH_LIMIT`).
4. Выполняется модерация текста и изображений.
5. Результат сохраняется в БД; покрытые изображения загружаются в MinIO.
6. Для отладки локально сохраняется `verdict_<ad_id>.json` в `OUTPUT_FOLDER`.


## Структура проекта (основное)
- `src/ad_moderator.py` — входная точка пакетной модерации.
- `src/config.py` — загрузка конфигурации из переменных окружения.
- `src/db.py` — работа с PostgreSQL (инициализация, выборки, сохранение результатов).
- `src/storage.py` — вспомогательные функции для MinIO.
- `src/utils.py` — утилиты, включая загрузку файлов по URL.
- `src/text_moderator/` — правила/логика текстовой модерации.
- `src/image_moderator/` — модерация изображений (YOLO, OpenCV), модели и примеры.


## Частые вопросы
- Ошибка про отсутствующие переменные окружения — проверьте `src/.env.local` по примеру выше.
- Нет соединения с PostgreSQL — проверьте `DB_HOST`, `DB_PORT`, доступы пользователя и сетевые правила.
- Нет доступа к MinIO — проверьте `MINIO_*` и что бакеты существуют; утилита сама создаст их при первом запуске.
- Модель не найдена — проверьте `MODEL_PATH` и наличие файла `.onnx`.


## Разработка
- Форматирование/линтинг не навязаны; придерживайтесь стиля существующего кода.
- Dependencies — см. `requirements.txt`.


## Лицензия
Если лицензия требуется, добавьте соответствующий раздел и файл `LICENSE`.

## Запуск в Docker (docker-compose)
В репозитории есть `Dockerfile` и `docker-compose.yml`, которые поднимают:
- `db` — PostgreSQL 15,
- `minio` — MinIO (S3-совместимое хранилище) + `mc` для инициализации бакетов,
- `app` — само приложение.

### 1) Подготовить переменные окружения
Создайте файл `.env` в корне проекта (или скопируйте `.env.docker.example` при наличии) со значениями, например:

```
# PostgreSQL
DB_NAME=advertisement
DB_USER=autoboyarin
DB_PASSWORD=secret

# MinIO
MINIO_ACCESS_KEY=ROOTNAME
MINIO_SECRET_KEY=CHANGEME123
MINIO_SYSTEM_BUCKET=autoboyarin
MINIO_CLIENT_BUCKET=autoboyarin-client
MINIO_CLIENT_PUBLIC_ACCESS=true

# Приложение
BATCH_LIMIT=50
CLEAN_OUTPUT_ON_START=true
COMMIT_RESULTS=true
SCHEDULER_INTERVAL_MINUTES=1
```

Примечания:
- Приложение внутри контейнера само подключается к `db` и `minio` по сервисным именам.
- Пути `OUTPUT_FOLDER` и `MODEL_PATH` внутри образа уже настроены по умолчанию (`/app/src/...`). При необходимости их можно переопределить через `.env`.

### 2) Сборка и запуск
```
docker compose build
docker compose up -d
```

Проверить логи приложения:
```
docker compose logs -f app
```

Остановить:
```
docker compose down
```

Остановить и очистить данные (PostgreSQL и MinIO):
```
docker compose down -v
```

Открыть MinIO Console: http://localhost:9001 (логин/пароль — из `.env`).
