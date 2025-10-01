#!/usr/bin/env python3
"""
Продвинутый скрипт для извлечения учебного контента из PDF с сохранением
всех изображений, графиков, таблиц и структуры документа.

Основано на архитектуре Docling:
- Document Converter с настраиваемыми pipelines
- DoclingDocument с полной иерархией
- Multimodal export для сохранения изображений
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, List
import json
from datetime import datetime

try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import (
        PdfPipelineOptions,
        TableFormatOption,
        EasyOcrOptions,
    )
    from docling.datamodel.document import DoclingDocument
    from docling_core.types.doc import (
        ImageRefMode,
        PictureItem,
        TableItem,
        DocItemLabel,
    )
except ImportError:
    print("❌ Ошибка: Библиотека Docling не установлена.")
    print("Установите её командой: pip install docling")
    sys.exit(1)


class EducationalContentExtractor:
    """
    Класс для извлечения учебного контента из PDF с максимальным
    сохранением структуры, изображений и таблиц.
    """
    
    def __init__(
        self,
        extract_images: bool = True,
        extract_tables: bool = True,
        use_ocr: bool = False,
        image_resolution_scale: float = 2.0,
    ):
        """
        Инициализация экстрактора.
        
        Args:
            extract_images: Извлекать изображения из документа
            extract_tables: Извлекать таблицы с сохранением структуры
            use_ocr: Использовать OCR для сканированных страниц
            image_resolution_scale: Масштаб для извлечения изображений (выше = лучше качество)
        """
        self.extract_images = extract_images
        self.extract_tables = extract_tables
        self.image_resolution_scale = image_resolution_scale
        
        # Настройка pipeline options для максимального качества
        self.pipeline_options = PdfPipelineOptions()
        self.pipeline_options.do_ocr = use_ocr
        self.pipeline_options.do_table_structure = extract_tables
        
        # Настройка для извлечения изображений
        if extract_images:
            self.pipeline_options.images_scale = image_resolution_scale
            self.pipeline_options.generate_picture_images = True
        
        # Создание Document Converter с настройками
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=self.pipeline_options
                )
            }
        )
    
    def extract_document(
        self, 
        pdf_path: Path,
        output_dir: Optional[Path] = None,
    ) -> DoclingDocument:
        """
        Извлечение документа с полным сохранением структуры.
        
        Args:
            pdf_path: Путь к PDF файлу
            output_dir: Директория для сохранения изображений
            
        Returns:
            DoclingDocument объект
        """
        print(f"📄 Обработка: {pdf_path.name}")
        print(f"   Извлечение изображений: {'✓' if self.extract_images else '✗'}")
        print(f"   Извлечение таблиц: {'✓' if self.extract_tables else '✗'}")
        print(f"   OCR: {'✓' if self.pipeline_options.do_ocr else '✗'}")
        
        # Конвертация документа
        result = self.converter.convert(str(pdf_path))
        doc = result.document
        
        print(f"✓ Документ обработан")
        
        # Статистика
        self._print_statistics(doc)
        
        return doc
    
    def _print_statistics(self, doc: DoclingDocument):
        """Вывод статистики по извлеченному контенту."""
        stats = {
            "Текстовые элементы": len(doc.texts) if hasattr(doc, 'texts') else 0,
            "Таблицы": len(doc.tables) if hasattr(doc, 'tables') else 0,
            "Изображения": len(doc.pictures) if hasattr(doc, 'pictures') else 0,
        }
        
        print("\n📊 Статистика извлеченного контента:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    def export_to_markdown_with_images(
        self,
        doc: DoclingDocument,
        output_dir: Path,
        base_filename: str,
    ) -> Path:
        """
        Экспорт в Markdown с сохранением изображений.
        
        Args:
            doc: DoclingDocument объект
            output_dir: Директория для сохранения
            base_filename: Базовое имя файла без расширения
            
        Returns:
            Путь к созданному Markdown файлу
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем директорию для изображений
        images_dir = output_dir / f"{base_filename}_images"
        images_dir.mkdir(exist_ok=True)
        
        # Экспорт в Markdown с embedded изображениями
        # ImageRefMode определяет как ссылаться на изображения
        markdown_content = doc.export_to_markdown(
            image_mode=ImageRefMode.REFERENCED,  # Ссылки на файлы изображений
            # image_mode=ImageRefMode.EMBEDDED,  # Альтернатива: base64 embedded
        )
        
        # Сохранение изображений отдельно
        if self.extract_images and hasattr(doc, 'pictures'):
            self._save_pictures(doc, images_dir, base_filename)
        
        # Сохранение Markdown
        md_path = output_dir / f"{base_filename}.md"
        md_path.write_text(markdown_content, encoding='utf-8')
        
        print(f"\n✓ Markdown сохранен: {md_path}")
        print(f"✓ Изображения сохранены: {images_dir}")
        
        return md_path
    
    def _save_pictures(
        self,
        doc: DoclingDocument,
        images_dir: Path,
        base_filename: str,
    ):
        """Сохранение изображений из документа."""
        picture_counter = 0
        
        for idx, picture in enumerate(doc.pictures):
            # Получаем изображение если оно доступно
            if hasattr(picture, 'image') and picture.image:
                picture_counter += 1
                image_path = images_dir / f"image_{idx+1:03d}.png"
                
                try:
                    # Сохраняем изображение
                    if hasattr(picture.image, 'pil_image'):
                        picture.image.pil_image.save(image_path)
                    elif hasattr(picture, 'data'):
                        image_path.write_bytes(picture.data)
                    
                    print(f"   ✓ Изображение {idx+1} сохранено")
                except Exception as e:
                    print(f"   ⚠ Ошибка сохранения изображения {idx+1}: {e}")
        
        print(f"\n   Всего изображений сохранено: {picture_counter}")
    
    def export_to_html_with_images(
        self,
        doc: DoclingDocument,
        output_dir: Path,
        base_filename: str,
    ) -> Path:
        """
        Экспорт в HTML с встроенными изображениями (base64).
        
        Args:
            doc: DoclingDocument объект
            output_dir: Директория для сохранения
            base_filename: Базовое имя файла
            
        Returns:
            Путь к созданному HTML файлу
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Экспорт в HTML с embedded изображениями
        html_content = doc.export_to_html(
            image_mode=ImageRefMode.EMBEDDED  # Base64 embedded для самодостаточного HTML
        )
        
        # Добавляем CSS для лучшего отображения
        styled_html = self._add_html_styling(html_content, base_filename)
        
        # Сохранение HTML
        html_path = output_dir / f"{base_filename}.html"
        html_path.write_text(styled_html, encoding='utf-8')
        
        print(f"\n✓ HTML сохранен: {html_path}")
        
        return html_path
    
    def _add_html_styling(self, html_content: str, title: str) -> str:
        """Добавление CSS стилей для лучшего отображения."""
        styled = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background-color: #f5f5f5;
        }}
        .content {{
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        h1 {{ font-size: 2.5em; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ font-size: 2em; border-bottom: 2px solid #3498db; padding-bottom: 8px; }}
        h3 {{ font-size: 1.5em; }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            color: #555;
            font-style: italic;
        }}
        ul, ol {{
            padding-left: 30px;
        }}
        li {{
            margin: 5px 0;
        }}
        .metadata {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 30px;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="content">
        <div class="metadata">
            <strong>Документ извлечен:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
            <strong>Источник:</strong> {title}<br>
            <strong>Инструмент:</strong> Docling Educational Content Extractor
        </div>
        {html_content}
    </div>
</body>
</html>"""
        return styled
    
    def export_complete_package(
        self,
        doc: DoclingDocument,
        output_dir: Path,
        base_filename: str,
        formats: List[str] = ["markdown", "html", "json"],
    ) -> Dict[str, Path]:
        """
        Экспорт полного пакета в разных форматах.
        
        Args:
            doc: DoclingDocument объект
            output_dir: Директория для сохранения
            base_filename: Базовое имя файла
            formats: Список форматов для экспорта
            
        Returns:
            Словарь {формат: путь к файлу}
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        results = {}
        
        print(f"\n📦 Создание полного пакета...")
        
        if "markdown" in formats:
            md_path = self.export_to_markdown_with_images(
                doc, output_dir, base_filename
            )
            results["markdown"] = md_path
        
        if "html" in formats:
            html_path = self.export_to_html_with_images(
                doc, output_dir, base_filename
            )
            results["html"] = html_path
        
        if "json" in formats:
            json_path = self._export_to_json(doc, output_dir, base_filename)
            results["json"] = json_path
        
        # Создание README с информацией о пакете
        readme_path = self._create_package_readme(
            output_dir, base_filename, doc, results
        )
        results["readme"] = readme_path
        
        print(f"\n✓ Полный пакет создан в: {output_dir}")
        
        return results
    
    def _export_to_json(
        self,
        doc: DoclingDocument,
        output_dir: Path,
        base_filename: str,
    ) -> Path:
        """Экспорт структуры документа в JSON."""
        json_content = doc.export_to_json()
        json_path = output_dir / f"{base_filename}_structure.json"
        json_path.write_text(json_content, encoding='utf-8')
        print(f"✓ JSON структура сохранена: {json_path}")
        return json_path
    
    def _create_package_readme(
        self,
        output_dir: Path,
        base_filename: str,
        doc: DoclingDocument,
        results: Dict[str, Path],
    ) -> Path:
        """Создание README файла с описанием пакета."""
        readme_content = f"""# Извлеченный учебный контент: {base_filename}

