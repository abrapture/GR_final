#!/usr/bin/env python3
"""
Пакетная обработка нескольких PDF файлов с извлечением учебного контента.
Идеально для обработки целых курсов, учебников или коллекций лекций.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from datetime import datetime

try:
    from extract_educational_content import EducationalContentExtractor
except ImportError:
    print("❌ Ошибка: Не найден модуль extract_educational_content.py")
    print("Убедитесь, что файл находится в той же директории")
    sys.exit(1)


class BatchEducationalExtractor:
    """Класс для пакетной обработки PDF файлов."""
    
    def __init__(
        self,
        extract_images: bool = True,
        extract_tables: bool = True,
        use_ocr: bool = False,
        image_resolution_scale: float = 2.0,
        max_workers: int = 2,
    ):
        """
        Инициализация пакетного экстрактора.
        
        Args:
            extract_images: Извлекать изображения
            extract_tables: Извлекать таблицы
            use_ocr: Использовать OCR
            image_resolution_scale: Масштаб изображений
            max_workers: Максимальное количество параллельных обработок
        """
        self.extractor = EducationalContentExtractor(
            extract_images=extract_images,
            extract_tables=extract_tables,
            use_ocr=use_ocr,
            image_resolution_scale=image_resolution_scale,
        )
        self.max_workers = max_workers
        self.results = []
        self.errors = []
    
    def process_file(
        self,
        pdf_path: Path,
        output_dir: Path,
        formats: List[str],
    ) -> Dict:
        """
        Обработка одного файла.
        
        Args:
            pdf_path: Путь к PDF
            output_dir: Директория вывода
            formats: Форматы экспорта
            
        Returns:
            Словарь с результатами
        """
        try:
            print(f"\n{'='*60}")
            print(f"Обработка: {pdf_path.name}")
            print(f"{'='*60}")
            
            # Извлечение документа
            doc = self.extractor.extract_document(pdf_path)
            
            # Создание поддиректории для этого файла
            file_output_dir = output_dir / pdf_path.stem
            
            # Экспорт
            results = self.extractor.export_complete_package(
                doc=doc,
                output_dir=file_output_dir,
                base_filename=pdf_path.stem,
                formats=formats,
            )
            
            return {
                "status": "success",
                "file": str(pdf_path),
                "output_dir": str(file_output_dir),
                "results": {k: str(v) for k, v in results.items()},
                "stats": {
                    "texts": len(doc.texts) if hasattr(doc, 'texts') else 0,
                    "tables": len(doc.tables) if hasattr(doc, 'tables') else 0,
                    "pictures": len(doc.pictures) if hasattr(doc, 'pictures') else 0,
                }
            }
            
        except Exception as e:
            error_info = {
                "status": "error",
                "file": str(pdf_path),
                "error": str(e),
            }
            self.errors.append(error_info)
            print(f"\n❌ Ошибка при обработке {pdf_path.name}: {e}")
            return error_info
    
    def process_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        formats: List[str],
        recursive: bool = False,
        parallel: bool = False,
    ) -> List[Dict]:
        """
        Обработка всех PDF файлов в директории.
        
        Args:
            input_dir: Входная директория
            output_dir: Выходная директория
            formats: Форматы экспорта
            recursive: Рекурсивный поиск PDF
            parallel: Параллельная обработка
            
        Returns:
            Список результатов обработки
        """
        # Поиск PDF файлов
        pattern = "**/*.pdf" if recursive else "*.pdf"
        pdf_files = list(input_dir.glob(pattern))
        
        if not pdf_files:
            print(f"⚠ В директории {input_dir} не найдено PDF файлов")
            return []
        
        print(f"\n🔍 Найдено PDF файлов: {len(pdf_files)}")
        print(f"📁 Выходная директория: {output_dir}")
        print(f"⚙️  Параллельная обработка: {'✓' if parallel else '✗'}")
        print(f"🔄 Рекурсивный поиск: {'✓' if recursive else '✗'}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Обработка файлов
        if parallel and len(pdf_files) > 1:
            results = self._process_parallel(pdf_files, output_dir, formats)
        else:
            results = self._process_sequential(pdf_files, output_dir, formats)
        
        self.results = results
        return results
    
    def _process_sequential(
        self,
        pdf_files: List[Path],
        output_dir: Path,
        formats: List[str],
    ) -> List[Dict]:
        """Последовательная обработка файлов."""
        results = []
        
        for idx, pdf_path in enumerate(pdf_files, 1):
            print(f"\n{'🔹'*30}")
            print(f"Файл {idx}/{len(pdf_files)}")
            result = self.process_file(pdf_path, output_dir, formats)
            results.append(result)
        
        return results
    
    def _process_parallel(
        self,
        pdf_files: List[Path],
        output_dir: Path,
        formats: List[str],
    ) -> List[Dict]:
        """Параллельная обработка файлов."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Запуск задач
            future_to_pdf = {
                executor.submit(
                    self.process_file, pdf_path, output_dir, formats
                ): pdf_path
                for pdf_path in pdf_files
            }
            
            # Сбор результатов
            for idx, future in enumerate(as_completed(future_to_pdf), 1):
                pdf_path = future_to_pdf[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"\n✓ Обработано {idx}/{len(pdf_files)}: {pdf_path.name}")
                except Exception as e:
                    error_info = {
                        "status": "error",
                        "file": str(pdf_path),
                        "error": str(e),
                    }
                    results.append(error_info)
                    print(f"\n❌ Ошибка {idx}/{len(pdf_files)}: {pdf_path.name}")
        
        return results
    
    def create_batch_report(self, output_dir: Path) -> Path:
        """
        Создание отчета о пакетной обработке.
        
        Args:
            output_dir: Директория для сохранения отчета
            
        Returns:
            Путь к файлу отчета
        """
        successful = [r for r in self.results if r.get("status") == "success"]
        failed = [r for r in self.results if r.get("status") == "error"]
        
        # Создание JSON отчета
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(self.results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": f"{len(successful)/len(self.results)*100:.1f}%" if self.results else "0%",
            "results": self.results,
        }
        
        json_path = output_dir / "batch_report.json"
        json_path.write_text(json.dumps(report_data, indent=2, ensure_ascii=False), encoding='utf-8')
        
        # Создание Markdown отчета
        md_content = f"""# Отчет о пакетной обработке

## Сводка

- **Дата обработки**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Всего файлов**: {len(self.results)}
- **Успешно**: {len(successful)} ✓
- **Ошибок**: {len(failed)} ✗
- **Успешность**: {len(successful)/len(self.results)*100:.1f}%

"""
        
        if successful:
            md_content += "## ✅ Успешно обработанные файлы\n\n"
            for result in successful:
                stats = result.get('stats', {})
                md_content += f"### {Path(result['file']).name}\n\n"
                md_content += f"- **Выходная директория**: `{result['output_dir']}`\n"
                md_content += f"- **Текстовые элементы**: {stats.get('texts', 0)}\n"
                md_content += f"- **Таблицы**: {stats.get('tables', 0)}\n"
                md_content += f"- **Изображения**: {stats.get('pictures', 0)}\n\n"
        
        if failed:
            md_content += "## ❌ Файлы с ошибками\n\n"
            for result in failed:
                md_content += f"### {Path(result['file']).name}\n\n"
                md_content += f"- **Ошибка**: `{result.get('error', 'Unknown error')}`\n\n"
        
        md_content += f"""
## Статистика по всем файлам

"""
        
        if successful:
            total_stats = {
                'texts': sum(r.get('stats', {}).get('texts', 0) for r in successful),
                'tables': sum(r.get('stats', {}).get('tables', 0) for r in successful),
                'pictures': sum(r.get('stats', {}).get('pictures', 0) for r in successful),
            }
            
            md_content += f"""
- **Всего текстовых элементов**: {total_stats['texts']}
- **Всего таблиц**: {total_stats['tables']}
- **Всего изображений**: {total_stats['pictures']}
"""
        
        md_content += f"""
## Технические детали

- **Инструмент**: Docling Batch Educational Content Extractor
- **JSON отчет**: `batch_report.json`
- **Документация**: https://docling-project.github.io/docling/

"""
        
        md_path = output_dir / "BATCH_REPORT.md"
        md_path.write_text(md_content, encoding='utf-8')
        
        print(f"\n✓ Отчет сохранен:")
        print(f"   • JSON: {json_path}")
        print(f"   • Markdown: {md_path}")
        
        return md_path


