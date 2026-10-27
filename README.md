# AQSHAM Electric — glass redesign samples

Статическая **пустышка-копия** шаблона [aqsham.kz](https://www.aqsham.kz/) с glassmorphism-вариантами для согласования редизайна.

**Демо:** https://aqsham.melnichuk.kz/

## Страницы

| URL | Что это |
|-----|---------|
| `/` | V1 — копия шаблона + светлое стекло |
| `/hub.html` | Хаб образцов |
| `/samples/v2-dark.html` | V2 — тёмное стекло |
| `/samples/v3-aurora.html` | V3 — aurora-стекло |

## Структура

```
index.html          # главный образец (V1)
hub.html            # список вариантов
samples/            # V2 / V3
css/                # theme-clone.css + glass overlays
js/clone.js         # слайдер героя
assets/             # логотипы, товары, бренды, проекты
tools/              # сборка/деплой (секреты только через env)
```

## Как править

1. Править HTML/CSS/JS локально.
2. Открыть `index.html` в браузере или поднять любой static server.
3. Стили темы: `css/theme-clone.css`, стекло: `css/glass.css` (+ `glass-dark.css` / `glass-aurora.css`).
4. Пересобрать из скрейпа (опционально): `python tools/_build_clone.py`

Это **фронт без бэкенда**: корзина/формы — демо, ссылки на прод отключены.

## Деплой на melnichuk.kz

Нужны переменные из `.env.example`, затем:

```bash
python tools/deploy.py
```

## Для AI (Grok и др.)

Задача: доработать визуал и UX B2B-каталога электротехники AQSHAM (Актобе), сохранив структуру секций оригинала (шапка, герой-слайдер товаров, каталог, бренды, проекты, новости, CTA, футер). Стекло — по желанию клиента; не ломать мобильную читаемость и контраст текста.
