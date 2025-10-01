#!/usr/bin/env python3
"""
Демонстрационный скрипт для показа возможностей извлечения
учебного контента из PDF с использованием Docling.

Этот скрипт показывает различные сценарии использования и
демонстрирует архитектуру Docling на практике.
"""

from pathlib import Path
from typing import Optional
import sys

try:
    from extract_educational_content import EducationalContentExtractor
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat
    from docling_core.types.doc import ImageRefMode, DocItemLabel
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("\nУстановите зависимости:")
    print("  pip install docling")
    sys.exit(1)


def demo_1_basic_extraction():
    """
    Демо 1: Базовое извлечение с сохранением структуры.
    
    Показывает:
    - Создание экстрактора с настройками
    - Извлечение документа
    - Базовую статистику
    """
    print("\n" + "="*70)
    print("ДЕМО 1: Базовое извлечение учебного контента")
    print("="*70)
    
    # Создаем экстрактор с стандартными настройками
    extractor = EducationalContentExtractor(
        extract_images=True,
        extract_tables=True,
        use_ocr=False,
        image_resolution_scale=2.0,
    )
    
    # Проверяем наличие тестового файла
    test_file = Path("sample.pdf")
    if not test_file.exists():
        print(f"\n⚠️  Тестовый файл {test_file} не найден")
        print("Создайте PDF файл или укажите путь к существующему")
        return
    
    # Извлекаем документ
    print(f"\n📄 Извлечение: {test_file}")
    doc = extractor.extract_document(test_file)
    
    # Анализ структуры
    print("\n📊 Анализ структуры документа:")
    print(f"   • Название: {doc.name if hasattr(doc, 'name') else 'N/A'}")
    
    if hasattr(doc, 'texts'):
        print(f"   • Текстовых элементов: {len(doc.texts)}")
        # Показать первые 3 заголовка
        headings = [t for t in doc.texts if hasattr(t, 'label') and 'heading' in str(t.label).lower()]
        if headings[:3]:
            print("   • Первые заголовки:")
            for h in headings[:3]:
                print(f"     - {h.text[:60]}...")
    
    if hasattr(doc, 'tables'):
        print(f"   • Таблиц: {len(doc.tables)}")
    
    if hasattr(doc, 'pictures'):
        print(f"   • Изображений: {len(doc.pictures)}")
    
    print("\n✅ Демо 1 завершено")


def demo_2_image_modes():
    """
    Демо 2: Различные режимы работы с изображениями.
    
    Показывает:
    - ImageRefMode.REFERENCED - ссылки на файлы
    - ImageRefMode.EMBEDDED - встроенные base64
    - Сравнение размеров файлов
    """
    print("\n" + "="*70)
    print("ДЕМО 2: Режимы работы с изображениями")
    print("="*70)
    
    test_file = Path("sample.pdf")
    if not test_file.exists():
        print(f"\n⚠️  Тестовый файл не найден")
        return
    
    # Настройка pipeline с генерацией изображений
    pipeline_options = PdfPipelineOptions()
    pipeline_options.generate_picture_images = True
    pipeline_options.images_scale = 2.0
    
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
    print(f"\n📄 Конвертация: {test_file}")
    result = converter.convert(str(test_file))
    doc = result.document
    
    # Режим 1: REFERENCED - отдельные файлы
    print("\n📂 Режим 1: REFERENCED (отдельные файлы)")
    md_referenced = doc.export_to_markdown(image_mode=ImageRefMode.REFERENCED)
    print(f"   • Размер Markdown: {len(md_referenced)} символов")
    print(f"   • Изображения: отдельные PNG файлы")
    print(f"   • Использование: Git, редактирование, блоги")
    
    # Режим 2: EMBEDDED - встроенные
    print("\n📦 Режим 2: EMBEDDED (встроенные base64)")
    html_embedded = doc.export_to_html(image_mode=ImageRefMode.EMBEDDED)
    print(f"   • Размер HTML: {len(html_embedded)} символов")
    print(f"   • Изображения: base64 внутри файла")
    print(f"   • Использование: архивирование, email")
    
    # Сравнение
    print("\n📊 Сравнение:")
    print(f"   • Соотношение размеров: {len(html_embedded) / len(md_referenced):.1f}x")
    print(f"   • Рекомендация для презентаций: REFERENCED + HTML EMBEDDED")
    
    print("\n✅ Демо 2 завершено")


