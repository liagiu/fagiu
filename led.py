from flask import Flask, render_template, request
import datetime
import subprocess
import RPi.GPIO as GPIO
import os
import glob
import time

 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

app = Flask (__name__)

GPIO.setwarnings(False)

GPIO.setmode(GPIO. BOARD)

estado = {'olho_esq' : False, 'olho_dir' : False }

olho_esq = 16

olho_dir = 18

setpoint = None

GPIO.setup(olho_esq, GPIO.OUT)

GPIO.setup(olho_dir, GPIO.OUT)

GPIO.output(olho_esq, False)

GPIO.output(olho_dir, False)




def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

    
def read_temp():
    lines = read_temp_raw()
    if len(lines) > 0:
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0 
            
            return "{:.1f}".format(temp_c)
    else:
        return 0

@app.route("/")

def inicio():
 return mostra_estado()

@app.route("/olho_esq/1")
def ligar_olho_esq():
  GPIO.output(olho_esq, True)
  return mostra_estado()

@app.route("/olho_esq/0")
def desl_olho_esq(): 
  GPIO.output(olho_esq, False)
  return mostra_estado()

@app.route("/olho_dir/1")
def ligar_olho_dir(): 
  GPIO.output(olho_dir, True) 
  return mostra_estado()

@app.route("/olho_dir/0") 
def desl_olho_dir(): 
 GPIO.output (olho_dir, False)
 return mostra_estado()

@app.route("/temp")
def mostrar_temp():
  temp = read_temp()
  return render_template('temperatura.html', temperatura=temp)

@app.route("/temp", methods = ['POST'])
def receber_setpoint():
    setpoint = request.get_json()["setpoint"]
    print(setpoint)
    return setpoint

def mostra_estado():
  estado = {

    'olho_esq' : GPIO.input(olho_esq),

    'olho_dir' : GPIO.input(olho_dir)

  }

  return render_template('fagiu.html', **estado)

if __name__ == "__main__":
  print("Servidor: " + subprocess.getoutput('hostname -I'). strip() + ":5000")

app.run(host='0.0.0.0', debug=False)