## Информация об извлечении

- **Дата извлечения**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Инструмент**: Docling Educational Content Extractor
- **Исходный файл**: {base_filename}.pdf

## Статистика контента

- **Текстовые элементы**: {len(doc.texts) if hasattr(doc, 'texts') else 0}
- **Таблицы**: {len(doc.tables) if hasattr(doc, 'tables') else 0}
- **Изображения**: {len(doc.pictures) if hasattr(doc, 'pictures') else 0}

## Созданные файлы

"""
        
        for format_name, path in results.items():
            if format_name != "readme":
                readme_content += f"- **{format_name.upper()}**: `{path.name}`\n"
        
        readme_content += f"""
## Структура директории

```
{output_dir.name}/
├── {base_filename}.md                    # Markdown версия
├── {base_filename}.html                  # HTML версия (самодостаточная)
├── {base_filename}_structure.json        # JSON структура документа
├── {base_filename}_images/               # Директория с изображениями
│   ├── image_001.png
│   ├── image_002.png
│   └── ...
└── README.md                             # Этот файл
```

## Рекомендации по использованию

### Markdown файл
- Используйте для редактирования и интеграции в другие документы
- Изображения ссылаются на файлы в папке `{base_filename}_images/`
- Идеально для систем контроля версий (Git)

### HTML файл
- Самодостаточный файл со встроенными изображениями (base64)
- Откройте в любом браузере для просмотра
- Идеально для распространения и архивирования

