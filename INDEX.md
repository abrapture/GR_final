# Индекс проекта: Извлечение учебного контента из PDF

## 📚 Документация

### Основная документация

| Файл | Описание | Для кого |
|------|----------|----------|
| **README.md** | Общее описание проекта, быстрый старт, базовое использование | Все пользователи |
| **QUICKSTART.md** | Краткое руководство для немедленного начала работы | Новые пользователи |
| **EDUCATIONAL_CONTENT_GUIDE.md** | 📖 Полное руководство по извлечению учебного контента | Основной документ |
| **ARCHITECTURE_SUMMARY.md** | Техническое описание архитектуры и решений | Разработчики |
| **INDEX.md** | Этот файл - навигация по проекту | Все |

### Быстрая навигация

- **Хочу быстро начать** → [QUICKSTART.md](QUICKSTART.md)
- **Нужно извлечь лекции/учебники** → [EDUCATIONAL_CONTENT_GUIDE.md](EDUCATIONAL_CONTENT_GUIDE.md)
- **Понять как это работает** → [ARCHITECTURE_SUMMARY.md](ARCHITECTURE_SUMMARY.md)
- **Базовое использование** → [README.md](README.md)

## 🛠️ Инструменты

### Основные скрипты

| Файл | Назначение | Команда запуска |
|------|-----------|-----------------|
| **extract_educational_content.py** | ⭐ Главный инструмент для учебного контента с высоким качеством | `python extract_educational_content.py file.pdf -o output/` |
| **batch_extract_educational.py** | Пакетная обработка множества PDF файлов | `python batch_extract_educational.py folder/ -o output/` |
| **extract_pdf.py** | Базовый инструмент для простого извлечения | `python extract_pdf.py file.pdf -o output.md` |

### Вспомогательные скрипты

| Файл | Назначение | Команда запуска |
|------|-----------|-----------------|
| **check_install.py** | Проверка установки всех зависимостей | `python check_install.py` |
| **demo_educational_extraction.py** | Демонстрация возможностей с примерами | `python demo_educational_extraction.py` |
| **example_usage.py** | Примеры использования базового инструмента | `python example_usage.py` |
| **install.sh** | Автоматическая установка зависимостей | `./install.sh` |

## 📊 Сравнение инструментов

### extract_educational_content.py vs extract_pdf.py

| Функция | extract_educational_content.py | extract_pdf.py |
|---------|-------------------------------|----------------|
| **Качество изображений** | ⭐⭐⭐⭐⭐ Настраиваемое (1x-4x) | ⭐⭐⭐ Стандартное |
| **Режимы изображений** | ✅ REFERENCED + EMBEDDED | ⚠️ Только базовый |
| **Извлечение таблиц** | ✅ С сохранением структуры | ✅ Базовое |
| **Форматы экспорта** | ✅ MD + HTML + JSON + README | ✅ MD / HTML / JSON |
| **Организация файлов** | ✅ Полный пакет с папками | ⚠️ Отдельные файлы |
| **HTML стилизация** | ✅ Красивый CSS | ⚠️ Базовый HTML |
| **Метаданные** | ✅ Автоматический README | ❌ Нет |
| **Сложность** | Средняя | Простая |
| **Использование** | Учебный контент, курсы | Быстрое извлечение |

**Рекомендация:**
- Для **учебных материалов** → `extract_educational_content.py` ⭐
- Для **быстрого просмотра** → `extract_pdf.py`

## 🎯 Сценарии использования

### Сценарий 1: Одна презентация

**Цель:** Извлечь презентацию с картинками для редактирования

```bash
# Использовать:
python extract_educational_content.py lecture.pdf -o output/ --image-scale 2.5

# Результат:
output/
├── lecture.md              # Markdown с ссылками на картинки
├── lecture.html            # HTML для просмотра
├── lecture_images/         # Все картинки отдельно
└── README.md              # Информация о пакете
```

