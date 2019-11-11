Programa de python que analiza la curva horaria de la factura de la luz de Naturgy, en formato google sheets.
Para utilizarlo es necesario tener el modulo de python sheetfu instalado(https://github.com/socialpoint-labs/sheetfu).
El programa se conecta con Google Drive a traves de la Api de Google, por lo que hay que activarla para la cuenta deseada, conseguir el 
archivo .json, que pide el programa.
Los datos (ID Y nombre), de las google sheets que se quieran analizar deben estar guardados en otra google sheet con los datos ordenados:
denominación(nombre de la hoja en la que están los datos), ID, nombre, hora inicio periodo valle, hora fin periodo valle.
Para que las hojas trabajen con la API tienen que compartirse con el correo que proporciona la API(gserviceaccount).
