# Importamos flask, request y render template
from flask import Flask, request, render_template
from datetime import datetime
from hashlib import sha256
import json


tiempo = str(datetime.today())

class Bloque:
    def __init__(self, index, transacciones, timestamp, hash_anterior, nonce=0):
        self.index = index
        self.transacciones = transacciones
        self.timestamp = timestamp
        self.hash_anterior = hash_anterior
        self.nonce = nonce


    def criptador(self):
        bloque_string = json.dumps(self.__dict__, sort_keys=True)
        
        return sha256(bloque_string.encode()).hexdigest()
        
        

class Blockchain:
    def __init__(self):
        self.transacciones_pendientes = []
        self.cadena = []
        self.crear_bloque_genesis()

 
    def crear_bloque_genesis(self):
        bloque_genesis = Bloque(0, ["Bloque genesis"], tiempo, '0')
        bloque_genesis.hash = bloque_genesis.criptador()

        self.cadena.append(bloque_genesis)
    
    @property
    def ultimo_bloque(self):
        return self.cadena[-1]

    
    dificultad = 2
    def prueba_de_trabajo(self, bloque):
        bloque.nonce = 0

        bloque_criptado = bloque.criptador()

        while not bloque_criptado.startswith('0'* Blockchain.dificultad):
            bloque.nonce += 1

            bloque_criptado = bloque.criptador()
        return bloque_criptado

    def prueba_de_trabajo_validada(self, bloque, hash_del_bloque):
        return(hash_del_bloque.startswith('0' * Blockchain.dificultad) and 
               hash_del_bloque == bloque.criptador())
        
    def agregar_bloque(self, bloque, prueba):
        hash_anterior = self.ultimo_bloque.hash
        if hash_anterior != bloque.hash_anterior:
            return False
        
        if not self.prueba_de_trabajo_validada(bloque, prueba):
            return False
        
        bloque.hash = prueba

        self.cadena.append(bloque)
        return True
    
    
    def agregar_transacciones(self, transaccion):
        self.transacciones_pendientes.append(transaccion)


    def cerrar_bloque(self):
        if not self.transacciones_pendientes:
            return False
        
        ultimo_bloque = self.ultimo_bloque

        nuevo_bloque = Bloque(ultimo_bloque.index + 1, transacciones=self.transacciones_pendientes, timestamp=tiempo, hash_anterior=ultimo_bloque.hash)

        prueba = self.prueba_de_trabajo(nuevo_bloque)

        self.agregar_bloque(nuevo_bloque, prueba)

        self.transacciones_pendientes = []
        return nuevo_bloque.index
    


## Comienza el flask ##

# Instanciamos flask
app = Flask(__name__)

#Instanciamos la blockchain que habiamos creado
pengucoin = Blockchain()


@app.route('/')
def index():
    return render_template('base.html')

@app.route('/cerrar', methods=['GET', 'POST'])
def minar():
    # Para cerrar el bloque llamamos a nuestra funcion de cerrar bloque
    if request.method == 'POST':
        pengucoin.cerrar_bloque()
    return render_template('minar.html')

@app.route('/transaccion/nueva', methods=['GET', 'POST'])
def nueva_transaccion():
    if request.method == 'POST':
        # Para agregar la transaccion
        
        # Recibimos la transaccion del html y la guardamos dentro de una variable
        transaccion = request.form['nueva_transaccion']

        # Agregamos la transaccion a la lista de transacciones pendientes (mempool)
        nueva_transaccion = pengucoin.agregar_transacciones(transaccion)
    
        return render_template('transaccion_nueva.html'), nueva_transaccion
    return render_template('transaccion_nueva.html')


@app.route('/cadena', methods=['GET'])
def cadena_completa():
    #Vemos toda la cadena de la blockchain
    cadena = []
    for bloque in pengucoin.cadena:
        cadena.append(bloque.__dict__)
    
    return render_template('cadena.html', cadena=cadena)
    

#Con esto configuramos nuestro servidor flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)