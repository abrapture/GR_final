# Архитектура решения для извлечения учебного контента

## 📐 Обзор архитектуры Docling

Согласно [официальной документации](https://docling-project.github.io/docling/concepts/architecture/), архитектура Docling состоит из следующих компонентов:

```
┌─────────────────────────────────────────────────────────────┐
│                     Document Converter                       │
│  (Главный компонент для конвертации документов)              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ├──► Format-specific Backend
                        │    (PDF, DOCX, PPTX, etc.)
                        │
                        ├──► Pipeline & Options
                        │    (Настройки обработки)
                        │
                        └──► Conversion Result
                             │
                             └──► DoclingDocument
                                  (Унифицированное представление)
                                  │
                                  ├──► Export Methods
                                  │    (Markdown, HTML, JSON)
                                  │
                                  ├──► Serializers
                                  │    (Кастомизация вывода)
                                  │
                                  └──► Chunkers
                                       (Разбиение на части)
```

## 🎯 Наше решение: Оптимальная конфигурация для учебного контента

### 1. Pipeline Options - Настройка обработки

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions()

# КЛЮЧЕВЫЕ НАСТРОЙКИ для учебного контента:

# 1. Извлечение структуры таблиц
pipeline_options.do_table_structure = True
# → Сохраняет строки, столбцы, объединенные ячейки

# 2. Генерация изображений
pipeline_options.generate_picture_images = True
# → Извлекает изображения в PIL Image формат

# 3. Масштаб изображений (критично для качества!)
pipeline_options.images_scale = 2.0  # 1.0-4.0
# → 1.0x = низкое качество, быстро
# → 2.0x = стандарт (РЕКОМЕНДУЕТСЯ)
# → 3.0x = высокое качество для диаграмм
# → 4.0x = максимум для технических чертежей

# 4. OCR для сканированных документов
pipeline_options.do_ocr = False  # True для сканов
# → Использует EasyOCR или Tesseract
```

### 2. DoclingDocument - Структура данных

[DoclingDocument](https://docling-project.github.io/docling/concepts/docling_document/) - это pydantic модель с полной иерархией:

```python
doc = result.document

# Основные коллекции элементов:
doc.texts       # List[TextItem] - все текстовые элементы
                # • paragraph
                # • section_header
                # • list_item
                # • code
                # • formula

doc.tables      # List[TableItem] - таблицы со структурой
                # • num_rows, num_cols
                # • grid structure
                # • cell data

doc.pictures    # List[PictureItem] - изображения
                # • PIL Image
                # • bounding box
                # • classification

doc.key_value_items  # List[KeyValueItem] - метаданные

# Структура документа:
doc.body        # NodeItem - дерево основного контента
doc.furniture   # NodeItem - заголовки, подвалы
doc.groups      # Set[NodeItem] - списки, главы

# Метаданные:
doc.name        # Название документа
doc.origin      # Источник
```

### 3. Image Reference Modes - Режимы работы с изображениями

Согласно [документации по сериализации](https://docling-project.github.io/docling/concepts/serialization/#examples):

```python
from docling_core.types.doc import ImageRefMode

# РЕЖИМ 1: REFERENCED - Ссылки на файлы
markdown = doc.export_to_markdown(image_mode=ImageRefMode.REFERENCED)
# Результат: ![Image](path/to/image.png)
# 
# ✅ Преимущества:
# • Изображения в отдельных файлах
# • Можно редактировать независимо
# • Меньше размер Markdown
# • Подходит для Git
#
# ❌ Недостатки:
# • Нужно управлять файлами
# • Могут потеряться ссылки

# РЕЖИМ 2: EMBEDDED - Встроенные (base64)
html = doc.export_to_html(image_mode=ImageRefMode.EMBEDDED)
# Результат: <img src="data:image/png;base64,iVBORw0...">
#
# ✅ Преимущества:
# • Один самодостаточный файл
# • Не теряются ссылки
# • Легко распространять
#
# ❌ Недостатки:
# • Больший размер файла
# • Сложнее редактировать
```

**Наша рекомендация для учебного контента:**
- Markdown → REFERENCED (для редактирования, Git)
- HTML → EMBEDDED (для просмотра, архивирования)

### 4. Export Methods - Форматы вывода

```python
# 1. MARKDOWN - для редактирования и Git
markdown = doc.export_to_markdown(
    image_mode=ImageRefMode.REFERENCED
)
# • Сохраняет структуру
# • Таблицы в Markdown формате
# • Ссылки на изображения
# • Легко читается и редактируется

# 2. HTML - для просмотра в браузере
html = doc.export_to_html(
    image_mode=ImageRefMode.EMBEDDED
)
# • Самодостаточный файл
# • Встроенные изображения (base64)
# • Можно добавить CSS для стилизации

# 3. JSON - для программной обработки
json_str = doc.export_to_json()
# • Полная структура документа
# • Все метаданные
# • Для анализа и дальнейшей обработки

# 4. DICT - для Python обработки
doc_dict = doc.export_to_dict()
# • Python словарь
# • Для программной манипуляции
```

## 🏗️ Архитектура нашего решения

### Компоненты системы

```
┌────────────────────────────────────────────────────────────┐
│  EducationalContentExtractor                                │
│  (Основной класс для извлечения учебного контента)          │
└─────────────────┬──────────────────────────────────────────┘
                  │
                  ├──► Document Converter
                  │    • PdfFormatOption с оптимальными настройками
                  │    • PdfPipelineOptions для качества
                  │
                  ├──► extract_document()
                  │    • Конвертация PDF → DoclingDocument
                  │    • Статистика контента
                  │
                  ├──► export_to_markdown_with_images()
                  │    • REFERENCED режим
                  │    • Отдельная папка для изображений
                  │    • Сохранение всех картинок
                  │
                  ├──► export_to_html_with_images()
                  │    • EMBEDDED режим
                  │    • Base64 изображения
                  │    • Красивый CSS
                  │
                  ├──► export_to_json()
                  │    • Полная структура
                  │
                  └──► export_complete_package()
                       • Все форматы сразу
                       • README с метаданными
                       • Организованная структура папок
```

### Workflow обработки документа

```
1. INPUT: PDF файл
   ↓
2. CONFIGURATION: PdfPipelineOptions
   • images_scale = 2.0-3.0
   • do_table_structure = True
   • generate_picture_images = True
   • do_ocr = (если нужно)
   ↓
3. CONVERSION: DocumentConverter
   • PDF Backend обрабатывает файл
   • Pipeline применяет настройки
   • Создается DoclingDocument
   ↓
4. DOCLING DOCUMENT:
   ├─► texts[] - все текстовые элементы с типами
   ├─► tables[] - таблицы со структурой
   ├─► pictures[] - изображения PIL Image
   └─► body - иерархия документа
   ↓
5. EXPORT:
   ├─► Markdown + папка images/
   │   • ImageRefMode.REFERENCED
   │   • Отдельные PNG файлы
   │
   ├─► HTML (самодостаточный)
   │   • ImageRefMode.EMBEDDED
   │   • Base64 images
   │   • CSS стилизация
   │
   └─► JSON (структура)
       • Полные метаданные
   ↓
6. OUTPUT: Организованный пакет
   document/
   ├── document.md
   ├── document.html
   ├── document_structure.json
   ├── document_images/
   │   ├── image_001.png
   │   └── ...
   └── README.md
```

## 🎓 Оптимизации для учебного контента

### 1. Качество изображений

**Проблема:** Учебный контент часто содержит диаграммы, графики, схемы, которые должны быть четкими.

**Решение:**
```python
pipeline_options.images_scale = 2.5  # Увеличено с базового 1.0
```

**Результат:**
- Диаграммы четкие и читаемые
- Текст на картинках различим
- Графики сохраняют детали

### 2. Структура таблиц

**Проблема:** Таблицы с данными должны сохранять свою структуру.

**Решение:**
```python
pipeline_options.do_table_structure = True
```

**Результат:**
- Строки и столбцы сохраняются
- Объединенные ячейки обрабатываются
- Экспорт в Markdown table формат

### 3. Два режима изображений

**Проблема:** Разные сценарии использования требуют разных форматов.

**Решение:** Создаем оба варианта:
```python
# Для редактирования (Git, совместная работа)
markdown = export_to_markdown_with_images()  # REFERENCED

# Для архивирования (email, хранение)
html = export_to_html_with_images()  # EMBEDDED
```

**Результат:**
- Markdown для работы с текстом
- HTML для просмотра и распространения

### 4. Метаданные и README

**Проблема:** Нужна информация о том, как документ был извлечен.

**Решение:** Автоматическое создание README:
```python
def _create_package_readme():
    # Создает README.md с:
    # • Датой извлечения
    # • Статистикой (тексты, таблицы, изображения)
    # • Описанием файлов
    # • Рекомендациями по использованию
```

**Результат:**
- Полная документация пакета
- Легко понять, что и как использовать

### 5. Пакетная обработка

**Проблема:** Курсы содержат десятки лекций.

**Решение:** BatchEducationalExtractor:
```python
# Обработка всей директории
batch_extractor.process_directory(
    input_dir=lectures/,
    parallel=True,  # Параллельная обработка
    workers=4,      # 4 потока
)
```

**Результат:**
- Быстрая обработка множества файлов
- Автоматический отчет
- Организованная структура вывода

## 📊 Сравнение с альтернативами

| Метод | Качество | Структура | Изображения | Таблицы | Скорость |
|-------|----------|-----------|-------------|---------|----------|
| **Docling (наше решение)** | ⭐⭐⭐⭐⭐ | ✅ Полная | ✅ Высокое качество | ✅ Со структурой | ⭐⭐⭐⭐ |
| PyPDF2 | ⭐⭐ | ❌ Теряется | ❌ Не извлекает | ❌ Текстом | ⭐⭐⭐⭐⭐ |
| pdfplumber | ⭐⭐⭐ | ⚠️ Частично | ⚠️ Низкое | ⚠️ Частично | ⭐⭐⭐⭐ |
| Adobe Acrobat | ⭐⭐⭐⭐ | ✅ Хорошо | ✅ Хорошо | ✅ Хорошо | ⭐⭐⭐ |
| OCR (Tesseract) | ⭐⭐⭐ | ❌ Нет | ✅ Для сканов | ❌ Нет | ⭐⭐ |

**Вывод:** Docling предоставляет лучший баланс качества, функциональности и скорости для учебного контента.

## 🚀 Итоговые преимущества нашего решения

1. **Полнота извлечения:**
   - Текст с сохранением иерархии
   - Изображения в высоком качестве
   - Таблицы со структурой
   - Формулы и специальные символы

2. **Гибкость форматов:**
   - Markdown для редактирования
   - HTML для просмотра
   - JSON для обработки

3. **Два режима изображений:**
   - REFERENCED для работы
   - EMBEDDED для архивирования

4. **Автоматизация:**
   - Пакетная обработка
   - Параллельные потоки
   - Автоматические отчеты

5. **Локальность:**
   - Все обработка локально
   - Нет отправки данных
   - Полный контроль

6. **Расширяемость:**
   - Открытый код
   - Кастомизация под задачи
   - Интеграция с AI фреймворками

## 📚 Ссылки на документацию

- [Архитектура Docling](https://docling-project.github.io/docling/concepts/architecture/)
- [DoclingDocument](https://docling-project.github.io/docling/concepts/docling_document/)
- [Serialization](https://docling-project.github.io/docling/concepts/serialization/)
- [Document Converter API](https://docling-project.github.io/docling/reference/document_converter/)
- [Pipeline Options](https://docling-project.github.io/docling/reference/pipeline_options/)

## 🎯 Заключение

Наше решение основано на глубоком понимании архитектуры Docling и оптимизировано специально для извлечения учебного контента. Мы используем:

- **PdfPipelineOptions** с оптимальными настройками качества
- **DoclingDocument** для полного представления структуры
- **ImageRefMode** для гибкой работы с изображениями
- **Export methods** для множества форматов вывода
- **Batch processing** для эффективной обработки курсов

Результат: **максимально качественное извлечение учебного контента с сохранением всех элементов и структуры документа.**

