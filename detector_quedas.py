# detector de quedas para apagoes - versao melhorada
import cv2
import mediapipe as mp
import time

# configuracao do mediapipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# variaveis globais
contador_alertas = 0
tempo_sem_pessoa = 0
ultima_posicao_cabeca = 0
historico_movimento = []

def verificar_queda(landmarks):
    # pega a posicao da cabeca (nariz)
    nariz = landmarks[mp_pose.PoseLandmark.NOSE.value]
    posicao_cabeca = nariz.y
    
    # pega posicao dos pes
    pe_esquerdo = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    pe_direito = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    
    # pega posicao dos ombros
    ombro_esq = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    ombro_dir = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    
    # pega posicao dos quadris
    quadril_esq = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    quadril_dir = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    
    # calcula se a pessoa ta em pe ou deitada
    if pe_esquerdo.y > 0 and pe_direito.y > 0:
        altura_pessoa = abs(posicao_cabeca - max(pe_esquerdo.y, pe_direito.y))
    else:
        altura_pessoa = 1.0  # valor padrao se nao conseguir detectar os pes
    
    mensagem = "Normal"
    tem_queda = False
    
    # verifica se a altura for muito pequena, pode ser queda
    if altura_pessoa < 0.4:
        tem_queda = True
        mensagem = "ALERTA: Pessoa pode ter caido!"
    
    # verifica se a cabeca ta muito baixa
    elif posicao_cabeca > 0.7:  # 0.7 significa que ta na parte de baixo da tela
        tem_queda = True
        mensagem = "ALERTA: Cabeca muito baixa!"
    
    # verifica os ombros pra ver inclinacao
    diferenca_ombros = abs(ombro_esq.y - ombro_dir.y)
    if diferenca_ombros > 0.15:
        tem_queda = True
        mensagem = "ALERTA: Pessoa muito inclinada!"
    
    # verifica se os ombros tao quase na mesma altura dos quadris (pessoa deitada)
    altura_ombros = (ombro_esq.y + ombro_dir.y) / 2
    altura_quadris = (quadril_esq.y + quadril_dir.y) / 2
    diferenca_altura = abs(altura_ombros - altura_quadris)
    
    if diferenca_altura < 0.1:  # se a diferenca for muito pequena, pessoa ta deitada
        tem_queda = True
        mensagem = "ALERTA: Pessoa parece estar deitada!"
    
    return tem_queda, mensagem

def verificar_pessoa_parada(landmarks):
    global historico_movimento
    
    # pega alguns pontos importantes pra calcular movimento
    nariz = landmarks[mp_pose.PoseLandmark.NOSE.value]
    ombro_esq = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    ombro_dir = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    
    # calcula uma posicao media
    posicao_atual = (nariz.x + ombro_esq.x + ombro_dir.x) / 3
    
    # adiciona no historico
    historico_movimento.append(posicao_atual)
    
    # mantem so os ultimos 20 frames
    if len(historico_movimento) > 20:
        historico_movimento.pop(0)
    
    # se nao tem historico suficiente, nao analisa
    if len(historico_movimento) < 10:
        return False, "Analisando movimento..."
    
    # calcula se a pessoa ta se movendo
    movimento_total = 0
    for i in range(len(historico_movimento) - 1):
        movimento = abs(historico_movimento[i+1] - historico_movimento[i])
        movimento_total = movimento_total + movimento
    
    movimento_medio = movimento_total / len(historico_movimento)
    
    # se o movimento eh muito pequeno, pessoa pode estar inconsciente
    if movimento_medio < 0.01:
        return True, "ALERTA: Pessoa parece imovel!"
    
    return False, "Pessoa se movendo normalmente"