def demo_3_quality_comparison():
    """
    Демо 3: Сравнение качества извлечения изображений.
    
    Показывает:
    - Разные масштабы (1.0x, 2.0x, 3.0x)
    - Влияние на размер и качество
    - Рекомендации по использованию
    """
    print("\n" + "="*70)
    print("ДЕМО 3: Качество извлечения изображений")
    print("="*70)
    
    test_file = Path("sample.pdf")
    if not test_file.exists():
        print(f"\n⚠️  Тестовый файл не найден")
        return
    
    scales = [1.0, 2.0, 3.0]
    
    print(f"\n📄 Тестирование: {test_file}")
    print("\nСравнение различных масштабов:")
    
    for scale in scales:
        print(f"\n🔍 Масштаб {scale}x:")
        
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = scale
        pipeline_options.generate_picture_images = True
        
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        
        result = converter.convert(str(test_file))
        doc = result.document
        
        # Экспорт для оценки размера
        md_content = doc.export_to_markdown()
        
        print(f"   • Размер вывода: {len(md_content)} символов")
        print(f"   • Время обработки: ~{scale * 1.5:.1f}s (относительно)")
        
        # Рекомендации
        if scale == 1.0:
            print(f"   • Применение: быстрый просмотр, низкое качество")
        elif scale == 2.0:
            print(f"   • Применение: стандарт, баланс качества/размера ⭐")
        elif scale == 3.0:
            print(f"   • Применение: высокое качество, диаграммы")
    
    print("\n💡 Рекомендации:")
    print("   • Презентации: 2.0x - 2.5x")
    print("   • Учебники: 2.0x")
    print("   • Технические чертежи: 3.0x - 4.0x")
    print("   • Быстрый просмотр: 1.0x")
    
    print("\n✅ Демо 3 завершено")


def demo_4_document_structure():
    """
    Демо 4: Анализ структуры документа.
    
    Показывает:
    - Иерархию заголовков
    - Типы элементов (texts, tables, pictures)
    - Порядок чтения
    """
    print("\n" + "="*70)
    print("ДЕМО 4: Анализ структуры документа")
    print("="*70)
    
    test_file = Path("sample.pdf")
    if not test_file.exists():
        print(f"\n⚠️  Тестовый файл не найден")
        return
    
    extractor = EducationalContentExtractor()
    doc = extractor.extract_document(test_file)
    
    print("\n🔍 Детальный анализ структуры:")
    
    # Анализ текстовых элементов
    if hasattr(doc, 'texts') and doc.texts:
        print(f"\n📝 Текстовые элементы ({len(doc.texts)} шт.):")
        
        # Группировка по типам
        element_types = {}
        for text in doc.texts:
            label = str(text.label) if hasattr(text, 'label') else 'unknown'
            element_types[label] = element_types.get(label, 0) + 1
        
        for label, count in sorted(element_types.items(), key=lambda x: -x[1]):
            print(f"   • {label}: {count}")
        
        # Показать структуру заголовков
        print(f"\n📑 Иерархия заголовков:")
        for idx, text in enumerate(doc.texts[:10]):  # Первые 10
            if hasattr(text, 'label') and 'heading' in str(text.label).lower():
                level = str(text.label).lower().count('heading')
                indent = "  " * level
                print(f"   {indent}• {text.text[:50]}...")
    
    # Анализ таблиц
    if hasattr(doc, 'tables') and doc.tables:
        print(f"\n📊 Таблицы ({len(doc.tables)} шт.):")
        for idx, table in enumerate(doc.tables[:3], 1):  # Первые 3
            print(f"   • Таблица {idx}")
            if hasattr(table, 'num_rows') and hasattr(table, 'num_cols'):
                print(f"     Размер: {table.num_rows}x{table.num_cols}")
    
    # Анализ изображений
    if hasattr(doc, 'pictures') and doc.pictures:
        print(f"\n🖼️  Изображения ({len(doc.pictures)} шт.):")
        for idx, picture in enumerate(doc.pictures[:5], 1):  # Первые 5
            print(f"   • Изображение {idx}")
            if hasattr(picture, 'size'):
                print(f"     Размер: {picture.size}")
    
    # JSON структура
    print(f"\n📋 JSON структура:")
    json_data = doc.export_to_json()
    print(f"   • Размер: {len(json_data)} символов")
    print(f"   • Использование: программная обработка, анализ")
    
    print("\n✅ Демо 4 завершено")


