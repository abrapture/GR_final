#!/usr/bin/env python3
"""
Модуль для дедупликации повторяющегося контента в презентациях.

Решает проблему "анимационных" слайдов, где каждый следующий слайд
отличается только одной новой строкой, а остальное содержимое дублируется.

Стратегии дедупликации:
1. Sequential Diff - сравнение соседних слайдов
2. Content Hashing - поиск одинаковых блоков
3. Smart Merge - объединение похожих слайдов
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import hashlib
import difflib

try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.document import DoclingDocument
    from docling_core.types.doc import TextItem, ImageRefMode
except ImportError:
    print("❌ Ошибка: Библиотека Docling не установлена.")
    print("Установите: pip install docling")
    sys.exit(1)


class SlideDeduplicator:
    """
    Класс для дедупликации повторяющегося контента в презентациях.
    """
    
    def __init__(
        self,
        similarity_threshold: float = 0.85,
        min_text_length: int = 10,
    ):
        """
        Инициализация дедупликатора.
        
        Args:
            similarity_threshold: Порог сходства для объединения слайдов (0.0-1.0)
            min_text_length: Минимальная длина текста для учета
        """
        self.similarity_threshold = similarity_threshold
        self.min_text_length = min_text_length
        self.stats = {
            'original_items': 0,
            'deduplicated_items': 0,
            'removed_duplicates': 0,
        }
    
    def extract_slides_content(self, doc: DoclingDocument) -> List[Dict]:
        """
        Извлекает содержимое по слайдам (страницам).
        
        Args:
            doc: DoclingDocument объект
            
        Returns:
            Список словарей с содержимым каждого слайда
        """
        slides = []
        
        if not hasattr(doc, 'texts') or not doc.texts:
            return slides
        
        # Группируем текстовые элементы по страницам
        slides_by_page = defaultdict(list)
        
        for text_item in doc.texts:
            # Получаем номер страницы из провenance
            page_num = 0
            if hasattr(text_item, 'prov') and text_item.prov:
                for prov in text_item.prov:
                    if hasattr(prov, 'page_no'):
                        page_num = prov.page_no
                        break
            
            if hasattr(text_item, 'text') and len(text_item.text.strip()) >= self.min_text_length:
                slides_by_page[page_num].append({
                    'text': text_item.text.strip(),
                    'label': str(text_item.label) if hasattr(text_item, 'label') else 'text',
                    'original_item': text_item,
                })
        
        # Преобразуем в список слайдов
        for page_num in sorted(slides_by_page.keys()):
            slides.append({
                'page_num': page_num,
                'items': slides_by_page[page_num],
                'text_hash': self._hash_slide_content(slides_by_page[page_num]),
            })
        
        return slides
    
    def _hash_slide_content(self, items: List[Dict]) -> str:
        """Создает хеш содержимого слайда."""
        content = '\n'.join([item['text'] for item in items])
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _hash_text(self, text: str) -> str:
        """Создает хеш текста."""
        return hashlib.md5(text.strip().encode('utf-8')).hexdigest()
    
    def calculate_similarity(self, slide1: Dict, slide2: Dict) -> float:
        """
        Вычисляет сходство между двумя слайдами.
        
        Args:
            slide1, slide2: Словари с содержимым слайдов
            
        Returns:
            Коэффициент сходства (0.0-1.0)
        """
        texts1 = [item['text'] for item in slide1['items']]
        texts2 = [item['text'] for item in slide2['items']]
        
        # Используем SequenceMatcher для сравнения
        matcher = difflib.SequenceMatcher(None, texts1, texts2)
        return matcher.ratio()
    
    def find_new_content(
        self,
        prev_slide: Dict,
        curr_slide: Dict,
    ) -> List[Dict]:
        """
        Находит новый контент в текущем слайде по сравнению с предыдущим.
        
        Args:
            prev_slide: Предыдущий слайд
            curr_slide: Текущий слайд
            
        Returns:
            Список новых элементов
        """
        prev_hashes = {self._hash_text(item['text']) for item in prev_slide['items']}
        
        new_items = []
        for item in curr_slide['items']:
            item_hash = self._hash_text(item['text'])
            if item_hash not in prev_hashes:
                new_items.append(item)
        
        return new_items
    
    def deduplicate_sequential(self, slides: List[Dict]) -> List[Dict]:
        """
        Дедупликация методом последовательного сравнения.
        
        Стратегия: сравниваем каждый слайд с предыдущим и оставляем только новый контент.
        
        Args:
            slides: Список слайдов
            
        Returns:
            Дедуплицированный список слайдов
        """
        if not slides:
            return []
        
        deduplicated = []
        
        # Первый слайд добавляем полностью
        deduplicated.append(slides[0])
        
        for i in range(1, len(slides)):
            prev_slide = slides[i - 1]
            curr_slide = slides[i]
            
            # Вычисляем сходство
            similarity = self.calculate_similarity(prev_slide, curr_slide)
            
            if similarity >= self.similarity_threshold:
                # Слайды очень похожи - находим только новый контент
                new_items = self.find_new_content(prev_slide, curr_slide)
                
                if new_items:
                    # Создаем слайд только с новым контентом
                    deduplicated.append({
                        'page_num': curr_slide['page_num'],
                        'items': new_items,
                        'text_hash': self._hash_slide_content(new_items),
                        'is_incremental': True,
                        'similarity_to_prev': similarity,
                    })
                # Если нет нового контента - пропускаем слайд
            else:
                # Слайды различаются существенно - добавляем полностью
                deduplicated.append(curr_slide)
        
        return deduplicated
    
    def deduplicate_by_hashing(self, slides: List[Dict]) -> List[Dict]:
        """
        Дедупликация по хешам содержимого.
        
        Стратегия: находим слайды с идентичным содержимым и удаляем дубликаты.
        
        Args:
            slides: Список слайдов
            
        Returns:
            Дедуплицированный список слайдов
        """
        seen_hashes = set()
        deduplicated = []
        
        for slide in slides:
            slide_hash = slide['text_hash']
            
            if slide_hash not in seen_hashes:
                deduplicated.append(slide)
                seen_hashes.add(slide_hash)
            else:
                # Слайд с таким хешем уже был - пропускаем
                pass
        
        return deduplicated
    
    def smart_merge_slides(self, slides: List[Dict]) -> Dict:
        """
        Умное объединение слайдов в смысловые блоки.
        
        Стратегия: группируем похожие слайды и объединяем их,
        сохраняя только уникальный контент.
        
        Args:
            slides: Список слайдов
            
        Returns:
            Словарь со структурированным контентом
        """
        if not slides:
            return {'sections': []}
        
        sections = []
        current_section = {
            'start_page': slides[0]['page_num'],
            'end_page': slides[0]['page_num'],
            'items': slides[0]['items'].copy(),
            'item_hashes': {self._hash_text(item['text']) for item in slides[0]['items']},
        }
        
        for i in range(1, len(slides)):
            curr_slide = slides[i]
            
            # Вычисляем сходство с текущей секцией
            similarity = self.calculate_similarity(
                {'items': current_section['items']},
                curr_slide
            )
            
            if similarity >= self.similarity_threshold:
                # Слайд относится к текущей секции - добавляем только новые элементы
                for item in curr_slide['items']:
                    item_hash = self._hash_text(item['text'])
                    if item_hash not in current_section['item_hashes']:
                        current_section['items'].append(item)
                        current_section['item_hashes'].add(item_hash)
                
                current_section['end_page'] = curr_slide['page_num']
            else:
                # Начинается новая секция
                sections.append(current_section)
                current_section = {
                    'start_page': curr_slide['page_num'],
                    'end_page': curr_slide['page_num'],
                    'items': curr_slide['items'].copy(),
                    'item_hashes': {self._hash_text(item['text']) for item in curr_slide['items']},
                }
        
        # Добавляем последнюю секцию
        sections.append(current_section)
        
        return {'sections': sections}
    
    def export_to_markdown(
        self,
        deduplicated_data: any,
        strategy: str,
        original_doc: DoclingDocument,
    ) -> str:
        """
        Экспорт дедуплицированного контента в Markdown.
        
        Args:
            deduplicated_data: Дедуплицированные данные
            strategy: Использованная стратегия
            original_doc: Оригинальный DoclingDocument
            
        Returns:
            Markdown контент
        """
        md_lines = []
        
        # Заголовок
        md_lines.append(f"# {original_doc.name if hasattr(original_doc, 'name') else 'Презентация'}")
        md_lines.append("")
        md_lines.append(f"*Дедупликация выполнена методом: {strategy}*")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        if strategy == 'smart_merge' and isinstance(deduplicated_data, dict):
            # Экспорт по секциям
            for idx, section in enumerate(deduplicated_data['sections'], 1):
                start = section['start_page'] + 1  # +1 для человеческой нумерации
                end = section['end_page'] + 1
                
                if start == end:
                    md_lines.append(f"## Раздел {idx} (слайд {start})")
                else:
                    md_lines.append(f"## Раздел {idx} (слайды {start}-{end})")
                
                md_lines.append("")
                
                for item in section['items']:
                    label = item['label']
                    text = item['text']
                    
                    if 'heading' in label.lower():
                        md_lines.append(f"### {text}")
                    elif 'list' in label.lower():
                        md_lines.append(f"- {text}")
                    else:
                        md_lines.append(f"{text}")
                    
                    md_lines.append("")
                
                md_lines.append("---")
                md_lines.append("")
        
        elif isinstance(deduplicated_data, list):
            # Экспорт списком слайдов
            for slide in deduplicated_data:
                page_num = slide['page_num'] + 1
                is_incremental = slide.get('is_incremental', False)
                
                if is_incremental:
                    md_lines.append(f"### ➕ Дополнение к слайду {page_num}")
                else:
                    md_lines.append(f"## Слайд {page_num}")
                
                if 'similarity_to_prev' in slide:
                    sim = slide['similarity_to_prev'] * 100
                    md_lines.append(f"*Сходство с предыдущим: {sim:.1f}%*")
                
                md_lines.append("")
                
                for item in slide['items']:
                    label = item['label']
                    text = item['text']
                    
                    if 'heading' in label.lower():
                        md_lines.append(f"### {text}")
                    elif 'list' in label.lower():
                        md_lines.append(f"- {text}")
                    else:
                        md_lines.append(f"{text}")
                    
                    md_lines.append("")
                
                md_lines.append("---")
                md_lines.append("")
        
        # Статистика
        md_lines.append("## Статистика дедупликации")
        md_lines.append("")
        md_lines.append(f"- Исходных элементов: {self.stats['original_items']}")
        md_lines.append(f"- После дедупликации: {self.stats['deduplicated_items']}")
        md_lines.append(f"- Удалено дубликатов: {self.stats['removed_duplicates']}")
        
        if self.stats['original_items'] > 0:
            reduction = (self.stats['removed_duplicates'] / self.stats['original_items']) * 100
            md_lines.append(f"- Сокращение объема: {reduction:.1f}%")
        
        return '\n'.join(md_lines)
    
    def process_presentation(
        self,
        pdf_path: Path,
        strategy: str = 'smart_merge',
    ) -> Tuple[any, DoclingDocument]:
        """
        Обработка презентации с дедупликацией.
        
        Args:
            pdf_path: Путь к PDF презентации
            strategy: Стратегия дедупликации
                - 'sequential': последовательное сравнение
                - 'hashing': по хешам
                - 'smart_merge': умное объединение (рекомендуется)
            
        Returns:
            Кортеж (дедуплицированные данные, оригинальный документ)
        """
        print(f"\n📄 Обработка: {pdf_path.name}")
        print(f"   Стратегия: {strategy}")
        
        # Конвертация документа
        pipeline_options = PdfPipelineOptions()
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        
        result = converter.convert(str(pdf_path))
        doc = result.document
        
        # Извлечение содержимого по слайдам
        slides = self.extract_slides_content(doc)
        
        print(f"   Найдено слайдов: {len(slides)}")
        
        # Подсчет исходных элементов
        self.stats['original_items'] = sum(len(slide['items']) for slide in slides)
        
        # Дедупликация
        if strategy == 'sequential':
            deduplicated = self.deduplicate_sequential(slides)
        elif strategy == 'hashing':
            deduplicated = self.deduplicate_by_hashing(slides)
        elif strategy == 'smart_merge':
            deduplicated = self.smart_merge_slides(slides)
        else:
            raise ValueError(f"Неизвестная стратегия: {strategy}")
        
        # Подсчет результатов
        if isinstance(deduplicated, dict):
            self.stats['deduplicated_items'] = sum(
                len(section['items']) for section in deduplicated['sections']
            )
        else:
            self.stats['deduplicated_items'] = sum(
                len(slide['items']) for slide in deduplicated
            )
        
        self.stats['removed_duplicates'] = (
            self.stats['original_items'] - self.stats['deduplicated_items']
        )
        
        print(f"\n📊 Результаты дедупликации:")
        print(f"   Исходных элементов: {self.stats['original_items']}")
        print(f"   После обработки: {self.stats['deduplicated_items']}")
        print(f"   Удалено дубликатов: {self.stats['removed_duplicates']}")
        
        if self.stats['original_items'] > 0:
            reduction = (self.stats['removed_duplicates'] / self.stats['original_items']) * 100
            print(f"   Сокращение: {reduction:.1f}%")
        
        return deduplicated, doc


def main():
    """Основная функция для запуска из командной строки."""
    parser = argparse.ArgumentParser(
        description='Дедупликация повторяющегося контента в презентациях',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Умное объединение (рекомендуется для анимационных слайдов)
  python deduplicate_slides.py presentation.pdf -o output.md

  # Последовательное сравнение
  python deduplicate_slides.py presentation.pdf -o output.md -s sequential

  # С настройкой порога сходства
  python deduplicate_slides.py presentation.pdf -o output.md -t 0.90

Стратегии:
  - smart_merge (по умолчанию): объединяет похожие слайды в секции
  - sequential: сравнивает соседние слайды, оставляет только новое
  - hashing: удаляет полностью идентичные слайды
        """
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Путь к PDF презентации'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help='Путь для сохранения дедуплицированного контента'
    )
    
    parser.add_argument(
        '-s', '--strategy',
        type=str,
        choices=['sequential', 'hashing', 'smart_merge'],
        default='smart_merge',
        help='Стратегия дедупликации (по умолчанию: smart_merge)'
    )
    
    parser.add_argument(
        '-t', '--threshold',
        type=float,
        default=0.85,
        help='Порог сходства для объединения слайдов (0.0-1.0, по умолчанию: 0.85)'
    )
    
    parser.add_argument(
        '--min-length',
        type=int,
        default=10,
        help='Минимальная длина текста для учета (по умолчанию: 10)'
    )
    
    args = parser.parse_args()
    
    # Проверка входного файла
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Файл не найден: {input_path}")
        sys.exit(1)
    
    # Создание дедупликатора
    print("🚀 Инициализация дедупликатора")
    print("=" * 60)
    
    deduplicator = SlideDeduplicator(
        similarity_threshold=args.threshold,
        min_text_length=args.min_length,
    )
    
    # Обработка
    print(f"\n📚 Дедупликация презентации...")
    print("=" * 60)
    
    try:
        deduplicated_data, original_doc = deduplicator.process_presentation(
            input_path,
            strategy=args.strategy,
        )
        
        # Экспорт
        print(f"\n💾 Экспорт результата...")
        print("=" * 60)
        
        markdown_content = deduplicator.export_to_markdown(
            deduplicated_data,
            args.strategy,
            original_doc,
        )
        
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown_content, encoding='utf-8')
        
        print(f"\n✅ Готово! Результат сохранен в: {output_path}")
        
        # Итоговая статистика
        print(f"\n" + "=" * 60)
        print("ИТОГИ")
        print("=" * 60)
        print(f"📊 Исходный размер: {deduplicator.stats['original_items']} элементов")
        print(f"📊 После дедупликации: {deduplicator.stats['deduplicated_items']} элементов")
        print(f"📊 Экономия: {deduplicator.stats['removed_duplicates']} элементов")
        
        if deduplicator.stats['original_items'] > 0:
            reduction = (deduplicator.stats['removed_duplicates'] / 
                        deduplicator.stats['original_items']) * 100
            print(f"📊 Сокращение объема: {reduction:.1f}%")
        
    except Exception as e:
        print(f"\n❌ Ошибка при обработке: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

