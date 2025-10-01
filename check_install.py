#!/usr/bin/env python3
"""
Скрипт для проверки установки Docling и готовности системы.
"""

import sys


def check_python_version():
    """Проверка версии Python."""
    version = sys.version_info
    print(f"🐍 Python версия: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Требуется Python 3.8 или выше")
        return False
    else:
        print("✓ Версия Python подходит")
        return True


def check_docling():
    """Проверка установки Docling."""
    try:
        from docling.document_converter import DocumentConverter
        print("\n📦 Docling:")
        print("✓ Docling установлен успешно")
        return True
    except ImportError as e:
        print("\n📦 Docling:")
        print(f"❌ Docling не установлен: {e}")
        print("\n💡 Установите командой:")
        print("   pip install docling")
        print("   или запустите: ./install.sh")
        return False


def check_optional_dependencies():
    """Проверка опциональных зависимостей."""
    print("\n🔧 Опциональные зависимости:")
    
    deps = {
        "PIL": "Pillow (для работы с изображениями)",
        "easyocr": "EasyOCR (для OCR сканированных документов)",
        "pytesseract": "PyTesseract (альтернатива для OCR)"
    }
    
    for module, description in deps.items():
        try:
            __import__(module)
            print(f"✓ {description} - установлен")
        except ImportError:
            print(f"⚠  {description} - не установлен (опционально)")


def check_files():
    """Проверка наличия необходимых файлов."""
    from pathlib import Path
    
    print("\n📁 Файлы проекта:")
    
    required_files = [
        "extract_pdf.py",
        "example_usage.py",
        "requirements.txt",
        "README.md",
        "QUICKSTART.md"
    ]
    
    all_present = True
    for filename in required_files:
        if Path(filename).exists():
            print(f"✓ {filename}")
        else:
            print(f"❌ {filename} не найден")
            all_present = False
    
    return all_present


def main():
    """Основная функция проверки."""
    print("=" * 60)
    print("ПРОВЕРКА УСТАНОВКИ DOCLING")
    print("=" * 60)
    
    # Проверки
    python_ok = check_python_version()
    docling_ok = check_docling()
    check_optional_dependencies()
    files_ok = check_files()
    
    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ПРОВЕРКИ")
    print("=" * 60)
    
    if python_ok and docling_ok and files_ok:
        print("✓ ✓ ✓ Всё готово к работе! ✓ ✓ ✓")
        print("\n📖 Следующие шаги:")
        print("   1. Прочитайте QUICKSTART.md")
        print("   2. Запустите: python extract_pdf.py your_file.pdf")
        print("   3. Изучите примеры: python example_usage.py")
        return 0
    else:
        print("⚠️  Обнаружены проблемы")
        if not docling_ok:
            print("\n💡 Запустите установку:")
            print("   ./install.sh")
            print("   или")
            print("   pip install docling")
        return 1


if __name__ == "__main__":
    sys.exit(main())

