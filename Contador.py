import cv2
import time 

# Inicializar la captura de video desde la cámara
url = "http://192.168.0.5:8080/video"
cap = cv2.VideoCapture(url)  # Reemplaza 'video.mp4' con el nombre de tu archivo de video

# Variables para el seguimiento de personas
contador_entrada = 0
contador_salida = 0

# Coordenadas de la línea de detección (posición de la puerta)
#linea_x = 300  # Ajusta esta coordenada según la posición de tu puerta

# Umbral para la detección de movimiento
umbral_deteccion = 12000  # Ajusta este valor según tus necesidades

x_prev, y_prev = None, None

# Variables para el cálculo de la variación total en 1 segundo
delta_x_total = 0
tiempo_inicial = time.time()

cont = 0

while(cap.isOpened()):
    ret, frame = cap.read()
    if not ret:
        break

    # Convertir el frame a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    diferencia = gray

    # Calcular la diferencia entre dos frames consecutivos
    if 'previous_frame' in locals():
        diferencia = cv2.absdiff(previous_frame, gray)
        #cv2.imshow("dif",cv2.resize(diferencia,(800,1000)))
    previous_frame = gray

    # Aplicar umbral para detectar el movimiento
    _, umbral = cv2.threshold(diferencia, 30, 255, cv2.THRESH_BINARY)
    #cv2.imshow("umbral",cv2.resize(umbral,(800,1000)))

    # Encontrar contornos en la imagen umbral
    contours, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(frame,contours,-1,(0,0,255),2)
    for contour in contours:
        if cv2.contourArea(contour) > umbral_deteccion:
            x, y, w, h = cv2.boundingRect(contour)
            #cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0),2)

            if x_prev is not None and y_prev is not None:
            # Calcula la variación en las coordenadas
                delta_x = x - x_prev
                delta_x_total += delta_x
                # Imprime la variación en las coordenadas
                #print(f"Variación en X: {delta_x}")

            x_prev, y_prev = x, y

            

    # Dibujar la línea de detección
    #cv2.line(frame, (linea_x, 0), (linea_x, frame.shape[0]), (0, 0, 255), 2)

     # Comprobar si ha transcurrido 1 segundo
    tiempo_actual = time.time()
    if tiempo_actual - tiempo_inicial >= 2.0:
        if cont % 2 == 0:
            print(f"Variación total en X durante 2 segundo: {delta_x_total}")

            # Determinar la dirección del movimiento
            if delta_x_total < 0:
                contador_entrada += 1
            elif delta_x_total > 0:
                contador_salida += 1

            delta_x = 0
            x = 0
            delta_x_total = 0  # Reiniciar el contador de variación

            # Actualizar el tiempo inicial
            tiempo_inicial = tiempo_actual
        else: 
            tiempo_inicial = tiempo_actual
            delta_x_total = 0
        cont += 1

     # Mostrar el número de personas que entran y salen
    cv2.putText(frame, f'Entrada: {contador_entrada}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, f'Salida: {contador_salida}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Mostrar el frame con las detecciones
    cv2.imshow('Detección de Movimiento', cv2.resize(frame,(800,1000)))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura de video y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()