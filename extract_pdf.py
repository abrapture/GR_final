#!/usr/bin/env python3
"""
Скрипт для извлечения содержимого из PDF презентаций с использованием Docling.
Поддерживает экспорт в различные форматы: Markdown, HTML, JSON.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import PdfFormatOption
except ImportError:
    print("Ошибка: Библиотека Docling не установлена.")
    print("Установите её командой: pip install docling")
    sys.exit(1)


class PDFExtractor:
    """Класс для извлечения содержимого из PDF файлов."""
    
    def __init__(self, use_ocr: bool = False):
        """
        Инициализация экстрактора PDF.
        
        Args:
            use_ocr: Использовать OCR для сканированных PDF
        """
        # Настройка параметров обработки PDF
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = use_ocr
        
        # Создание конвертера с настройками
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
    
    def extract_single_file(
        self, 
        pdf_path: Path, 
        output_format: str = "markdown"
    ) -> Optional[str]:
        """
        Извлечение содержимого из одного PDF файла.
        
        Args:
            pdf_path: Путь к PDF файлу
            output_format: Формат вывода (markdown, html, json, doctags)
            
        Returns:
            Извлеченное содержимое в виде строки или None при ошибке
        """
        try:
            print(f"Обработка файла: {pdf_path}")
            
            # Конвертация документа
            result = self.converter.convert(str(pdf_path))
            
            # Экспорт в нужный формат
            if output_format.lower() == "markdown":
                content = result.document.export_to_markdown()
            elif output_format.lower() == "html":
                content = result.document.export_to_html()
            elif output_format.lower() == "json":
                content = result.document.export_to_json()
            elif output_format.lower() == "doctags":
                content = result.document.export_to_document_tokens()
            else:
                print(f"Неизвестный формат: {output_format}. Используется markdown.")
                content = result.document.export_to_markdown()
            
            print(f"✓ Файл успешно обработан: {pdf_path}")
            return content
            
        except Exception as e:
            print(f"✗ Ошибка при обработке {pdf_path}: {e}")
            return None
    
    def extract_multiple_files(
        self, 
        pdf_paths: List[Path], 
        output_format: str = "markdown"
    ) -> dict:
        """
        Извлечение содержимого из нескольких PDF файлов.
        
        Args:
            pdf_paths: Список путей к PDF файлам
            output_format: Формат вывода
            
        Returns:
            Словарь {имя_файла: содержимое}
        """
        results = {}
        
        for pdf_path in pdf_paths:
            content = self.extract_single_file(pdf_path, output_format)
            if content:
                results[pdf_path.name] = content
        
        return results
    
    def save_to_file(self, content: str, output_path: Path):
        """
        Сохранение извлеченного содержимого в файл.
        
        Args:
            content: Содержимое для сохранения
            output_path: Путь к выходному файлу
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding='utf-8')
            print(f"✓ Результат сохранен в: {output_path}")
        except Exception as e:
            print(f"✗ Ошибка при сохранении файла {output_path}: {e}")


def main():
    """Основная функция для запуска из командной строки."""
    parser = argparse.ArgumentParser(
        description='Извлечение содержимого из PDF презентаций с помощью Docling',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Извлечь содержимое одного PDF в Markdown
  python extract_pdf.py presentation.pdf
  
  # Извлечь с сохранением в файл
  python extract_pdf.py presentation.pdf -o output.md
  
  # Извлечь в HTML формате
  python extract_pdf.py presentation.pdf -f html -o output.html
  
  # Обработать несколько файлов
  python extract_pdf.py file1.pdf file2.pdf -o output_dir/
  
  # Использовать OCR для сканированных PDF
  python extract_pdf.py scanned.pdf --ocr -o output.md
        """
    )
    
    parser.add_argument(
        'input_files',
        nargs='+',
        type=str,
        help='Путь к PDF файлу(ам) для обработки'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Путь для сохранения результата (файл или директория)'
    )
    
    parser.add_argument(
        '-f', '--format',
        type=str,
        default='markdown',
        choices=['markdown', 'html', 'json', 'doctags'],
        help='Формат вывода (по умолчанию: markdown)'
    )
    
    parser.add_argument(
        '--ocr',
        action='store_true',
        help='Использовать OCR для сканированных PDF'
    )
    
    parser.add_argument(
        '--print',
        action='store_true',
        help='Вывести результат в консоль'
    )
    
    args = parser.parse_args()
    
    # Создание экстрактора
    extractor = PDFExtractor(use_ocr=args.ocr)
    
    # Преобразование путей
    input_paths = [Path(p) for p in args.input_files]
    
    # Проверка существования файлов
    for path in input_paths:
        if not path.exists():
            print(f"✗ Файл не найден: {path}")
            sys.exit(1)
        if not path.suffix.lower() == '.pdf':
            print(f"⚠ Предупреждение: {path} не является PDF файлом")
    
    # Обработка файлов
    if len(input_paths) == 1:
        # Один файл
        content = extractor.extract_single_file(input_paths[0], args.format)
        
        if content:
            if args.print:
                print("\n" + "="*50)
                print("ИЗВЛЕЧЕННОЕ СОДЕРЖИМОЕ:")
                print("="*50)
                print(content)
            
            if args.output:
                output_path = Path(args.output)
                extractor.save_to_file(content, output_path)
            elif not args.print:
                print("\n" + content)
    else:
        # Несколько файлов
        results = extractor.extract_multiple_files(input_paths, args.format)
        
        if args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for filename, content in results.items():
                # Определение расширения на основе формата
                ext_map = {
                    'markdown': '.md',
                    'html': '.html',
                    'json': '.json',
                    'doctags': '.txt'
                }
                ext = ext_map.get(args.format, '.txt')
                
                output_path = output_dir / f"{Path(filename).stem}{ext}"
                extractor.save_to_file(content, output_path)
        
        if args.print or not args.output:
            for filename, content in results.items():
                print(f"\n{'='*50}")
                print(f"Файл: {filename}")
                print('='*50)
                print(content)
    
    print(f"\n✓ Обработка завершена!")


if __name__ == "__main__":
    main()

