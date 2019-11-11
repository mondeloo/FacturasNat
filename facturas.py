# -*- coding: utf-8 -*-
from sheetfu import SpreadsheetApp
import os

def clear(): return os.system('cls')

# mensaje de carga para no ver la consola vacia mientras corre el codigo
hojas = []  # contendrá todas las hojas que se carguen
print(" >> Bienvenido a la aplicacion que analiza su factura de Naturgy! <<")
print(" >> Estamos cargando la base de datos")
JSON_FILE = str(input("Especifica el nombre del archivo .json(incluyendo .json)\n"))
# ----------##############-----------------------------------CODE---------------------##################----------
# -------------------------------------------------------DEFINICIONES---------------------------------------------
# clase que equivaldra a cada Día conteniendo su fecha, consumos y consumo total
# clase que consigue los valores de la hoja de calculo ya filtrados para su uso
# la propediedad definitiva solo contiene una lista de los consumos
# las listas de los consumos son: [fecha,hora inicio,hora fin,periodo(valle/punta),consumo,precio unitario,precio total]
# fecha y hora inicio se especifica que tienen formato unicode(u"..."), pero se pueden tratar normal ya que la codificacion de python es unicode por defecto(utf-8)
# ejemplo Día: [u'08/10/2018', u'15', 16, u'Energ\xeda Activa Punta', 0.473, 0.09003, 0.04258]

class dia:
    # objeto con las propiedades: consumos(lista del consumo por hora), fecha, consumo total del Día, consumo total en valle, consumo total en punta
    def __init__(self,fecha,inicio,fin):
        self.consumos = []
        self.fecha = fecha
        self.consumo_total = 0
        self.consumo_punta = 0
        self.consumo_valle = 0
        self.precio_total = 0
        self.inicio = inicio
        self.fin = fin
    # metodo para añadir consumos a la lista

    def anadir_consumo(self, consumo):
        self.consumos.append(consumo)
    # metodos que dan valor a algunas propiedades

    def calculo_total(self):
        total = 0
        for item in self.consumos:
            total += item[2]
        return total

    def calculo_valle(self):
        total = 0
        for item in self.consumos:
            if item[0] < self.inicio or item[0] > self.fin:
                total += item[2]
            else:
                continue
        return total

    def calculo_punta(self):
        total = 0
        for item in self.consumos:
            if item[0] > (self.inicio - 1) and item[0] < (self.fin + 1):
                total += item[2]
            else:
                continue
        return total
    # metodo que completa los datos del objeto que usare cuando tenga completa la lista consumos

    def calculo_precio(self):
        total = 0
        for item in self.consumos:
            total += item[3]
        return total
    
    def completar_datos(self):
        #no salta ninguno de los tres errores pero todos los consumos dan 0
        try:
            self.consumo_total = self.calculo_total()
        except:
            print(" ERror en total ")
        try:
            self.consumo_valle = self.calculo_valle()
        except:
            print(" ERror en valle")
        try:
            self.consumo_punta = self.calculo_punta()
        except:
            print(" ERror en punta")
        try:
            self.precio_total = self.calculo_precio()
        except:
            print(" ERror en precio")
             
############################---------------------------------------############################
# funcion que pasa del formato de VALUES a formato consumo para almacenar en objetos de clase Día

def crear_consumo(elemento):
    # hay que pasarlos a integer porque vienen en string
    hora_inicio = int(elemento[1])
    hora_fin = int(elemento[2])
    kwh = elemento[4]  # es un numero decimal por lo que no se pasa a integer
    precio = elemento[6]
    return [hora_inicio, hora_fin, kwh,precio]

############################---------------------------------------############################

