import RPi.GPIO as GPIO
import serial
import time

TRIG = 24  # Pin TRIG 
ECHO = 23  # Pin ECHO 

GPIO.setmode(GPIO.BCM)  
GPIO.setup(TRIG, GPIO.OUT)  
GPIO.setup(ECHO, GPIO.IN)  

# Función para leer duty desde archivo
def leer_duty_cycle():
    try:
        with open("dutycycle.txt", "r") as file:
            duty = int(file.read().strip())
            if 0 <= duty <= 100:
                return duty
            else:
                print("Valor fuera de rango (0-100)")
                return 50
    except:
        print("Error leyendo el archivo.")
        return 50
# Función para medir distancia
def medir_distancia():
    # Enviar un pulso en TRIG
    GPIO.output(TRIG, GPIO.LOW)  # Aseguramos que TRIG esté apagado
    time.sleep(0.1)  # Esperamos un poco antes de activar el pulso
    GPIO.output(TRIG, GPIO.HIGH)  # Activamos TRIG
    time.sleep(0.00001)  # El pulso debe durar 10 microsegundos
    GPIO.output(TRIG, GPIO.LOW)  # Desactivamos TRIG

    # Medir el tiempo que tarda en llegar el pulso de ECHO
    while GPIO.input(ECHO) == GPIO.LOW:
        inicio = time.time()  # Guardamos el tiempo en que comienza el pulso

    while GPIO.input(ECHO) == GPIO.HIGH:
        fin = time.time()  # Guardamos el tiempo en que termina el pulso

    # Calcular la distancia (la velocidad del sonido es 343 m/s)
    duracion = fin - inicio  # Duración del pulso en segundos
    distancia = duracion * 34300  # Convertimos la duración en centímetros
    return distancia

# UART
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()
time.sleep(2)
print("UART conectado en /dev/ttyACM0")

last_distance = None  # Variable para almacenar la última distancia

try:
    while True:
        # Medir distancia
        distancia = medir_distancia()
        print("Distancia medida: %.1f cm" % distancia)

        # Leer el archivo de texto
        duty = leer_duty_cycle()
        print(f"Motor activado con {duty}%")

        # Verificar si hay un cambio en la distancia
        if last_distance is None or abs(distancia - last_distance) > 1:  # Si hay un cambio significativo
            if (distancia > 25):
                ser.write("5\n".encode('utf-8'))  # Enviar 5 si la distancia es mayor a 15 cm
                ser.write(f"{duty}\n".encode('utf-8'))
                print("'dutycycle' enviado")
            else:
                ser.write("0\n".encode('utf-8'))  # Enviar 0 si la distancia es menor o igual a 15 cm
            last_distance = distancia  # Actualizar la última distancia

        # Esperar 1 segundo antes de la siguiente medición
        time.sleep(0.0005) 

        # Leer respuesta de la Tiva
        raw = ser.readline()
        value = raw.decode('utf-8').strip()
        print(f"Tiva dice: {value}")
except KeyboardInterrupt:
    print("Programa terminado por el usuario.")

finally:
    ser.close()
