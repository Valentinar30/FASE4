
# ============================================================
# PROYECTO: SOFTWARE FJ
# Sistema Integral de Gestion de Clientes, Servicios y Reservas
# Curso: Programacion - UNAD
# ============================================================

from abc import ABC, abstractmethod
from datetime import datetime
import logging
import math


# ============================================================
# 1. CONFIGURACION DEL SISTEMA DE REGISTROS
# ============================================================

logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger("SoftwareFJ")


# ============================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ============================================================

class ErrorSistema(Exception):
    """Excepcion general del sistema."""
    pass


class DatosInvalidos(ErrorSistema):
    """Se genera cuando los datos ingresados no son validos."""
    pass


class ServicioNoDisponible(ErrorSistema):
    """Se genera cuando un servicio no esta disponible."""
    pass


class ReservaInvalida(ErrorSistema):
    """Se genera cuando una reserva no cumple las condiciones."""
    pass


class OperacionNoPermitida(ErrorSistema):
    """Se genera cuando una operacion no esta permitida."""
    pass


# ============================================================
# 3. CLASE ABSTRACTA GENERAL
# ============================================================

class Entidad(ABC):

    def __init__(self, identificacion):
        identificacion = str(identificacion).strip()

        if not identificacion:
            raise DatosInvalidos(
                "La identificacion no puede estar vacia."
            )

        self._identificacion = identificacion

    @property
    def identificacion(self):
        return self._identificacion

    @abstractmethod
    def mostrar_informacion(self):
        pass


# ============================================================
# 4. CLASE CLIENTE
# ============================================================

class Cliente(Entidad):

    def __init__(self, identificacion, nombre, correo, telefono):
        super().__init__(identificacion)

        nombre = str(nombre).strip()
        correo = str(correo).strip()
        telefono = str(telefono).strip()

        if len(nombre) < 2:
            raise DatosInvalidos(
                "El nombre debe contener al menos dos caracteres."
            )

        if "@" not in correo or "." not in correo.split("@")[-1]:
            raise DatosInvalidos("El correo electronico no es valido.")

        if not telefono.isdigit() or len(telefono) < 7:
            raise DatosInvalidos("El telefono no es valido.")

        # Encapsulacion: atributos privados.
        self.__nombre = nombre
        self.__correo = correo
        self.__telefono = telefono

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    def mostrar_informacion(self):
        return (
            f"ID: {self.identificacion} | "
            f"Nombre: {self.__nombre} | "
            f"Correo: {self.__correo} | "
            f"Telefono: {self.__telefono}"
        )


# ============================================================
# 5. CLASE ABSTRACTA SERVICIO
# ============================================================

class Servicio(Entidad):

    def __init__(self, identificacion, nombre, precio):
        super().__init__(identificacion)

        nombre = str(nombre).strip()

        if not nombre:
            raise DatosInvalidos("El nombre del servicio es obligatorio.")

        self._nombre = nombre
        self._precio = self._validar_numero(precio, "precio")
        self._disponible = True

    @staticmethod
    def _validar_numero(valor, nombre):
        try:
            numero = float(valor)

            if not math.isfinite(numero) or numero <= 0:
                raise DatosInvalidos(
                    f"El {nombre} debe ser un numero positivo y finito."
                )

            return numero

        except (TypeError, ValueError) as error:
            raise DatosInvalidos(
                f"El {nombre} debe ser numerico."
            ) from error

    @property
    def nombre(self):
        return self._nombre

    @property
    def precio(self):
        return self._precio

    @property
    def disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        if not isinstance(estado, bool):
            raise DatosInvalidos(
                "La disponibilidad debe ser verdadera o falsa."
            )

        self._disponible = estado

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        duracion = self._validar_numero(duracion, "duracion")

        try:
            impuesto = float(impuesto)
            descuento = float(descuento)

            if not math.isfinite(impuesto) or not 0 <= impuesto <= 100:
                raise DatosInvalidos(
                    "El impuesto debe estar entre 0 y 100."
                )

            if not math.isfinite(descuento) or not 0 <= descuento <= 100:
                raise DatosInvalidos(
                    "El descuento debe estar entre 0 y 100."
                )

            subtotal = self.precio * duracion
            total = subtotal + subtotal * impuesto / 100
            total = total - subtotal * descuento / 100

            if not math.isfinite(total) or total < 0:
                raise DatosInvalidos("El calculo del costo es inconsistente.")

            return round(total, 2)

        except (TypeError, ValueError) as error:
            raise DatosInvalidos(
                "Los valores del calculo deben ser numericos."
            ) from error

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    @abstractmethod
    def describir(self):
        pass

    def mostrar_informacion(self):
        return self.describir()