class hoja_calculo_factura:
    #hoja con consumos de una factura
    def __init__(self, id, name, denominacion,inicio,fin):
        self.id = id
        self.name = name
        self.denominacion = denominacion
        self.registros = []
        self.definitiva = []
        self.consumo_dias = []
        self.inicio = inicio
        self.fin = fin
        self.diferencia_total = 0
        self.diferencia_punta = 0
        self.diferencia_valle = 0
        self.diferencia_precio = 0

    def conseguir_valores(self):
        try:
            spreadsheet = SpreadsheetApp(JSON_FILE).open_by_id(self.id)
            sheet = spreadsheet.get_sheet_by_name(self.name)
            data_range = sheet.get_data_range()
            self.registros = data_range.get_values()
        except:
            print("No conecta con la sheet")

    def filtrar_registros(self):
        filtrada = []#que hace esto??
        for item in self.registros:
            if item[0] == "Consumo agrupado:":
                break
            try:
                fecha = item[0].split("/")
                if len(fecha) == 3:
                    filtrada.append(item)
            except:
                continue
        return filtrada

    def calcular_consumo_dias(self):
        self.conseguir_valores()
        self.definitiva = self.filtrar_registros()
        # creo el primer objeto día con el indice de comienzo especificado al principio
        # añado el primer objeto a la lista para poder comparar con algun objeto en la primera iteracion
        fecha_1 = self.definitiva[0][0]
        try:
            valor = dia(fecha_1,self.inicio,self.fin)
        except:
            print("No crea el dia")
        self.consumo_dias.append(valor)
        # bucle para crear lista con objetos de cada Día
        try: #si no pongo el try no funciona ??????¿¿¿¿¿¿¿¿¿¿¿
            k =0
            for item in self.definitiva:  # item es una entrada de consumo de un Día una hora
                # fecha es la fecha de una entrada de google sheet
                fecha = item[0]
                for elemento in self.consumo_dias:  # elemento es un objeto Día correspondiente a una fecha
                    if fecha == elemento.fecha:  # si la fecha ya está guardada en consumo dias
                        # creamos un formato consumo con la entrada
                        consumo = crear_consumo(item)
                        # añadimos el consumo a los consumos del objeto con fecha igual
                        elemento.anadir_consumo(consumo)
                        coincidencia = True
                        break  # si hubo coincidencia salimos del bucle puesto que solo puede coincidir una vez
                    else:
                        coincidencia = False
                if coincidencia == False:  # si la fecha no se encontraba ya guardada crea un objeto con esa fecha le añade el consumo de la entrada y lo guarda en la lista consumo_dias
                    valor = dia(fecha,self.inicio,self.fin)
                    valor.anadir_consumo(crear_consumo(item))
                    self.consumo_dias.append(valor)
                    k+=1
                    continue
                else:
                    continue
        except: #no salta ya 
            print("error fuck")#ya no sale
        # completar los valores de todos los dias guardados:
        for elemento in self.consumo_dias:
            try:
                elemento.completar_datos()
            except:
                print("Error completando consumo dias ")
    
    def calcular_estadisticas(self,ma_t,min_t,ma_p,min_p,ma_v,min_v,ma_pr,min_pr):
        self.diferencia_total = ma_t - min_t
        self.diferencia_valle = ma_v - min_v
        self.diferencia_punta = ma_p - min_p
        self.diferencia_precio = ma_pr - min_pr

def cargar_hoja_factura(SPREED_SHEET_ID, SHEET_NAME, DENOMINACION, HORA_INICIO_PUNTA, HORA_FIN_PUNTA):
    try:
        hoja = hoja_calculo_factura(SPREED_SHEET_ID, SHEET_NAME, DENOMINACION, HORA_INICIO_PUNTA, HORA_FIN_PUNTA)
        try:
            hoja.calcular_consumo_dias()
        except:
            print("Error consumo dias")
        hojas.append(hoja)
    except:
        print("Ha habido un ERROR")
        print("\n")
        print("Introduzca los datos de nuevo")

def ordenar(lista_dada,criterio):
    lista_des = []
    for dia in lista_dada:
        lista_des.append(dia)
    ordenada = []
    while(len(lista_des)>0):
        mayor = False
        igual = False
        for item in lista_des:
            for elemento in lista_des:
                if criterio == "total":
                    if item.consumo_total > elemento.consumo_total:
                        mayor = True
                        igual = False
                        continue
                    elif item.consumo_total == elemento.consumo_total:
                        igual = True
                        continue
                    else:
                        mayor = False
                        igual = False
                        break
                elif criterio == "valle":
                    if item.consumo_valle > elemento.consumo_valle:
                        mayor = True
                        igual = False
                        continue
                    elif item.consumo_valle == elemento.consumo_valle:
                        igual = True
                        continue
                    else:
                        mayor = False
                        igual = False
                        break
                elif criterio == "punta":
                    if item.consumo_punta > elemento.consumo_punta:
                        mayor = True
                        continue
                    elif item.consumo_punta == elemento.consumo_punta:
                        igual = True
                        continue
                    else:
                        mayor = False
                        igual = False
                        break
                elif criterio == "precio":
                    if item.precio_total > elemento.precio_total:
                        mayor = True
                        continue
                    elif item.precio_total == elemento.precio_total:
                        igual = True
                        continue
                    else:
                        mayor = False
                        igual = False
                        break
            if mayor:
                lista_des.remove(item)
                ordenada.append(item)
            elif igual:
                for element in lista_des:
                    ordenada.append(element)
                    lista_des.remove(element)
    return ordenada
