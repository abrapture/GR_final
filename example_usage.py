#!/usr/bin/env python3
"""
Примеры использования PDFExtractor для различных сценариев.
"""

from pathlib import Path
from extract_pdf import PDFExtractor


def example_1_basic_extraction():
    """Пример 1: Базовое извлечение содержимого из PDF в Markdown."""
    print("=" * 60)
    print("Пример 1: Базовое извлечение в Markdown")
    print("=" * 60)
    
    extractor = PDFExtractor()
    
    # Укажите путь к вашему PDF файлу
    pdf_path = Path("presentation.pdf")
    
    if pdf_path.exists():
        content = extractor.extract_single_file(pdf_path, output_format="markdown")
        
        if content:
            # Сохранение результата
            output_path = Path("output/presentation.md")
            extractor.save_to_file(content, output_path)
            
            # Вывод первых 500 символов
            print("\nПервые 500 символов:")
            print(content[:500])
    else:
        print(f"⚠ Файл {pdf_path} не найден. Создайте тестовый PDF.")


def example_2_html_export():
    """Пример 2: Экспорт в HTML формат."""
    print("\n" + "=" * 60)
    print("Пример 2: Экспорт в HTML")
    print("=" * 60)
    
    extractor = PDFExtractor()
    
    pdf_path = Path("presentation.pdf")
    
    if pdf_path.exists():
        content = extractor.extract_single_file(pdf_path, output_format="html")
        
        if content:
            output_path = Path("output/presentation.html")
            extractor.save_to_file(content, output_path)
            print(f"\n✓ HTML сохранен в {output_path}")


def example_3_batch_processing():
    """Пример 3: Пакетная обработка нескольких PDF файлов."""
    print("\n" + "=" * 60)
    print("Пример 3: Пакетная обработка")
    print("=" * 60)
    
    extractor = PDFExtractor()
    
    # Список файлов для обработки
    pdf_files = [
        Path("presentation1.pdf"),
        Path("presentation2.pdf"),
        Path("presentation3.pdf"),
    ]
    
    # Фильтруем только существующие файлы
    existing_files = [f for f in pdf_files if f.exists()]
    
    if existing_files:
        results = extractor.extract_multiple_files(existing_files, output_format="markdown")
        
        # Сохранение всех результатов
        output_dir = Path("output/batch")
        for filename, content in results.items():
            output_path = output_dir / f"{Path(filename).stem}.md"
            extractor.save_to_file(content, output_path)
        
        print(f"\n✓ Обработано файлов: {len(results)}")
    else:
        print("⚠ Не найдено ни одного PDF файла для обработки")


def example_4_ocr_processing():
    """Пример 4: Обработка сканированного PDF с OCR."""
    print("\n" + "=" * 60)
    print("Пример 4: Обработка с OCR")
    print("=" * 60)
    
    # Создаем экстрактор с включенным OCR
    extractor = PDFExtractor(use_ocr=True)
    
    pdf_path = Path("scanned_presentation.pdf")
    
    if pdf_path.exists():
        print("Обработка сканированного документа (это может занять время)...")
        content = extractor.extract_single_file(pdf_path, output_format="markdown")
        
        if content:
            output_path = Path("output/scanned_presentation.md")
            extractor.save_to_file(content, output_path)
    else:
        print("⚠ Сканированный PDF не найден")


def example_5_json_export():
    """Пример 5: Экспорт в JSON для программной обработки."""
    print("\n" + "=" * 60)
    print("Пример 5: Экспорт в JSON")
    print("=" * 60)
    
    extractor = PDFExtractor()
    
    pdf_path = Path("presentation.pdf")
    
    if pdf_path.exists():
        content = extractor.extract_single_file(pdf_path, output_format="json")
        
        if content:
            output_path = Path("output/presentation.json")
            extractor.save_to_file(content, output_path)
            print(f"\n✓ JSON данные сохранены для дальнейшей обработки")
            
            # Можно загрузить JSON и работать с ним программно
            import json
            doc_data = json.loads(content)
            print(f"Структура документа содержит: {len(doc_data)} элементов верхнего уровня")


def example_6_working_with_document():
    """Пример 6: Работа с объектом DoclingDocument."""
    print("\n" + "=" * 60)
    print("Пример 6: Работа с объектом документа")
    print("=" * 60)
    
    from docling.document_converter import DocumentConverter
    
    pdf_path = Path("presentation.pdf")
    
    if pdf_path.exists():
        converter = DocumentConverter()
        result = converter.convert(str(pdf_path))
        
        # Получаем объект документа
        doc = result.document
        
        print(f"Название документа: {doc.name}")
        print(f"Количество страниц: {len(doc.pages) if hasattr(doc, 'pages') else 'N/A'}")
        
        # Экспорт в разные форматы
        markdown = doc.export_to_markdown()
        html = doc.export_to_html()
        
        print(f"\nРазмер Markdown: {len(markdown)} символов")
        print(f"Размер HTML: {len(html)} символов")
        
        # Сохранение в оба формата
        extractor = PDFExtractor()
        extractor.save_to_file(markdown, Path("output/doc.md"))
        extractor.save_to_file(html, Path("output/doc.html"))


def main():
    """Запуск всех примеров."""
    print("\n" + "🚀 " * 20)
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ DOCLING ДЛЯ ИЗВЛЕЧЕНИЯ PDF")
    print("🚀 " * 20 + "\n")
    
    # Создаем директорию для вывода
    Path("output").mkdir(exist_ok=True)
    
    # Запускаем примеры
    example_1_basic_extraction()
    example_2_html_export()
    example_3_batch_processing()
    example_4_ocr_processing()
    example_5_json_export()
    example_6_working_with_document()
    
    print("\n" + "✓ " * 20)
    print("ВСЕ ПРИМЕРЫ ЗАВЕРШЕНЫ")
    print("✓ " * 20 + "\n")


if __name__ == "__main__":
    main()