def demo_5_complete_package():
    """
    Демо 5: Создание полного пакета.
    
    Показывает:
    - Экспорт во все форматы
    - Создание README
    - Организацию файлов
    """
    print("\n" + "="*70)
    print("ДЕМО 5: Создание полного пакета")
    print("="*70)
    
    test_file = Path("sample.pdf")
    if not test_file.exists():
        print(f"\n⚠️  Тестовый файл не найден")
        return
    
    output_dir = Path("demo_output")
    
    print(f"\n📦 Создание полного пакета:")
    print(f"   • Входной файл: {test_file}")
    print(f"   • Выходная директория: {output_dir}")
    
    extractor = EducationalContentExtractor(
        extract_images=True,
        extract_tables=True,
        image_resolution_scale=2.0,
    )
    
    # Извлечение
    doc = extractor.extract_document(test_file)
    
    # Создание полного пакета
    results = extractor.export_complete_package(
        doc=doc,
        output_dir=output_dir,
        base_filename=test_file.stem,
        formats=['markdown', 'html', 'json'],
    )
    
    print(f"\n✅ Создан полный пакет:")
    print(f"\n📁 Структура:")
    print(f"{output_dir}/")
    for format_name, path in results.items():
        print(f"├── {path.name}")
    if results.get('markdown'):
        print(f"└── {test_file.stem}_images/")
        print(f"    └── (изображения)")
    
    print(f"\n💡 Рекомендации по использованию:")
    print(f"   • .md - для редактирования и Git")
    print(f"   • .html - для просмотра в браузере")
    print(f"   • .json - для программной обработки")
    print(f"   • README.md - информация о пакете")
    
    print("\n✅ Демо 5 завершено")


def main():
    """Запуск всех демонстраций."""
    print("\n" + "🎓 "*30)
    print("ДЕМОНСТРАЦИЯ ВОЗМОЖНОСТЕЙ ИЗВЛЕЧЕНИЯ УЧЕБНОГО КОНТЕНТА")
    print("Основано на архитектуре Docling")
    print("🎓 "*30)
    
    demos = [
        ("Базовое извлечение", demo_1_basic_extraction),
        ("Режимы изображений", demo_2_image_modes),
        ("Качество изображений", demo_3_quality_comparison),
        ("Структура документа", demo_4_document_structure),
        ("Полный пакет", demo_5_complete_package),
    ]
    
    print("\nДоступные демонстрации:")
    for idx, (name, _) in enumerate(demos, 1):
        print(f"  {idx}. {name}")
    print(f"  0. Запустить все")
    
    try:
        choice = input("\nВыберите демо (0-5): ").strip()
        
        if choice == "0":
            for name, demo_func in demos:
                demo_func()
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            demos[int(choice) - 1][1]()
        else:
            print("❌ Неверный выбор")
            return
        
        print("\n" + "="*70)
        print("✅ ВСЕ ДЕМОНСТРАЦИИ ЗАВЕРШЕНЫ")
        print("="*70)
        print("\n📖 Для подробной информации см.:")
        print("   • EDUCATIONAL_CONTENT_GUIDE.md - полное руководство")
        print("   • README.md - общая документация")
        print("   • https://docling-project.github.io/docling/ - документация Docling")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Демонстрация прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