#------------------------------------HOJA DE DATOS DE FACTURAS GUARDADAS------------------------------
class dato:
    def __init__(self,denominacion,ID,nombre,inicio,fin):
        self.denominacion = denominacion
        self.id = ID
        self.nombre = nombre
        self.inicio = inicio
        self.fin = fin

class hoja_datos:
    #gsheet con los datos para cargar todas las gsheets de facturas
    def __init__(self,ID,nombre):
        self.id = ID
        self.nombre = nombre
        self.registros = []
        self.datos = [] #contiene objetos dato que son los datos para cargar una hoja de calculo de facturas
    
    def cargar_datos(self):
        try:
            spreadsheet = SpreadsheetApp(JSON_FILE).open_by_id(self.id)
            sheet = spreadsheet.get_sheet_by_name(self.nombre)
            data_range = sheet.get_data_range()
            self.registros = data_range.get_values()
        except:
            print("No conecta con la sheet")
        for num in range(1,len(self.registros) ):
            deno = self.registros[num][0]
            id_d = self.registros[num][1]
            nom = self.registros[num][2]
            ini = self.registros[num][3]
            fin = self.registros[num][4]
            dat = dato(deno,id_d,nom,ini,fin)
            self.datos.append(dat)
    
def cargar_datos_facturas():
    #cargo al programa la gsheet de datos
    ID = str(input("Escriba la ID de la hoja que contiene los datos de las hojas factura: "))
    NOMBRE = str(input("Escriba el nombre de la hoja a cargar: "))
    hoja = hoja_datos(ID,NOMBRE)
    hoja.cargar_datos()
    return hoja
#------------------------------------------------------------------------------------------------------
#---------------------------------------INTERFAZ LINEA COMANDO-----------------------------------------
#------------------------------------------------------------------------------------------------------
facturas = cargar_datos_facturas()
#el usuario carga las hojas que quiera
cargar = True
while(cargar and len(hojas)!=len(facturas.datos)): #corre si se cargaron hojas de facturas correctamente, el usuario puede decir si quiere cargar más
    clear()
    if(len(hojas)):
        print(" Hojas ya cargadas:")
        for item in hojas:
            print("  {0}".format(item.denominacion))
    print(" >>------------------------<<")
    print(" Hojas en memoria:")
    for element in facturas.datos:#solo muestra las que no están ya cargadas en el programa
        subida = False
        for item in hojas:
            if element.denominacion == item.denominacion:
                subida = True
            else:
                continue
        if subida == False:
            print("  {0}".format(element.denominacion)) 
    print(" >>---------------<<")
    print(" Cual quiere cargar?")
    answer = input("  ")
    cargada = False #suponemos que la hoja que nos da el usuario no está cargada aún
    for elemento in hojas:
            if answer.lower() == elemento.denominacion.lower():
                print(" Ya esta cargada, no se ha vuelto a cargar.")
                print(" Escoja otra")
                cargada = True #si coincide con una cargada lo guardamos en esta variable
    existe = False
    if cargada == False:
        for item in facturas.datos:#buscamos si el nombre que introdujo existe    
            if answer.lower() == item.denominacion.lower():
                cargar_hoja_factura(item.id,item.nombre,item.denominacion,item.inicio,item.fin)
                clear()
                print(" >> Cargada")
                existe = True
        if existe == False:
            print(" No has introducido un nombre correcto")
    while(len(hojas)!=len(facturas.datos)): #pregunta si queremos cargar más hojas
        #print(" >>---------------------<<")
        print(" Quiere cargar mas? (Si/No)")
        res = input("  ")
        if res.lower() == "si":
            break
        elif res.lower() == "no":
            cargar= False
            clear()
            break
        else:
            print(" No has escrito una respuesta permitida")
#dependiendo del numero de hojas guardadas tendremos distintas opciones    
if len(hojas) == 0:
    print(" No hay hojas cargadas")
    exit()