### JSON файл
- Полная структура документа для программной обработки
- Содержит метаданные, иерархию и все элементы
- Используйте для анализа или дальнейшей обработки

## Технические детали

- **Формат исходного документа**: PDF
- **Использован OCR**: {'Да' if self.pipeline_options.do_ocr else 'Нет'}
- **Качество изображений**: {self.image_resolution_scale}x
- **Извлечение таблиц**: {'Включено' if self.extract_tables else 'Отключено'}

## Дополнительная информация

Для вопросов по извлечению контента обратитесь к документации Docling:
https://docling-project.github.io/docling/
"""
        
        readme_path = output_dir / "README.md"
        readme_path.write_text(readme_content, encoding='utf-8')
        print(f"✓ README создан: {readme_path}")
        
        return readme_path


def main():
    """Основная функция для запуска из командной строки."""
    parser = argparse.ArgumentParser(
        description='Извлечение учебного контента из PDF с сохранением структуры и изображений',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Извлечь весь контент с изображениями в Markdown
  python extract_educational_content.py lecture.pdf -o output/

  # Создать полный пакет (MD + HTML + JSON)
  python extract_educational_content.py textbook.pdf -o output/ --all-formats

  # Использовать OCR для сканированных документов
  python extract_educational_content.py scanned.pdf -o output/ --ocr

  # Высокое качество изображений
  python extract_educational_content.py presentation.pdf -o output/ --image-scale 3.0

  # Только Markdown без изображений
  python extract_educational_content.py doc.pdf -o output/ --no-images -f markdown
        """
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Путь к PDF файлу для обработки'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help='Директория для сохранения результатов'
    )
    
    parser.add_argument(
        '-f', '--formats',
        nargs='+',
        choices=['markdown', 'html', 'json'],
        default=['markdown'],
        help='Форматы для экспорта (по умолчанию: markdown)'
    )
    
    parser.add_argument(
        '--all-formats',
        action='store_true',
        help='Создать все форматы (Markdown + HTML + JSON)'
    )
    
    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Не извлекать изображения'
    )
    
    parser.add_argument(
        '--no-tables',
        action='store_true',
        help='Не извлекать таблицы'
    )
    
    parser.add_argument(
        '--ocr',
        action='store_true',
        help='Использовать OCR для сканированных страниц'
    )
    
    parser.add_argument(
        '--image-scale',
        type=float,
        default=2.0,
        help='Масштаб для извлечения изображений (по умолчанию: 2.0)'
    )
    
    args = parser.parse_args()
    
    # Проверка входного файла
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Файл не найден: {input_path}")
        sys.exit(1)
    
    if not input_path.suffix.lower() == '.pdf':
        print(f"⚠ Предупреждение: {input_path} может не быть PDF файлом")
    
    # Определение форматов
    formats = ['markdown', 'html', 'json'] if args.all_formats else args.formats
    
    # Создание экстрактора
    print("🚀 Инициализация Educational Content Extractor")
    print("=" * 60)
    
    extractor = EducationalContentExtractor(
        extract_images=not args.no_images,
        extract_tables=not args.no_tables,
        use_ocr=args.ocr,
        image_resolution_scale=args.image_scale,
    )
    
    # Извлечение документа
    print(f"\n📚 Извлечение учебного контента...")
    print("=" * 60)
    
    doc = extractor.extract_document(input_path)
    
    # Экспорт
    output_dir = Path(args.output)
    base_filename = input_path.stem
    
    print(f"\n💾 Экспорт результатов...")
    print("=" * 60)
    
    results = extractor.export_complete_package(
        doc=doc,
        output_dir=output_dir,
        base_filename=base_filename,
        formats=formats,
    )
    
    # Итоги
    print("\n" + "=" * 60)
    print("✅ ИЗВЛЕЧЕНИЕ ЗАВЕРШЕНО УСПЕШНО")
    print("=" * 60)
    print(f"\n📁 Все файлы сохранены в: {output_dir}")
    print(f"\n📄 Созданные файлы:")
    for format_name, path in results.items():
        print(f"   • {format_name.upper()}: {path.name}")
    
    print(f"\n💡 Откройте README.md в директории вывода для подробной информации")


if __name__ == "__main__":
    main()