# ============================================================
# 6. SERVICIO ESPECIALIZADO: RESERVA DE SALAS
# ============================================================

class ReservaSala(Servicio):

    def validar_parametros(self, duracion):
        duracion = self._validar_numero(duracion, "horas")

        if duracion > 12:
            raise DatosInvalidos(
                "La reserva de una sala no puede superar 12 horas."
            )

        return duracion

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        duracion = self.validar_parametros(duracion)
        return super().calcular_costo(duracion, impuesto, descuento)

    def describir(self):
        return (
            f"Sala: {self.nombre} | "
            f"Precio por hora: ${self.precio:,.2f}"
        )


# ============================================================
# 7. SERVICIO ESPECIALIZADO: ALQUILER DE EQUIPOS
# ============================================================

class AlquilerEquipo(Servicio):

    def validar_parametros(self, duracion):
        duracion = self._validar_numero(duracion, "dias")

        if duracion > 30:
            raise DatosInvalidos(
                "El alquiler no puede superar 30 dias."
            )

        return duracion

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        duracion = self.validar_parametros(duracion)
        return super().calcular_costo(duracion, impuesto, descuento)

    def describir(self):
        return (
            f"Equipo: {self.nombre} | "
            f"Precio por dia: ${self.precio:,.2f}"
        )


# ============================================================
# 8. SERVICIO ESPECIALIZADO: ASESORIAS
# ============================================================

class Asesoria(Servicio):

    def validar_parametros(self, duracion):
        duracion = self._validar_numero(duracion, "horas")

        if duracion > 8:
            raise DatosInvalidos(
                "La asesoria no puede superar 8 horas."
            )

        return duracion

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        duracion = self.validar_parametros(duracion)
        return super().calcular_costo(duracion, impuesto, descuento)

    def describir(self):
        return (
            f"Asesoria: {self.nombre} | "
            f"Precio por hora: ${self.precio:,.2f}"
        )


# ============================================================
# 9. CLASE RESERVA
# ============================================================

