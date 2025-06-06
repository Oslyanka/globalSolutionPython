# Detector de Quedas em Vídeos para Situações de Apagão

## Descrição do Problema
Durante apagões ou emergências, pessoas podem sofrer quedas em casa sem serem socorridas a tempo. Câmeras de segurança perdem efetividade quando não há quem monitore as imagens em tempo real. Este projeto visa automatizar a detecção de situações de risco, como quedas, imobilidade ou ausência da pessoa no vídeo.

## Objetivo
Criar um sistema automatizado de análise de vídeo para:
- Detectar quedas ou situações de risco em tempo real
- Emitir alertas visuais imediatos
- Ajudar no monitoramento mesmo com baixa iluminação

## Tecnologias Utilizadas
- Python 3
- OpenCV
- MediaPipe

## Como Funciona

O sistema analisa vídeos e usa pontos do corpo (pose estimation) para verificar:
- Queda ou deitar repentino
- Imobilidade (possível inconsciência)
- Ausência de pessoa na cena

Quando um risco é identificado, o alerta é exibido na tela.

## Vídeo Demonstrativo
[Link do vídeo demonstrativo no YouTube](https://youtu.be/SEU_LINK_AQUI)

## Como Executar

1. Instale as dependências:
```
pip install opencv-python mediapipe
```

2. Execute o sistema:
```
python detector_quedas.py
```

3. Insira o caminho do vídeo quando solicitado:
```
Digite o caminho do arquivo de video: exemplo.mp4
```

4. Pressione:
- `q` para sair
- `r` para resetar alertas

## Integrantes do Grupo

- Aksel Viktor Caminha Rae - RM99011
- Ian Xavier Kuraoka - RM98860
- Arthur Wollmann Petrin - RM98735

## Código Fonte
O código está disponível neste repositório no arquivo `detector_quedas.py`.
