
from abc import ABC, abstractmethod
import logging

# ==========================================
# CONFIGURACION DEL ARCHIVO DE REGISTROS
# ==========================================

logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# ==========================================
# EXCEPCIONES PERSONALIZADAS
# ==========================================

class ErrorSistema(Exception):
    pass


class DatosInvalidos(ErrorSistema):
    pass


class ServicioNoDisponible(ErrorSistema):
    pass


class ReservaInvalida(ErrorSistema):
    pass


# ==========================================
# CLASE ABSTRACTA GENERAL
# ==========================================

class Entidad(ABC):

    def __init__(self, identificacion):
        if not identificacion:
            raise DatosInvalidos("La identificacion es obligatoria")
        self.identificacion = identificacion

    @abstractmethod
    def mostrar_informacion(self):
        pass


# ==========================================
# CLASE CLIENTE
# ==========================================

class Cliente(Entidad):

    def __init__(self, identificacion, nombre, correo):
        super().__init__(identificacion)

        if not nombre.strip():
            raise DatosInvalidos("El nombre no puede estar vacio")

        if "@" not in correo or "." not in correo:
            raise DatosInvalidos("El correo no es valido")

        self.__nombre = nombre
        self.__correo = correo

    def mostrar_informacion(self):
        return f"Cliente: {self.__nombre} - {self.__correo}"

    @property
    def nombre(self):
        return self.__nombre


# ==========================================
# CLASE ABSTRACTA SERVICIO
# ==========================================

class Servicio(Entidad):

    def __init__(self, identificacion, nombre, precio):
        super().__init__(identificacion)

        if precio <= 0:
            raise DatosInvalidos("El precio debe ser mayor que cero")

        self.nombre = nombre
        self.precio = precio
        self.disponible = True

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        pass

    @abstractmethod
    def describir(self):
        pass

    def mostrar_informacion(self):
        return self.describir()


# ==========================================
# SERVICIO 1: RESERVA DE SALAS
# ==========================================

class ReservaSala(Servicio):

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        if duracion <= 0:
            raise DatosInvalidos("La duracion debe ser positiva")

        subtotal = self.precio * duracion
        return subtotal + (subtotal * impuesto / 100) - (
            subtotal * descuento / 100
        )

    def describir(self):
        return f"Sala: {self.nombre}, precio por hora: ${self.precio}"


# ==========================================
# SERVICIO 2: ALQUILER DE EQUIPOS
# ==========================================

class AlquilerEquipo(Servicio):

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        if duracion <= 0:
            raise DatosInvalidos("La duracion debe ser positiva")

        subtotal = self.precio * duracion
        return subtotal + (subtotal * impuesto / 100) - (
            subtotal * descuento / 100
        )

    def describir(self):
        return f"Equipo: {self.nombre}, precio por dia: ${self.precio}"


# ==========================================
# SERVICIO 3: ASESORIAS
# ==========================================

class Asesoria(Servicio):

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        if duracion <= 0:
            raise DatosInvalidos("La duracion debe ser positiva")

        subtotal = self.precio * duracion
        return subtotal + (subtotal * impuesto / 100) - (
            subtotal * descuento / 100
        )

    def describir(self):
        return f"Asesoria: {self.nombre}, precio por hora: ${self.precio}"


# ==========================================
# CLASE RESERVA
# ==========================================

class Reserva(Entidad):

    def __init__(self, identificacion, cliente, servicio, duracion):
        super().__init__(identificacion)

        if not isinstance(cliente, Cliente):
            raise ReservaInvalida("Cliente incorrecto")

        if not isinstance(servicio, Servicio):
            raise ReservaInvalida("Servicio incorrecto")

        if duracion <= 0:
            raise ReservaInvalida("Duracion incorrecta")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"

    def confirmar(self):
        if self.estado != "Pendiente":
            raise ReservaInvalida("La reserva no puede confirmarse")

        if not self.servicio.disponible:
            raise ServicioNoDisponible("El servicio no esta disponible")

        self.estado = "Confirmada"
        logging.info("Reserva %s confirmada", self.identificacion)

    def cancelar(self):
        if self.estado == "Cancelada":
            raise ReservaInvalida("La reserva ya fue cancelada")

        self.estado = "Cancelada"
        logging.info("Reserva %s cancelada", self.identificacion)

    def procesar(self):
        if self.estado != "Confirmada":
            raise ReservaInvalida("Debe confirmar la reserva primero")

        costo = self.servicio.calcular_costo(self.duracion)
        logging.info("Reserva %s procesada", self.identificacion)
        return costo

    def mostrar_informacion(self):
        return (
            f"Reserva {self.identificacion}: "
            f"{self.cliente.nombre} - {self.servicio.nombre} "
            f"- Estado: {self.estado}"
        )


# ==========================================
# GESTOR GENERAL DEL SISTEMA
# ==========================================

