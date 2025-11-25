
	#Pedir al usuario que ingrese su nombre de usuario y contraseña
username = input("Ingrese su usuario: ")
password = input("Ingrese su contraseña: ") 

	#Verificamos que el usuario y la conntraseña esten correctos 
if username in usuarios and usuarios[username] == paseword:
		print("Bienvenido")
else:
		print("El usuario o contraseña incorrectos")

