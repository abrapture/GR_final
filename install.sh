#!/bin/bash
# Скрипт для установки Docling и проверки установки

echo "🚀 Установка Docling..."
echo "================================"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8 или выше."
    exit 1
fi

echo "✓ Python найден: $(python3 --version)"
echo ""

# Установка pip если не установлен
if ! command -v pip3 &> /dev/null; then
    echo "⚠️  pip3 не найден. Устанавливаю pip..."
    python3 -m ensurepip --upgrade
fi

echo "✓ pip найден: $(pip3 --version)"
echo ""

# Обновление pip
echo "📦 Обновление pip..."
pip3 install --upgrade pip
echo ""

# Установка Docling
echo "📥 Установка Docling..."
pip3 install docling

echo ""
echo "================================"
echo "✓ Установка завершена!"
echo "================================"
echo ""

# Проверка установки
echo "🔍 Проверка установки..."
python3 << EOF
try:
    from docling.document_converter import DocumentConverter
    print("✓ Docling установлен успешно!")
    print("✓ Готов к использованию!")
except ImportError as e:
    print("❌ Ошибка при импорте Docling:", e)
    print("Попробуйте переустановить: pip3 install --upgrade docling")
EOF

echo ""
echo "================================"
echo "📚 Следующие шаги:"
echo "================================"
echo "1. Прочитайте QUICKSTART.md для быстрого старта"
echo "2. Запустите: python3 extract_pdf.py your_file.pdf"
echo "3. Изучите примеры: python3 example_usage.py"
echo ""
echo "📖 Полная документация: README.md"
echo "🌐 Официальный сайт: https://docling-project.github.io/docling/"
echo ""