def main():
    """Основная функция для командной строки."""
    parser = argparse.ArgumentParser(
        description='Пакетная обработка PDF файлов для извлечения учебного контента',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Обработать все PDF в директории
  python batch_extract_educational.py input_folder/ -o output/

  # Рекурсивная обработка всех поддиректорий
  python batch_extract_educational.py lectures/ -o output/ --recursive

  # Параллельная обработка с 4 потоками
  python batch_extract_educational.py docs/ -o output/ --parallel --workers 4

  # Все форматы с OCR
  python batch_extract_educational.py scanned_docs/ -o output/ --all-formats --ocr
        """
    )
    
    parser.add_argument(
        'input_dir',
        type=str,
        help='Директория с PDF файлами'
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
        help='Форматы для экспорта'
    )
    
    parser.add_argument(
        '--all-formats',
        action='store_true',
        help='Создать все форматы'
    )
    
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Рекурсивный поиск PDF в поддиректориях'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Параллельная обработка файлов'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=2,
        help='Количество параллельных потоков (по умолчанию: 2)'
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
        help='Использовать OCR'
    )
    
    parser.add_argument(
        '--image-scale',
        type=float,
        default=2.0,
        help='Масштаб изображений'
    )
    
    args = parser.parse_args()
    
    # Проверка входной директории
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"❌ Директория не найдена: {input_dir}")
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"❌ Путь не является директорией: {input_dir}")
        sys.exit(1)
    
    # Определение форматов
    formats = ['markdown', 'html', 'json'] if args.all_formats else args.formats
    
    # Создание пакетного экстрактора
    print("🚀 Инициализация Batch Educational Content Extractor")
    print("=" * 60)
    
    batch_extractor = BatchEducationalExtractor(
        extract_images=not args.no_images,
        extract_tables=not args.no_tables,
        use_ocr=args.ocr,
        image_resolution_scale=args.image_scale,
        max_workers=args.workers,
    )
    
    # Обработка директории
    output_dir = Path(args.output)
    
    results = batch_extractor.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        formats=formats,
        recursive=args.recursive,
        parallel=args.parallel,
    )
    
    # Создание отчета
    if results:
        print(f"\n{'='*60}")
        print("📊 Создание отчета о пакетной обработке")
        print("=" * 60)
        
        batch_extractor.create_batch_report(output_dir)
        
        # Итоги
        successful = [r for r in results if r.get("status") == "success"]
        failed = [r for r in results if r.get("status") == "error"]
        
        print(f"\n{'='*60}")
        print("✅ ПАКЕТНАЯ ОБРАБОТКА ЗАВЕРШЕНА")
        print("=" * 60)
        print(f"\n📊 Результаты:")
        print(f"   • Всего файлов: {len(results)}")
        print(f"   • Успешно: {len(successful)} ✓")
        print(f"   • Ошибок: {len(failed)} ✗")
        print(f"   • Успешность: {len(successful)/len(results)*100:.1f}%")
        print(f"\n📁 Все результаты в: {output_dir}")
        print(f"📄 Подробный отчет: {output_dir}/BATCH_REPORT.md")
    else:
        print("\n⚠ Не найдено файлов для обработки")


if __name__ == "__main__":
    main()

