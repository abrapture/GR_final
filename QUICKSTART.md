# Быстрый старт

## Шаг 1: Установка библиотеки

```bash
cd /Users/alexey/Documents/alexey/GR_final
pip install docling
```

## Шаг 2: Базовое использование

### Вариант А: Командная строка

```bash
# Простое извлечение (вывод в консоль)
python extract_pdf.py ваш_файл.pdf

# Сохранить в файл
python extract_pdf.py ваш_файл.pdf -o результат.md

# Экспорт в HTML
python extract_pdf.py ваш_файл.pdf -f html -o результат.html
```

### Вариант Б: Программное использование

Создайте файл `test.py`:

```python
from pathlib import Path
from extract_pdf import PDFExtractor

# Создать экстрактор
extractor = PDFExtractor()

# Извлечь содержимое
content = extractor.extract_single_file(
    Path("ваш_файл.pdf"), 
    output_format="markdown"
)

# Показать результат
print(content)

# Или сохранить в файл
extractor.save_to_file(content, Path("результат.md"))
```

Затем запустите:
```bash
python test.py
```

## Шаг 3: Просмотр примеров

```bash
# Запустить все примеры
python example_usage.py
```

## Частые команды

```bash
# Один файл → Markdown
python extract_pdf.py presentation.pdf -o output.md

# Несколько файлов → директория
python extract_pdf.py file1.pdf file2.pdf file3.pdf -o output/

# Сканированный документ с OCR
python extract_pdf.py scanned.pdf --ocr -o output.md

# Вывод в консоль
python extract_pdf.py document.pdf --print
```

## Проверка установки

Создайте файл `check_install.py`:

```python
try:
    from docling.document_converter import DocumentConverter
    print("✓ Docling установлен успешно!")
    print(f"Версия: {DocumentConverter.__module__}")
except ImportError as e:
    print("✗ Ошибка: Docling не установлен")
    print(f"Установите командой: pip install docling")
```

Запустите:
```bash
python check_install.py
```

## Что дальше?

1. Прочитайте полную документацию в `README.md`
2. Изучите примеры в `example_usage.py`
3. Посетите [официальную документацию Docling](https://docling-project.github.io/docling/)