**Документация:** [EDUCATIONAL_CONTENT_GUIDE.md - Презентации](EDUCATIONAL_CONTENT_GUIDE.md#1-презентация-powerpoint--pdf)

---

### Сценарий 2: Учебник (большой PDF)

**Цель:** Извлечь главу учебника с таблицами и формулами

```bash
python extract_educational_content.py textbook_chapter.pdf \
    -o output/ \
    --all-formats \
    --image-scale 2.0
```

**Документация:** [EDUCATIONAL_CONTENT_GUIDE.md - Учебники](EDUCATIONAL_CONTENT_GUIDE.md#2-учебник)

---

### Сценарий 3: Сканированный документ

**Цель:** Распознать текст из скана с помощью OCR

```bash
python extract_educational_content.py scanned.pdf \
    -o output/ \
    --ocr \
    --image-scale 3.0 \
    --all-formats
```

**Документация:** [EDUCATIONAL_CONTENT_GUIDE.md - Сканированные](EDUCATIONAL_CONTENT_GUIDE.md#3-лекционные-записи-отсканированные)

---

### Сценарий 4: Целый курс (много файлов)

**Цель:** Обработать все лекции курса

```bash
python batch_extract_educational.py course_materials/ \
    -o extracted_course/ \
    --recursive \
    --all-formats \
    --parallel \
    --workers 4
```

**Результат:**
```
extracted_course/
├── lecture_01/
│   ├── lecture_01.md
│   ├── lecture_01.html
│   ├── lecture_01_images/
│   └── README.md
├── lecture_02/
│   └── ...
├── BATCH_REPORT.md        # Отчет о пакетной обработке
└── batch_report.json
```

**Документация:** [EDUCATIONAL_CONTENT_GUIDE.md - Целый курс](EDUCATIONAL_CONTENT_GUIDE.md#5-целый-курс-множество-файлов)

---

### Сценарий 5: Быстрый просмотр

**Цель:** Быстро посмотреть содержимое PDF

```bash
# Простой инструмент для скорости
python extract_pdf.py document.pdf --print
```

**Документация:** [README.md - Базовое использование](README.md#базовый-инструмент---простое-извлечение)

## 🔍 Поиск по задаче

### "Мне нужно..."

| Задача | Решение | Файл документации |
|--------|---------|-------------------|
| Извлечь презентацию с картинками | `extract_educational_content.py` | [EDUCATIONAL_CONTENT_GUIDE.md](EDUCATIONAL_CONTENT_GUIDE.md) |
| Быстро посмотреть текст PDF | `extract_pdf.py --print` | [README.md](README.md) |
| Обработать 50 лекций | `batch_extract_educational.py` | [EDUCATIONAL_CONTENT_GUIDE.md](EDUCATIONAL_CONTENT_GUIDE.md) |
| Распознать сканированный документ | `--ocr` опция | [EDUCATIONAL_CONTENT_GUIDE.md](EDUCATIONAL_CONTENT_GUIDE.md#3-лекционные-записи-отсканированные) |
| Получить HTML с картинками | `--all-formats` | [EDUCATIONAL_CONTENT_GUIDE.md](EDUCATIONAL_CONTENT_GUIDE.md#режимы-извлечения-изображений) |
| Понять как работает архитектура | Читать документацию | [ARCHITECTURE_SUMMARY.md](ARCHITECTURE_SUMMARY.md) |
| Настроить качество картинок | `--image-scale 3.0` | [EDUCATIONAL_CONTENT_GUIDE.md](EDUCATIONAL_CONTENT_GUIDE.md#настройка-качества-извлечения) |
| Только Markdown без HTML | `-f markdown` | [README.md](README.md) |
| Проверить установку | `check_install.py` | [QUICKSTART.md](QUICKSTART.md) |

## 📦 Структура проекта

```
GR_final/
│
├── 📖 ДОКУМЕНТАЦИЯ
│   ├── README.md                          # Общее описание
│   ├── QUICKSTART.md                      # Быстрый старт
│   ├── EDUCATIONAL_CONTENT_GUIDE.md       # 📚 Главное руководство
│   ├── ARCHITECTURE_SUMMARY.md            # Техническая документация
│   └── INDEX.md                           # Этот файл
│
├── 🛠️ ОСНОВНЫЕ ИНСТРУМЕНТЫ
│   ├── extract_educational_content.py     # ⭐ Главный инструмент
│   ├── batch_extract_educational.py       # Пакетная обработка
│   └── extract_pdf.py                     # Базовый инструмент
│
├── 🔧 ВСПОМОГАТЕЛЬНЫЕ СКРИПТЫ
│   ├── demo_educational_extraction.py     # Демонстрации
│   ├── example_usage.py                   # Примеры
│   ├── check_install.py                   # Проверка установки
│   └── install.sh                         # Установщик
│
├── 📋 КОНФИГУРАЦИЯ
│   └── requirements.txt                   # Зависимости Python
│
└── 📁 ДАННЫЕ (ваши файлы)
    ├── 1.txt, 2.txt, 3.txt, 4.txt        # Исследовательские файлы
    └── intro.txt                          # План работ
```

## 🚀 Рекомендуемый порядок изучения

### Для новичков

1. **Установка** → Запустите `./install.sh` или `pip install docling`
2. **Проверка** → Запустите `python check_install.py`
3. **Быстрый старт** → Прочитайте [QUICKSTART.md](QUICKSTART.md)
4. **Первый запуск** → `python extract_educational_content.py sample.pdf -o output/`
5. **Изучение результата** → Откройте `output/README.md`

### Для продвинутых

1. **Архитектура** → Изучите [ARCHITECTURE_SUMMARY.md](ARCHITECTURE_SUMMARY.md)
2. **Полное руководство** → Прочитайте [EDUCATIONAL_CONTENT_GUIDE.md](EDUCATIONAL_CONTENT_GUIDE.md)
3. **Демонстрации** → Запустите `python demo_educational_extraction.py`
4. **Кастомизация** → Изучите код `extract_educational_content.py`
5. **Интеграция** → Используйте как модуль в своих проектах

## 📚 Внешние ресурсы

### Документация Docling

- [Официальный сайт](https://docling-project.github.io/docling/)
- [Архитектура](https://docling-project.github.io/docling/concepts/architecture/)
- [DoclingDocument](https://docling-project.github.io/docling/concepts/docling_document/)
- [Serialization](https://docling-project.github.io/docling/concepts/serialization/)
- [Document Converter API](https://docling-project.github.io/docling/reference/document_converter/)
- [Pipeline Options](https://docling-project.github.io/docling/reference/pipeline_options/)
- [Примеры](https://docling-project.github.io/docling/examples/)

### Интеграции

- [LangChain](https://docling-project.github.io/docling/integrations/langchain/)
- [LlamaIndex](https://docling-project.github.io/docling/integrations/llamaindex/)
- [Haystack](https://docling-project.github.io/docling/integrations/haystack/)

## ❓ FAQ - Быстрые ответы

**Q: С чего начать?**
A: Прочитайте [QUICKSTART.md](QUICKSTART.md) и запустите `check_install.py`

**Q: Какой инструмент использовать?**
A: Для учебного контента → `extract_educational_content.py`, для быстрого просмотра → `extract_pdf.py`

**Q: Как обработать много файлов?**
A: Используйте `batch_extract_educational.py` с флагом `--parallel`

**Q: Картинки плохого качества?**
A: Увеличьте `--image-scale` до 3.0 или 4.0

**Q: Нужен OCR для скана?**
A: Добавьте флаг `--ocr` к команде

**Q: Как получить HTML с картинками?**
A: Используйте `--all-formats` для создания HTML с embedded изображениями

**Q: Где найти извлеченные файлы?**
A: В указанной `-o` директории, структура описана в `README.md` каждого пакета

**Q: Можно ли изменить стили HTML?**
A: Да, отредактируйте метод `_add_html_styling()` в `extract_educational_content.py`

**Q: Как использовать в своем коде?**
A: См. раздел "Программное использование" в [EDUCATIONAL_CONTENT_GUIDE.md](EDUCATIONAL_CONTENT_GUIDE.md#-программное-использование)

## 🆘 Получение помощи

1. **Проблемы с установкой** → [QUICKSTART.md - Проверка установки](QUICKSTART.md#проверка-установки)
2. **Ошибки при извлечении** → [EDUCATIONAL_CONTENT_GUIDE.md - Troubleshooting](EDUCATIONAL_CONTENT_GUIDE.md#-troubleshooting)
3. **Вопросы по архитектуре** → [ARCHITECTURE_SUMMARY.md](ARCHITECTURE_SUMMARY.md)
4. **Примеры использования** → [EDUCATIONAL_CONTENT_GUIDE.md - Примеры](EDUCATIONAL_CONTENT_GUIDE.md#-примеры-для-разных-типов-учебных-материалов)

## 📝 Итоговые рекомендации

### Для разных типов контента

| Тип контента | Инструмент | Команда | Время обработки |
|--------------|-----------|---------|-----------------|
| **Презентация (10-30 слайдов)** | extract_educational_content.py | `--image-scale 2.5` | ~30 сек |
| **Учебник (глава 20-50 стр)** | extract_educational_content.py | `--all-formats` | ~1-2 мин |
| **Сканированный документ** | extract_educational_content.py | `--ocr --image-scale 3.0` | ~2-5 мин |
| **Курс (20-50 лекций)** | batch_extract_educational.py | `--parallel --workers 4` | ~10-30 мин |
| **Быстрый просмотр** | extract_pdf.py | `--print` | ~5 сек |

### Качество vs Скорость

```
┌─────────────────────────────────────────┐
│  Быстро          ←→          Качественно │
├─────────────────────────────────────────┤
│  extract_pdf.py              ⚡⚡⚡⚡⚡    │
│  --image-scale 1.0           ⚡⚡⚡⚡     │
│  --image-scale 2.0 (⭐)      ⚡⚡⚡      │
│  --image-scale 3.0           ⚡⚡       │
│  --image-scale 4.0 + --ocr   ⚡        │
└─────────────────────────────────────────┘
```

**Золотая середина:** `--image-scale 2.0` без OCR

---

**Последнее обновление:** 2025-10-01

**Версия проекта:** 2.0

**Основано на:** Docling v2.x

**Автор решения:** Разработано на основе [официальной документации Docling](https://docling-project.github.io/docling/)