class Reserva(Entidad):

    def __init__(self, identificacion, cliente, servicio, duracion):
        super().__init__(identificacion)

        if not isinstance(cliente, Cliente):
            raise ReservaInvalida("Debe seleccionar un cliente valido.")

        if not isinstance(servicio, Servicio):
            raise ReservaInvalida("Debe seleccionar un servicio valido.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = servicio.validar_parametros(duracion)
        self.estado = "Pendiente"
        self.fecha = datetime.now()
        self.costo = None

        logger.info("Reserva %s creada.", self.identificacion)

    def confirmar(self):
        if self.estado != "Pendiente":
            raise ReservaInvalida(
                "Solo se pueden confirmar reservas pendientes."
            )

        if not self.servicio.disponible:
            raise ServicioNoDisponible(
                "El servicio seleccionado no esta disponible."
            )

        self.servicio.cambiar_disponibilidad(False)
        self.estado = "Confirmada"

        logger.info("Reserva %s confirmada.", self.identificacion)

    def cancelar(self):
        if self.estado not in ("Pendiente", "Confirmada"):
            raise OperacionNoPermitida(
                "No se puede cancelar una reserva procesada o cancelada."
            )

        if self.estado == "Confirmada":
            self.servicio.cambiar_disponibilidad(True)

        self.estado = "Cancelada"
        logger.info("Reserva %s cancelada.", self.identificacion)

    def procesar(self, impuesto=0, descuento=0):
        if self.estado != "Confirmada":
            raise ReservaInvalida(
                "La reserva debe estar confirmada antes de procesarse."
            )

        self.costo = self.servicio.calcular_costo(
            self.duracion, impuesto, descuento
        )

        self.estado = "Procesada"

        logger.info(
            "Reserva %s procesada. Total: %.2f",
            self.identificacion,
            self.costo
        )

        return self.costo

    def mostrar_informacion(self):
        return (
            f"Reserva: {self.identificacion} | "
            f"Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | "
            f"Duracion: {self.duracion} | "
            f"Estado: {self.estado}"
        )


# ============================================================
# 10. GESTOR GENERAL DEL SISTEMA
# ============================================================

class SistemaSoftwareFJ:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidos("El objeto no es un cliente valido.")

        if any(c.identificacion == cliente.identificacion
               for c in self.clientes):
            raise DatosInvalidos("El cliente ya se encuentra registrado.")

        self.clientes.append(cliente)
        logger.info("Cliente registrado: %s", cliente.nombre)

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatosInvalidos("El objeto no es un servicio valido.")

        if any(s.identificacion == servicio.identificacion
               for s in self.servicios):
            raise DatosInvalidos("El servicio ya se encuentra registrado.")

        self.servicios.append(servicio)
        logger.info("Servicio registrado: %s", servicio.nombre)

    def crear_reserva(self, reserva):
        if not isinstance(reserva, Reserva):
            raise ReservaInvalida("El objeto de reserva no es valido.")

        if any(r.identificacion == reserva.identificacion
               for r in self.reservas):
            raise ReservaInvalida("La reserva ya existe.")

        self.reservas.append(reserva)
        logger.info("Reserva agregada: %s", reserva.identificacion)

    def mostrar_resumen(self):
        print("\n========== RESUMEN DEL SISTEMA ==========")
        print("Clientes registrados:", len(self.clientes))
        print("Servicios registrados:", len(self.servicios))
        print("Reservas registradas:", len(self.reservas))
        print("=========================================")


# ============================================================
# 11. FUNCION PARA REGISTRAR Y CONTROLAR ERRORES
# ============================================================

def ejecutar_operacion(numero, descripcion, funcion):

    print(f"\nOPERACION {numero}: {descripcion}")

    try:
        funcion()

    except ErrorSistema as error:
        logger.error(
            "Operacion %s - %s: %s",
            numero, descripcion, error
        )
        print("ERROR CONTROLADO:", error)

    except Exception as error:
        logger.exception(
            "Error inesperado en operacion %s", numero
        )
        print("ERROR INESPERADO:", error)

    else:
        print("Operacion realizada correctamente.")

    finally:
        print("Verificacion de operacion finalizada.")


# ============================================================
# 12. EJECUCION Y PRUEBAS DEL SISTEMA
# ============================================================

def ejecutar_pruebas():

    sistema = SistemaSoftwareFJ()

    print("\n")
    print("==============================================")
    print("       SISTEMA INTEGRAL SOFTWARE FJ")
    print("  Gestion de Clientes, Servicios y Reservas")
    print("==============================================")

    # OPERACION 1: Registro de cliente valido.

    cliente1 = None

    def prueba1():
        nonlocal cliente1
        cliente1 = Cliente(
            "C001", "Valentina", "valentina@gmail.com", "3001234567"
        )
        sistema.registrar_cliente(cliente1)
        print(cliente1.mostrar_informacion())

    ejecutar_operacion(1, "Registro de cliente valido", prueba1)

    # OPERACION 2: Registro de cliente invalido.

    def prueba2():
        cliente_invalido = Cliente(
            "C002", "", "correo incorrecto", "123"
        )
        sistema.registrar_cliente(cliente_invalido)

    ejecutar_operacion(2, "Registro de cliente invalido", prueba2)

    # OPERACION 3: Registro de un segundo cliente.

    cliente2 = None

    def prueba3():
        nonlocal cliente2
        cliente2 = Cliente(
            "C003", "Carlos", "carlos@gmail.com", "3109876543"
        )
        sistema.registrar_cliente(cliente2)
        print(cliente2.mostrar_informacion())

    ejecutar_operacion(3, "Registro de segundo cliente", prueba3)

    # OPERACION 4: Creacion de una sala.

    sala = None

    def prueba4():
        nonlocal sala
        sala = ReservaSala("S001", "Sala principal", 50000)
        sistema.registrar_servicio(sala)
        print(sala.describir())

    ejecutar_operacion(4, "Creacion de servicio de sala", prueba4)

    # OPERACION 5: Creacion de alquiler de equipos.

    equipo = None

    def prueba5():
        nonlocal equipo
        equipo = AlquilerEquipo("E001", "Proyector", 30000)
        sistema.registrar_servicio(equipo)
        print(equipo.describir())

    ejecutar_operacion(5, "Creacion de servicio de equipos", prueba5)

    # OPERACION 6: Creacion de asesoria.

    asesoria = None

    def prueba6():
        nonlocal asesoria
        asesoria = Asesoria("A001", "Asesoria informatica", 80000)
        sistema.registrar_servicio(asesoria)
        print(asesoria.describir())

    ejecutar_operacion(6, "Creacion de asesoria especializada", prueba6)

    # OPERACION 7: Creacion de servicio con precio incorrecto.

    def prueba7():
        servicio_invalido = ReservaSala("S002", "Sala invalida", -100)
        sistema.registrar_servicio(servicio_invalido)

    ejecutar_operacion(7, "Creacion de servicio con precio invalido", prueba7)

    # OPERACION 8: Creacion y confirmacion de reserva.

    reserva1 = None

    def prueba8():
        nonlocal reserva1
        reserva1 = Reserva("R001", cliente1, sala, 2)
        sistema.crear_reserva(reserva1)
        reserva1.confirmar()
        print(reserva1.mostrar_informacion())

    ejecutar_operacion(8, "Creacion y confirmacion de reserva", prueba8)

    # OPERACION 9: Procesamiento y calculo de costo.

    def prueba9():
        costo = reserva1.procesar(impuesto=19, descuento=10)
        print(f"Costo final de la reserva: ${costo:,.2f}")

    ejecutar_operacion(9, "Procesamiento de reserva y calculo", prueba9)

    # OPERACION 10: Reserva con duracion incorrecta.

    def prueba10():
        reserva_invalida = Reserva("R002", cliente2, asesoria, 20)
        sistema.crear_reserva(reserva_invalida)

    ejecutar_operacion(10, "Intento de reserva con duracion incorrecta", prueba10)

    # OPERACION 11: Intento de confirmar un servicio ocupado.

    def prueba11():
        reserva2 = Reserva("R003", cliente2, sala, 1)
        sistema.crear_reserva(reserva2)
        reserva2.confirmar()

    ejecutar_operacion(11, "Intento de reservar servicio no disponible", prueba11)

    # OPERACION 12: Cancelacion de reserva pendiente.

    def prueba12():
        reserva3 = Reserva("R004", cliente2, equipo, 2)
        sistema.crear_reserva(reserva3)
        reserva3.cancelar()
        print(reserva3.mostrar_informacion())

    ejecutar_operacion(12, "Cancelacion de reserva", prueba12)

    # OPERACION 13: Calculo con parametros opcionales.

    def prueba13():
        costo = equipo.calcular_costo(
            3, impuesto=19, descuento=5
        )
        print(f"Costo del alquiler con ajustes: ${costo:,.2f}")

    ejecutar_operacion(13, "Calculo con impuesto y descuento", prueba13)

    # OPERACION 14: Ejemplo de try/except/else/finally.

    print("\nOPERACION 14: Estructura try/except/else/finally")

    try:
        total_clientes = len(sistema.clientes)
        print("Cantidad de clientes:", total_clientes)

    except Exception as error:
        logger.exception("Error consultando los clientes.")
        print("Error de consulta:", error)

    else:
        print("La consulta se realizo sin errores.")

    finally:
        print("Consulta finalizada.")

    # OPERACION 15: Encadenamiento de excepciones.

    print("\nOPERACION 15: Encadenamiento de excepciones")

    try:
        try:
            int("dato incorrecto")
        except ValueError as error:
            raise DatosInvalidos(
                "No fue posible convertir el dato."
            ) from error

    except DatosInvalidos as error:
        logger.exception("Excepcion encadenada.")
        print("Error controlado:", error)

    # RESUMEN FINAL.

    sistema.mostrar_resumen()

    print("\n==============================================")
    print("       SISTEMA FINALIZADO CORRECTAMENTE")
    print("       Revise el archivo logs.txt")
    print("==============================================\n")

    logger.info("Ejecucion del sistema finalizada.")


# ============================================================
# 13. PUNTO DE ENTRADA DEL PROGRAMA
# ============================================================

if __name__ == "__main__":

    try:
        ejecutar_pruebas()

    except Exception:
        logger.exception("Error critico durante la ejecucion.")
        print("Se presento un error general. Revise logs.txt.")

    finally:
        print("Software FJ: proceso de ejecucion terminado.")
