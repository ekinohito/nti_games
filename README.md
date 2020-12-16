# nti-games

## Разворачивание с помощью Docker:
```bash
git clone https://github.com/Platun0v/nti_games
```
Добавте в файл `.env.example` свои значения и сохраните, как `.env`

```bash
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate --noinput
docker-compose exec web python manage.py collectstatic --no-input --clear
```

После этого Docker слушает 1337 порт
