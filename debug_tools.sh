#!/bin/bash

echo "🔧 Painel de debug:"
echo "1 - Rodar main.py"
echo "2 - Testar Compositor"
echo "3 - Ver logs ao vivo"
echo "4 - Sair"
read -p "Escolha: " opcao

case $opcao in
  1) python main.py ;;
  2) python windows/compositor_window.py ;;
  3) tail -f logs/runtime.log ;;
  *) echo "🚪 Saindo..." ;;
esac

