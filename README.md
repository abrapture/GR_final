# Извлечение содержимого из PDF презентаций с помощью Docling

Этот проект использует библиотеку [Docling](https://docling-project.github.io/docling/) для извлечения содержимого из PDF презентаций с расширенным пониманием структуры документов.

## 🎓 Два варианта инструментов

### 1. **extract_pdf.py** - Базовый инструмент
Простое извлечение текста из PDF в различные форматы.

### 2. **extract_educational_content.py** - Продвинутый инструмент ⭐
Специально разработан для учебных материалов с максимальным сохранением качества:
- 📸 Извлечение изображений в высоком качестве (масштабируется до 4x)
- 🖼️ Два режима работы с изображениями: REFERENCED (отдельные файлы) и EMBEDDED (встроенные)
- 📊 Продвинутое извлечение таблиц с сохранением структуры
- 📐 Полная иерархия документа (заголовки, разделы, списки)
- 🎨 HTML экспорт с красивым CSS
- 📦 Полный пакет в разных форматах
- 📝 Автоматические README и отчеты

## Возможности

- 📄 **Извлечение текста из PDF** с сохранением структуры
- 📊 **Распознавание таблиц** и их структуры
- 🖼️ **Извлечение изображений и графиков** в оригинальном качестве
- 📐 **Сохранение иерархии документа** (заголовки, разделы, списки)
- 📑 **Определение порядка чтения** и макета страниц
- 🔄 **Множественные форматы экспорта**: Markdown, HTML, JSON
- 👓 **Поддержка OCR** для сканированных документов
- 📦 **Пакетная обработка** нескольких файлов
- ⚡ **Параллельная обработка** для скорости
- 🔒 **Локальное выполнение** без отправки данных во внешние сервисы

## Установка

### 1. Установка зависимостей

```bash
# Установка основной библиотеки
pip install -r requirements.txt

# Или напрямую
pip install docling
```

### 2. Опциональные зависимости

Для OCR (распознавание сканированных документов):
```bash
pip install easyocr
# или
pip install pytesseract
```

## Использование

### 🚀 Быстрый старт - Учебный контент (рекомендуется)

```bash
# Извлечь презентацию со всеми изображениями
python extract_educational_content.py lecture.pdf -o output/

# Полный пакет (Markdown + HTML + JSON)
python extract_educational_content.py textbook.pdf -o output/ --all-formats

# Высокое качество изображений для диаграмм
python extract_educational_content.py presentation.pdf -o output/ --image-scale 3.0

# С OCR для сканированных документов
python extract_educational_content.py scanned.pdf -o output/ --ocr

# Пакетная обработка целой директории
python batch_extract_educational.py course_materials/ -o output/ --recursive
```

**📖 Подробное руководство:** См. [EDUCATIONAL_CONTENT_GUIDE.md](EDUCATIONAL_CONTENT_GUIDE.md)

---

### Базовый инструмент - Простое извлечение

#### Командная строка

```bash
# Извлечь содержимое в Markdown
python extract_pdf.py presentation.pdf

# Сохранить результат в файл
python extract_pdf.py presentation.pdf -o output.md

# Экспорт в HTML
python extract_pdf.py presentation.pdf -f html -o output.html

# Экспорт в JSON
python extract_pdf.py presentation.pdf -f json -o output.json
```

#### Пакетная обработка
```bash
# Обработать несколько файлов
python extract_pdf.py file1.pdf file2.pdf file3.pdf -o output_dir/

# С использованием маски
python extract_pdf.py *.pdf -o output/
```

#### Сканированные документы
```bash
# Использовать OCR для сканированных PDF
python extract_pdf.py scanned.pdf --ocr -o output.md
```

#### Вывод в консоль
```bash
# Показать результат в терминале
python extract_pdf.py presentation.pdf --print
```

### Программное использование

#### Пример 1: Базовое извлечение

```python
from pathlib import Path
from extract_pdf import PDFExtractor

# Создать экстрактор
extractor = PDFExtractor()

# Извлечь содержимое
content = extractor.extract_single_file(
    Path("presentation.pdf"), 
    output_format="markdown"
)

# Сохранить результат
extractor.save_to_file(content, Path("output.md"))
```

#### Пример 2: Пакетная обработка

```python
from pathlib import Path
from extract_pdf import PDFExtractor

extractor = PDFExtractor()

# Список файлов
pdf_files = [
    Path("presentation1.pdf"),
    Path("presentation2.pdf"),
    Path("presentation3.pdf"),
]

# Обработать все файлы
results = extractor.extract_multiple_files(pdf_files, output_format="markdown")

# Сохранить результаты
for filename, content in results.items():
    output_path = Path(f"output/{filename}.md")
    extractor.save_to_file(content, output_path)
```

#### Пример 3: С использованием OCR

```python
from pathlib import Path
from extract_pdf import PDFExtractor

# Создать экстрактор с OCR
extractor = PDFExtractor(use_ocr=True)

# Обработать сканированный документ
content = extractor.extract_single_file(
    Path("scanned.pdf"), 
    output_format="markdown"
)

extractor.save_to_file(content, Path("scanned_output.md"))
```

#### Пример 4: Работа с объектом документа

```python
from pathlib import Path
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("presentation.pdf")

# Получить объект документа
doc = result.document

# Различные форматы экспорта
markdown = doc.export_to_markdown()
html = doc.export_to_html()
json_data = doc.export_to_json()

# Информация о документе
print(f"Название: {doc.name}")
print(f"Страниц: {len(doc.pages)}")
```

## Поддерживаемые форматы вывода

| Формат | Описание | Расширение |
|--------|----------|------------|
| `markdown` | Markdown разметка (по умолчанию) | `.md` |
| `html` | HTML разметка | `.html` |
| `json` | JSON структура документа | `.json` |
| `doctags` | Токены документа | `.txt` |

## Структура проекта

```
GR_final/
├── extract_pdf.py                      # Базовый инструмент извлечения
├── extract_educational_content.py      # ⭐ Продвинутый инструмент для учебного контента
├── batch_extract_educational.py        # Пакетная обработка множества файлов
├── example_usage.py                    # Примеры использования базового инструмента
├── requirements.txt                    # Зависимости проекта
├── README.md                          # Общая документация
├── EDUCATIONAL_CONTENT_GUIDE.md       # 📖 Подробное руководство
├── QUICKSTART.md                      # Быстрый старт
├── check_install.py                   # Проверка установки
├── install.sh                         # Скрипт установки (Unix/Mac)
└── output/                            # Директория для результатов
```

## Расширенные возможности Docling

### Извлечение таблиц

Docling автоматически распознает и извлекает таблицы с сохранением их структуры:

```python
converter = DocumentConverter()
result = converter.convert("document_with_tables.pdf")
markdown = result.document.export_to_markdown()
# Таблицы будут в формате Markdown tables
```

### Извлечение изображений

```python
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions

# Настройка для экспорта изображений
pipeline_options = PdfPipelineOptions()
pipeline_options.images_scale = 2.0  # Масштаб изображений

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

### Обработка формул

Docling может распознавать математические формулы в PDF:

```python
result = converter.convert("scientific_paper.pdf")
# Формулы будут извлечены и представлены в подходящем формате
```

## Примеры использования

Запустите файл с примерами:

```bash
python example_usage.py
```

Этот скрипт демонстрирует различные сценарии использования библиотеки.

## Troubleshooting

### Ошибка импорта Docling

```bash
pip install --upgrade docling
```

### Проблемы с OCR

Убедитесь, что установлены необходимые библиотеки:
```bash
pip install easyocr pytesseract
```

Для pytesseract также нужно установить Tesseract:
- **macOS**: `brew install tesseract`
- **Ubuntu**: `sudo apt-get install tesseract-ocr`
- **Windows**: Скачайте с [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Медленная обработка

Для ускорения обработки можно использовать GPU (если доступен):
```bash
pip install torch torchvision
```

## Дополнительные ресурсы

- 📚 [Документация Docling](https://docling-project.github.io/docling/)
- 🔗 [GitHub репозиторий](https://github.com/docling-project/docling)
- 💬 [Примеры использования](https://docling-project.github.io/docling/examples/simple-conversion/)
- 🤖 [Интеграции с AI фреймворками](https://docling-project.github.io/docling/integrations/)

## Лицензия

Этот проект использует библиотеку Docling, которая распространяется под лицензией MIT.

## Контакты

Для вопросов и предложений создавайте issues в репозитории проекта.