def processar_video(caminho_arquivo):
    global contador_alertas, tempo_sem_pessoa
    
    # abre o video
    video = cv2.VideoCapture(caminho_arquivo)
    
    if not video.isOpened():
        print("Erro: nao conseguiu abrir o video")
        return
    
    print("Sistema de Deteccao de Quedas Iniciado")
    print("Monitorando para situacoes de emergencia durante apagoes...")
    
    frame_numero = 0
    alertas_consecutivos = 0
    
    while True:
        # le o proximo frame
        sucesso, frame = video.read()
        
        if not sucesso:
            # se acabou o video, volta pro comeco
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frame_numero = 0
            print("Video reiniciado automaticamente")
            continue
        
        frame_numero = frame_numero + 1
        
        # converte pra rgb (mediapipe precisa de rgb)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # detecta a pose
        resultado = pose.process(frame_rgb)
        
        # variaveis pra status
        status_principal = "Monitorando area..."
        cor_principal = (0, 255, 0)  # verde
        status_secundario = ""
        
        # se encontrou uma pessoa
        if resultado.pose_landmarks:
            tempo_sem_pessoa = 0
            
            # desenha o esqueleto
            mp_drawing.draw_landmarks(frame, resultado.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            # verifica se tem queda
            tem_queda, mensagem_queda = verificar_queda(resultado.pose_landmarks.landmark)
            
            # verifica se a pessoa ta parada
            pessoa_parada, mensagem_movimento = verificar_pessoa_parada(resultado.pose_landmarks.landmark)
            
            # decide qual alerta mostrar
            if tem_queda:
                status_principal = mensagem_queda
                cor_principal = (0, 0, 255)  # vermelho
                contador_alertas = contador_alertas + 1
                alertas_consecutivos = alertas_consecutivos + 1
                
                # se tem muitos alertas seguidos, pode ser emergencia real
                if alertas_consecutivos > 10:
                    status_secundario = "EMERGENCIA: Verificar imediatamente!"
                
            elif pessoa_parada:
                status_principal = mensagem_movimento
                cor_principal = (0, 165, 255)  # laranja
                status_secundario = "Monitorar consciencia da pessoa"
                
            else:
                status_principal = "Pessoa detectada - Status normal"
                cor_principal = (0, 255, 0)  # verde
                status_secundario = mensagem_movimento
                alertas_consecutivos = 0  # reseta contador se ta tudo normal
            
        else:
            # nao encontrou pessoa
            tempo_sem_pessoa = tempo_sem_pessoa + 1
            
            if tempo_sem_pessoa > 30:  # mais de 1 segundo sem pessoa
                status_principal = "ATENCAO: Nenhuma pessoa detectada!"
                cor_principal = (0, 255, 255)  # amarelo
                status_secundario = "Verificar se alguem precisa de ajuda"
            else:
                status_principal = "Procurando pessoas na area..."
                cor_principal = (255, 255, 255)  # branco
            
            alertas_consecutivos = 0
        
        # desenha as informacoes na tela
        cv2.putText(frame, status_principal, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor_principal, 2)
        
        if status_secundario:
            cv2.putText(frame, status_secundario, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # informacoes do sistema
        cv2.putText(frame, f"Frame: {frame_numero}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Total de Alertas: {contador_alertas}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
        # titulo do sistema
        cv2.putText(frame, "SISTEMA DE EMERGENCIA - DETECTOR DE QUEDAS PARA APAGOES", (10, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, "Pressione 'q' para sair | 'r' para resetar contador", (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # mostra o frame
        cv2.imshow('Detector de Quedas - Sistema de Emergencia', frame)
        
        # verifica se apertou alguma tecla
        tecla = cv2.waitKey(30) & 0xFF
        if tecla == ord('q'):
            break
        elif tecla == ord('r'):
            contador_alertas = 0
            alertas_consecutivos = 0
            historico_movimento = []
            print("Contadores resetados")
    
    video.release()
    cv2.destroyAllWindows()
    
    # mostra relatorio final
    print("=" * 50)
    print("RELATORIO FINAL DO MONITORAMENTO")
    print("=" * 50)
    print(f"Frames processados: {frame_numero}")
    print(f"Total de alertas de queda: {contador_alertas}")
    print("Sistema finalizado")

def main():
    print("=" * 60)
    print("SISTEMA DE DETECCAO DE QUEDAS PARA SITUACOES DE APAGAO")
    print("=" * 60)
    print("Este sistema foi desenvolvido para:")
    print("- Monitorar pessoas durante faltas de energia")
    print("- Detectar quedas e situacoes de emergencia")
    print("- Alertar sobre pessoas que podem precisar de ajuda")
    print("- Funcionar em ambientes com pouca iluminacao")
    print()
    print("Tecnologias utilizadas: Python + MediaPipe + OpenCV")
    print()
    
    # pede o arquivo de video
    arquivo = input("Digite o caminho do arquivo de video: ")
    
    # remove aspas se o usuario colocou
    arquivo = arquivo.strip('"').strip("'")
    
    # verifica se o arquivo existe
    try:
        teste = cv2.VideoCapture(arquivo)
        if not teste.isOpened():
            print("Erro: arquivo nao encontrado ou formato nao suportado")
            print("Certifique-se que o arquivo existe e eh um video valido")
            return
        teste.release()
    except:
        print("Erro ao tentar abrir o arquivo")
        return
    
    print("Arquivo de video carregado com sucesso!")
    print("Iniciando sistema de monitoramento...")
    print("IMPORTANTE: Este sistema pode salvar vidas durante apagoes!")
    
    # processa o video
    try:
        processar_video(arquivo)
    except KeyboardInterrupt:
        print("Sistema interrompido pelo usuario")
    except Exception as e:
        print(f"Erro durante execucao: {e}")
    
    print("Obrigado por usar o Sistema de Deteccao de Quedas!")

# executa o programa
if __name__ == "__main__":
    main()