elif len(hojas) == 1:
    dias = hojas[0].consumo_dias
    while(True):
        print(" >>--------------------------<<")
        print(" Todas las opciones son por dia")
        print(" El orden es siempre descendente")
        print("      >> OPCIONES <<")
        print("  1.- Consumo total orden")
        print("  2.- Precio total orden")
        print("  3.- Consumo punta orden")
        print("  4.- Consumo valle orden")
        print("  5.- Consumo valle y punta")
        print("  6.- Estadisticas")
        print("  7.- Consumo total cronologico")
        print("  8.- Cerrar\n")
        print(" Especifique el numero de la opcion que quiera:")
        opcion = int(input("  "))
        clear()
        # codigo selector
        ordenada_t = ordenar(dias,"total") 
        ordenada_pr = ordenar(dias,"precio")
        ordenada_p = ordenar(dias,"punta")
        ordenada_v = ordenar(dias,"valle")
        hojas[0].calcular_estadisticas(ordenada_t[0].consumo_total,ordenada_t[len(ordenada_t)-1].consumo_total,ordenada_p[0].consumo_punta
        ,ordenada_p[len(ordenada_t)-1].consumo_punta,ordenada_v[0].consumo_valle,ordenada_v[len(ordenada_t)-1].consumo_valle
        ,ordenada_pr[0].precio_total,ordenada_pr[len(ordenada_t)-1].precio_total)
        if opcion == 1: 
            for item in ordenada_t:
                print(" Dia: {0}, consumo total: {1}".format(item.fecha, item.consumo_total))
        elif opcion == 2:
            for item in ordenada_pr:
                print(" Dia: {0}, precio: {1}".format(item.fecha,item.precio_total))
        elif opcion == 3:
            for item in ordenada_p:
                print( "Dia: {0}, consumo punta: {1}".format(item.fecha, item.consumo_punta))
        elif opcion == 4:
            for item in ordenada_v:
                print(" Dia: {0}, consumo valle: {1}".format(item.fecha, item.consumo_valle))
        elif opcion == 5:
            for item in dias:
                print(" Dia: {0}, consumo valle: {1}, consumo punta: {2}".format(item.fecha, item.consumo_valle, item.consumo_punta))
        elif opcion == 6:
            print("Diferencias entre valor menor y mayor de:")
            print("Consumo total: {0}".format(hojas[0].diferencia_total))
            print("Consumo punta: {0}".format(hojas[0].diferencia_punta))
            print("Consumo valle: {0}".format(hojas[0].diferencia_valle))
            print("Precio consumo total: {0}".format(hojas[0].diferencia_precio))
        elif opcion == 7:
             for k in range(len(dias)-1,0,-1):
                print(" Dia: {0}, consumo total: {1}".format(dias[k].fecha, dias[k].consumo_total))
        elif opcion == 8:
            exit()
        else:
            print("Error!")
            print("No has escrito un numero valido")
else:
    dias = [] #contiene todos los dias de las hojas cargadas
    for item in hojas:
        for elemento in item.consumo_dias:
            dias.append(elemento)
    while(True):
        print(" >>--------------------------<<")
        print(" Todas las opciones son por dia")
        print(" El orden es siempre descendente")
        print("     >> OPCIONES <<")
        print(" 1.- Consumo total orden")
        print(" 2.- Precio total orden")
        print(" 3.- Consumo punta orden")
        print(" 4.- Consumo valle orden")
        print(" 5.- Estadisticas conjuntas")
        print(" 6.- Cerrar\n")
        print(" Especifique el numero de la opcion que quiera:")
        opcion = int(input("  "))
        clear()
        ordenada_t = ordenar(dias,"total") 
        ordenada_pr = ordenar(dias,"precio")
        ordenada_p = ordenar(dias,"punta")
        ordenada_v = ordenar(dias,"valle")
        if opcion == 1:
            for item in ordenada_t:
                print(" Dia: {0}, consumo total: {1}".format(item.fecha, item.consumo_total))
        elif opcion == 2: 
            for item in ordenada_pr:
                print(" Dia: {0}, precio: {1}".format(item.fecha,item.precio_total))
        elif opcion == 3: 
            for item in ordenada_p:
                print(" Dia: {0}, consumo punta: {1}".format(item.fecha, item.consumo_punta))
        elif opcion == 4:
            for item in ordenada_v:
                print(" Dia: {0}, consumo valle: {1}".format(item.fecha, item.consumo_valle))
        elif opcion == 5:
            dif_t = ordenada_t[0].consumo_total-ordenada_t[len(ordenada_t)-1].consumo_total
            dif_p = ordenada_p[0].consumo_punta-ordenada_p[len(ordenada_p)-1].consumo_punta
            dif_v = ordenada_v[0].consumo_valle-ordenada_v[len(ordenada_v)-1].consumo_valle
            dif_pr = ordenada_pr[0].precio_total-ordenada_pr[len(ordenada_pr)-1].precio_total
            print("Diferencias entre valor menor y mayor de:")
            print("Consumo total: {0}".format(dif_t))
            print("Consumo punta: {0}".format(dif_p))
            print("Consumo valle: {0}".format(dif_v))
            print("Precio consumo total: {0}".format(dif_pr))
        elif opcion == 6:
            exit()           
        else:
            print(" Error!")
            print(" No has escrito un numero valido")