class SistemaSoftwareFJ:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        self.clientes.append(cliente)
        logging.info("Cliente registrado: %s", cliente.nombre)

    def registrar_servicio(self, servicio):
        self.servicios.append(servicio)
        logging.info("Servicio registrado: %s", servicio.nombre)

    def crear_reserva(self, reserva):
        self.reservas.append(reserva)
        logging.info("Reserva creada: %s", reserva.identificacion)


# ==========================================
# PRUEBAS DEL SISTEMA: 10 OPERACIONES
# ==========================================

def ejecutar_pruebas():

    sistema = SistemaSoftwareFJ()

    print("\n===================================")
    print(" SISTEMA INTEGRAL SOFTWARE FJ")
    print("===================================\n")

    # OPERACION 1: Registro correcto
    try:
        cliente1 = Cliente("C001", "Maria", "maria@gmail.com")
        sistema.registrar_cliente(cliente1)
        print("1. Cliente registrado correctamente")
    except ErrorSistema as error:
        print("1. Error:", error)

    # OPERACION 2: Registro incorrecto
    try:
        cliente2 = Cliente("C002", "", "correo incorrecto")
        sistema.registrar_cliente(cliente2)
    except ErrorSistema as error:
        logging.error("Error registrando cliente: %s", error)
        print("2. Cliente rechazado:", error)

    # OPERACION 3: Otro cliente correcto
    try:
        cliente3 = Cliente("C003", "Carlos", "carlos@gmail.com")
        sistema.registrar_cliente(cliente3)
        print("3. Segundo cliente registrado")
    except ErrorSistema as error:
        print("3. Error:", error)

    # OPERACION 4: Crear servicio de sala
    try:
        sala = ReservaSala("S001", "Sala principal", 50000)
        sistema.registrar_servicio(sala)
        print("4. Servicio de sala creado")
    except ErrorSistema as error:
        print("4. Error:", error)

    # OPERACION 5: Crear servicio de equipos
    try:
        equipo = AlquilerEquipo("E001", "Proyector", 30000)
        sistema.registrar_servicio(equipo)
        print("5. Servicio de equipo creado")
    except ErrorSistema as error:
        print("5. Error:", error)

    # OPERACION 6: Crear asesoria
    try:
        asesoria = Asesoria("A001", "Asesoria informatica", 80000)
        sistema.registrar_servicio(asesoria)
        print("6. Asesoria creada")
    except ErrorSistema as error:
        print("6. Error:", error)

    # OPERACION 7: Servicio con precio invalido
    try:
        servicio_invalido = ReservaSala("S002", "Sala invalida", -100)
        sistema.registrar_servicio(servicio_invalido)
    except ErrorSistema as error:
        logging.error("Error creando servicio: %s", error)
        print("7. Servicio rechazado:", error)

    # OPERACION 8: Crear y confirmar reserva
    try:
        reserva1 = Reserva("R001", cliente1, sala, 2)
        sistema.crear_reserva(reserva1)
        reserva1.confirmar()
        print("8. Reserva confirmada correctamente")
    except ErrorSistema as error:
        print("8. Error:", error)

    # OPERACION 9: Procesar reserva y calcular costo
    try:
        costo = reserva1.servicio.calcular_costo(
            reserva1.duracion, 19, 10
        )
        print("9. Costo total con impuesto y descuento: $", costo)
    except ErrorSistema as error:
        print("9. Error:", error)

    # OPERACION 10: Reserva incorrecta
    try:
        reserva2 = Reserva("R002", cliente3, equipo, -2)
        sistema.crear_reserva(reserva2)
    except ErrorSistema as error:
        logging.error("Error creando reserva: %s", error)
        print("10. Reserva rechazada:", error)

    # TRY / EXCEPT / ELSE
    try:
        print("\nVerificando servicios...")
        cantidad = len(sistema.servicios)
    except Exception as error:
        logging.error("Error verificando servicios: %s", error)
    else:
        print("Servicios registrados:", cantidad)

    # TRY / EXCEPT / FINALLY
    try:
        print("\nConsultando clientes...")
        print("Total de clientes:", len(sistema.clientes))
    except Exception as error:
        logging.error("Error consultando clientes: %s", error)
    finally:
        print("Consulta finalizada.")

    # ENCadenamiento de excepciones
    try:
        try:
            raise ValueError("Dato original incorrecto")
        except ValueError as error:
            raise DatosInvalidos(
                "No se pudo procesar el dato"
            ) from error
    except DatosInvalidos as error:
        logging.exception("Excepcion encadenada")
        print("\nError controlado:", error)

    print("\n===================================")
    print(" SISTEMA FINALIZADO CORRECTAMENTE")
    print(" Los errores se guardaron en logs.txt")
    print("===================================")


if __name__ == "__main__":
    ejecutar_pruebas()


