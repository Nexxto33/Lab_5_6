import RPi.GPIO as GPIO
import serial
import time
import random

TRIG = 22  
ECHO = 26  
IN1 = 5
IN2 = 6
ENA = 13
button2 = 20
on = 1
off = 0
buzzer_on = False
cont = 0

GPIO.setmode(GPIO.BCM)  
GPIO.setup(TRIG, GPIO.OUT)  
GPIO.setup(ECHO, GPIO.IN)  
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Inicializar PWM
pwm = GPIO.PWM(ENA, 1000)
pwm.start(0)
GPIO.output(IN1, GPIO.LOW)
GPIO.output(IN2, GPIO.HIGH)

# Función para medir distancia
def medir_distancia():
    GPIO.output(TRIG, GPIO.LOW) 
    time.sleep(0.1)  
    GPIO.output(TRIG, GPIO.HIGH) 
    time.sleep(0.00001)  
    GPIO.output(TRIG, GPIO.LOW)  

    while GPIO.input(ECHO) == GPIO.LOW:
        inicio = time.time() 

    while GPIO.input(ECHO) == GPIO.HIGH:
        fin = time.time()  

    duracion = (fin - inicio)/2  
    distancia = duracion * 34300  
    return distancia
# UART
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()
time.sleep(2)
print("UART conectado en /dev/ttyACM0")

last_distance = None  # Variable para almacenar la última distancia
# Programa principal

try:
    while True:
        distancia = medir_distancia()
        print("Distancia medida: %.1f cm" % distancia)
        if distancia<7:
            pwm.ChangeDutyCycle(100)
        else:
            pwm.ChangeDutyCycle(0)
        time.sleep(1)  
        temperature = (random.uniform(0, 35))
        #ser.write(f"{temperature}\n".encode('utf-8'))
        print("Temperatura: %.1f C" % off)
        time.sleep(2)
        # Leer respuesta de la Tiva
        raw = ser.readline()
        value = raw.decode('utf-8').strip()
        print(f"Tiva dice: {value}")
        if GPIO.input(button2) == GPIO.LOW:
            off=off+1
            ser.write(f"{off}\n".encode('utf-8'))
            print("Boton Rasp apretado")
            time.sleep(0.5)
            
except KeyboardInterrupt:
    print("Medición interrumpida por el usuario")

finally:
    GPIO.cleanup() 
