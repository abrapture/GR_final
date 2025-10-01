# Руководство по извлечению учебного контента с использованием Docling

## 🎯 Цель

Это руководство описывает наиболее эффективный способ извлечения учебной информации из PDF документов (презентаций, лекций, учебников) с сохранением:
- Всех изображений и графиков в оригинальном качестве
- Таблиц с их структурой
- Иерархии документа (заголовки, разделы)
- Формул и специальных символов
- Порядка чтения и макета

## 📐 Архитектура решения

Решение основано на [архитектуре Docling](https://docling-project.github.io/docling/concepts/architecture/):

```
PDF документ
    ↓
Document Converter (с PdfFormatOption)
    ↓
Pipeline с настройками:
  • do_table_structure = True
  • generate_picture_images = True
  • images_scale = 2.0+
  • do_ocr = True (для сканированных)
    ↓
DoclingDocument (унифицированный формат)
  • texts[] - все текстовые элементы
  • tables[] - таблицы со структурой
  • pictures[] - изображения
  • body - иерархия документа
    ↓
Export с разными режимами:
  • Markdown + изображения (REFERENCED)
  • HTML + embedded изображения (EMBEDDED)
  • JSON структура
```

## 🚀 Быстрый старт

### 1. Установка

```bash
# Базовая установка
pip install docling

# Для OCR (опционально)
pip install easyocr pytesseract
```

### 2. Извлечение одного документа

```bash
# Базовое использование
python extract_educational_content.py lecture.pdf -o output/

# С высоким качеством изображений
python extract_educational_content.py presentation.pdf -o output/ --image-scale 3.0

# Все форматы (MD + HTML + JSON)
python extract_educational_content.py textbook.pdf -o output/ --all-formats

# С OCR для сканированных документов
python extract_educational_content.py scanned.pdf -o output/ --ocr
```

### 3. Пакетная обработка

```bash
# Обработать всю директорию
python batch_extract_educational.py lectures/ -o output/

# Рекурсивно со всеми поддиректориями
python batch_extract_educational.py course_materials/ -o output/ --recursive

# Параллельная обработка
python batch_extract_educational.py docs/ -o output/ --parallel --workers 4
```

## 📚 Детальное использование

### Режимы извлечения изображений

Docling поддерживает два режима работы с изображениями (согласно [документации](https://docling-project.github.io/docling/concepts/serialization/#examples)):

#### 1. REFERENCED - Ссылки на файлы (рекомендуется для Markdown)

```python
from extract_educational_content import EducationalContentExtractor

extractor = EducationalContentExtractor(
    extract_images=True,
    image_resolution_scale=2.0  # Масштаб: 1.0-4.0
)

doc = extractor.extract_document(pdf_path)

# Экспорт с отдельными файлами изображений
md_path = extractor.export_to_markdown_with_images(
    doc, output_dir, "document"
)
```

**Результат:**
```
output/
├── document.md                 # Markdown с ссылками типа ![](document_images/image_001.png)
└── document_images/
    ├── image_001.png
    ├── image_002.png
    └── ...
```

**Преимущества:**
- ✅ Изображения можно редактировать отдельно
- ✅ Меньший размер Markdown файла
- ✅ Подходит для Git и систем контроля версий
- ✅ Можно заменить изображения без изменения текста

#### 2. EMBEDDED - Встроенные изображения (рекомендуется для HTML)

```python
# Экспорт HTML с base64 embedded изображениями
html_path = extractor.export_to_html_with_images(
    doc, output_dir, "document"
)
```

**Результат:**
```
output/
└── document.html              # Самодостаточный файл со всеми изображениями
```

**Преимущества:**
- ✅ Один файл содержит всё
- ✅ Легко распространять
- ✅ Не нужны внешние файлы
- ✅ Открывается в любом браузере

### Настройка качества извлечения

#### Масштаб изображений

```python
# Низкое качество - быстрее, меньше размер
extractor = EducationalContentExtractor(image_resolution_scale=1.0)

# Среднее качество (по умолчанию)
extractor = EducationalContentExtractor(image_resolution_scale=2.0)

# Высокое качество - для печати, диаграмм
extractor = EducationalContentExtractor(image_resolution_scale=3.0)

# Максимальное качество - для детальных чертежей
extractor = EducationalContentExtractor(image_resolution_scale=4.0)
```

#### Таблицы

```python
# С извлечением структуры таблиц (рекомендуется)
extractor = EducationalContentExtractor(extract_tables=True)

# Без таблиц - быстрее, но теряется структура
extractor = EducationalContentExtractor(extract_tables=False)
```

#### OCR для сканированных документов

```python
# Включить OCR
extractor = EducationalContentExtractor(use_ocr=True)
```

**Когда использовать OCR:**
- ✅ Документ отсканирован с бумаги
- ✅ PDF содержит изображения страниц
- ✅ Текст не выделяется в PDF
- ❌ Не нужен для "нормальных" PDF с текстовым слоем

## 🎓 Примеры для разных типов учебных материалов

### 1. Презентация (PowerPoint → PDF)

```bash
# Презентации обычно содержат много изображений и диаграмм
python extract_educational_content.py lecture_slides.pdf \
    -o output/ \
    --image-scale 2.5 \
    --all-formats
```

**Особенности:**
- Много визуального контента
- Минимум текста на слайд
- Важны диаграммы и схемы

### 2. Учебник

```bash
# Учебники - большие, много таблиц и формул
python extract_educational_content.py textbook_chapter.pdf \
    -o output/ \
    --image-scale 2.0 \
    -f markdown html
```

**Особенности:**
- Длинные тексты
- Структурированные разделы
- Таблицы и формулы

### 3. Лекционные записи (отсканированные)

```bash
# Рукописные или отсканированные материалы
python extract_educational_content.py handwritten_notes.pdf \
    -o output/ \
    --ocr \
    --image-scale 3.0 \
    --all-formats
```

**Особенности:**
- Нужен OCR
- Может потребоваться ручная проверка
- Высокое качество изображений

### 4. Научные статьи

```bash
# Статьи с графиками, таблицами данных
python extract_educational_content.py research_paper.pdf \
    -o output/ \
    --image-scale 2.5 \
    --all-formats
```

**Особенности:**
- Графики и charts
- Таблицы данных
- Формулы и уравнения
- Ссылки и цитаты

### 5. Целый курс (множество файлов)

```bash
# Пакетная обработка всех материалов курса
python batch_extract_educational.py course_materials/ \
    -o extracted_course/ \
    --recursive \
    --all-formats \
    --parallel \
    --workers 4
```

**Структура выходных файлов:**
```
extracted_course/
├── lecture_01/
│   ├── lecture_01.md
│   ├── lecture_01.html
│   ├── lecture_01_images/
│   └── README.md
├── lecture_02/
│   └── ...
├── BATCH_REPORT.md
└── batch_report.json
```

## 💡 Программное использование

### Базовый пример

```python
from pathlib import Path
from extract_educational_content import EducationalContentExtractor

# Создать экстрактор
extractor = EducationalContentExtractor(
    extract_images=True,
    extract_tables=True,
    image_resolution_scale=2.0,
)

# Извлечь документ
doc = extractor.extract_document(Path("lecture.pdf"))

# Экспорт в разные форматы
extractor.export_complete_package(
    doc=doc,
    output_dir=Path("output/lecture"),
    base_filename="lecture",
    formats=["markdown", "html", "json"],
)
```

### Работа с DoclingDocument напрямую

```python
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc import ImageRefMode

# Настройка pipeline
pipeline_options = PdfPipelineOptions()
pipeline_options.do_table_structure = True
pipeline_options.generate_picture_images = True
pipeline_options.images_scale = 2.5

# Создание конвертера
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

# Конвертация
result = converter.convert("document.pdf")
doc = result.document

# Доступ к элементам документа
print(f"Текстовых элементов: {len(doc.texts)}")
print(f"Таблиц: {len(doc.tables)}")
print(f"Изображений: {len(doc.pictures)}")

# Экспорт с разными режимами изображений
md_with_refs = doc.export_to_markdown(image_mode=ImageRefMode.REFERENCED)
html_embedded = doc.export_to_html(image_mode=ImageRefMode.EMBEDDED)
json_structure = doc.export_to_json()
```

### Анализ структуры документа

```python
# Получить иерархию заголовков
for text_item in doc.texts:
    if hasattr(text_item, 'label'):
        if 'heading' in text_item.label.lower():
            print(f"Заголовок: {text_item.text}")

# Извлечь все таблицы
for idx, table in enumerate(doc.tables):
    print(f"\nТаблица {idx + 1}:")
    # Таблица содержит структурированные данные
    if hasattr(table, 'data'):
        print(table.data)

# Сохранить изображения отдельно
for idx, picture in enumerate(doc.pictures):
    if hasattr(picture, 'image') and picture.image:
        picture.image.pil_image.save(f"image_{idx:03d}.png")
```

### Кастомная обработка

```python
from pathlib import Path
from extract_educational_content import EducationalContentExtractor

class CustomEducationalExtractor(EducationalContentExtractor):
    """Расширенный экстрактор с дополнительной обработкой."""
    
    def process_with_annotations(self, pdf_path: Path, output_dir: Path):
        """Извлечение с добавлением аннотаций."""
        # Извлечь документ
        doc = self.extract_document(pdf_path)
        
        # Добавить метаданные
        annotations = []
        
        # Анализ содержимого
        for text_item in doc.texts:
            if hasattr(text_item, 'text'):
                # Найти определения
                if 'определение:' in text_item.text.lower():
                    annotations.append({
                        'type': 'definition',
                        'text': text_item.text
                    })
                # Найти примеры
                elif 'пример:' in text_item.text.lower():
                    annotations.append({
                        'type': 'example',
                        'text': text_item.text
                    })
        
        # Экспорт с аннотациями
        results = self.export_complete_package(
            doc, output_dir, pdf_path.stem
        )
        
        # Сохранить аннотации отдельно
        import json
        annotations_path = output_dir / "annotations.json"
        annotations_path.write_text(
            json.dumps(annotations, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        return results, annotations

# Использование
extractor = CustomEducationalExtractor()
results, annotations = extractor.process_with_annotations(
    Path("lecture.pdf"),
    Path("output/")
)
```

## 🔧 Оптимизация производительности

### Для больших документов

```python
# Обработка по частям для экономии памяти
# (пока не поддерживается напрямую, но планируется)

# Текущий workaround: обработка по одному файлу
for pdf_file in pdf_files:
    extractor = EducationalContentExtractor()  # Новый экстрактор
    doc = extractor.extract_document(pdf_file)
    # ... обработка ...
    del doc  # Освободить память
```

### Параллельная обработка

```bash
# Использовать batch скрипт с параллелизмом
python batch_extract_educational.py docs/ \
    -o output/ \
    --parallel \
    --workers 4  # Количество ядер CPU
```

**Рекомендации по workers:**
- 2 workers - безопасно для большинства систем
- 4 workers - для систем с 8+ ядрами
- Не более CPU_cores - 1

### Управление памятью

```bash
# Отключить ненужные функции для экономии памяти
python extract_educational_content.py large_doc.pdf \
    -o output/ \
    --no-images \  # Если изображения не нужны
    -f markdown    # Только один формат
```

## 📊 Сравнение форматов вывода

| Формат | Размер | Редактирование | Изображения | Использование |
|--------|--------|----------------|-------------|---------------|
| **Markdown + изображения** | Средний | ✅ Легко | Отдельные файлы | Git, документация, блоги |
| **HTML embedded** | Большой | ❌ Сложно | Base64 внутри | Архивирование, email |
| **JSON структура** | Малый | 🔧 Программно | Метаданные | Анализ, обработка |

## ⚠️ Известные ограничения

### 1. Формулы

- ✅ Простые формулы распознаются
- ⚠️ Сложные LaTeX формулы могут требовать ручной проверки
- 💡 Используйте `--image-scale 3.0+` для лучшего качества

### 2. Таблицы

- ✅ Простые таблицы хорошо распознаются
- ⚠️ Объединенные ячейки могут терять структуру
- ⚠️ Вложенные таблицы упрощаются

### 3. Многоколоночный текст

- ✅ Порядок чтения обычно правильный
- ⚠️ Сложные макеты могут требовать проверки

### 4. OCR точность

- ✅ Хорошо для печатного текста
- ⚠️ Ошибки для рукописного текста
- ⚠️ Требует больше времени

## 🆘 Troubleshooting

### Проблема: Изображения не извлекаются

```bash
# Проверьте настройки
python extract_educational_content.py doc.pdf -o output/ \
    --image-scale 2.0  # Явно указать масштаб
```

### Проблема: Текст не распознается

```bash
# Включить OCR
python extract_educational_content.py doc.pdf -o output/ --ocr
```

### Проблема: Медленная обработка

```bash
# Отключить ненужное
python extract_educational_content.py doc.pdf -o output/ \
    --no-images \
    --no-tables
```

### Проблема: Недостаточно памяти

```python
# Обрабатывать файлы по одному
# Не использовать параллельную обработку
```

## 📖 Дополнительные ресурсы

- [Документация Docling](https://docling-project.github.io/docling/)
- [Архитектура Docling](https://docling-project.github.io/docling/concepts/architecture/)
- [DoclingDocument](https://docling-project.github.io/docling/concepts/docling_document/)
- [Serialization](https://docling-project.github.io/docling/concepts/serialization/)
- [Примеры использования](https://docling-project.github.io/docling/examples/)

## 🎯 Итоговые рекомендации

### Для презентаций и слайдов:
```bash
python extract_educational_content.py slides.pdf -o output/ \
    --image-scale 2.5 --all-formats
```

### Для учебников и длинных текстов:
```bash
python extract_educational_content.py textbook.pdf -o output/ \
    --image-scale 2.0 -f markdown
```

### Для сканированных материалов:
```bash
python extract_educational_content.py scanned.pdf -o output/ \
    --ocr --image-scale 3.0 --all-formats
```

### Для пакетной обработки курса:
```bash
python batch_extract_educational.py course/ -o extracted/ \
    --recursive --all-formats --parallel --workers 2
```

