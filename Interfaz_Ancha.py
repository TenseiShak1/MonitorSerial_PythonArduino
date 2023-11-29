import tkinter as tk
from tkinter import ttk, scrolledtext
from serial.tools import list_ports
import serial
import threading

class ArduinoInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Arduino Interface")
        self.root.geometry("680x520")  # Ancho x Alto

        self.arduino = None
        self.max_log_lines = 100  # Número máximo de líneas en el área de texto

        self.create_widgets()
        self.manejar_lectura_datos()

    def create_widgets(self):
        self.command_entry = tk.Entry(self.root, width=40, state=tk.DISABLED)
        self.command_entry.grid(row=0, column=0, padx=10, pady=10)

        self.send_button = tk.Button(self.root, text="Enviar Comando", command=self.send_command, state=tk.DISABLED)
        self.send_button.grid(row=0, column=1, padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(self.root, width=80, height=15)
        self.log_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.port_list_label = tk.Label(self.root, text="Puertos seriales disponibles:")
        self.port_list_label.grid(row=2, column=0, columnspan=2, pady=5)

        self.port_var = tk.StringVar()
        self.port_combobox = ttk.Combobox(self.root, textvariable=self.port_var, state="readonly")
        self.port_combobox.grid(row=3, column=0, columnspan=2, pady=5)

        self.refresh_button = tk.Button(self.root, text="Actualizar Puertos", command=self.update_serial_ports)
        self.refresh_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.connect_arduino_button = tk.Button(self.root, text="Conectar a Arduino", command=self.connect_arduino)
        self.connect_arduino_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Vincular la tecla Enter a la función send_command
        self.command_entry.bind("<Return>", lambda event: self.send_command())

        # Actualizar periódicamente la interfaz
        self.root.after(100, self.update_interface)

        # Botón para cerrar la aplicación
        self.close_button = tk.Button(self.root, text="Cerrar", command=self.close_application)
        self.close_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Llenar la lista de puertos seriales disponibles
        self.update_serial_ports()

    def update_serial_ports(self):
        ports = [port.device for port in list_ports.comports()]
        self.port_combobox["values"] = ports
        if ports:
            self.port_combobox.current(0)

    def conectar_arduino(self, puerto, velocidad):
        try:
            conexion = serial.Serial(puerto, velocidad, timeout=1)
            return conexion
        except serial.SerialException as e:
            self.log_text.insert(tk.END, f"Error al conectar a {puerto}: {e}\n")
            return None

    def connect_arduino(self):
        port_arduino = self.port_var.get()
        velocidad_arduino = 9600  # Ajusta a la velocidad de baudios de tu Arduino

        self.arduino = self.conectar_arduino(port_arduino, velocidad_arduino)

        if self.arduino is not None:
            self.log_text.insert(tk.END, f"Conectado a {port_arduino}\n")
            self.port_combobox["state"] = tk.DISABLED
            self.refresh_button["state"] = tk.DISABLED
            self.connect_arduino_button["state"] = tk.DISABLED
            self.command_entry["state"] = tk.NORMAL
            self.send_button["state"] = tk.NORMAL

    def send_command(self):
        if self.arduino is not None:
            comando_a_enviar = self.command_entry.get()
            self.enviar_comando(comando_a_enviar)
            self.log_text.insert(tk.END, f"Comando enviado: {comando_a_enviar}\n")
            self.command_entry.delete(0, tk.END)

    def enviar_comando(self, comando):
        try:
            self.arduino.write(comando.encode("utf-8"))
        except serial.SerialException as e:
            self.log_text.insert(tk.END, f"Error al enviar comando: {e}\n")

    def leer_datos(self):
        while True:
            try:
                if self.arduino and self.arduino.in_waiting > 0:
                    datos = self.arduino.readline().decode("utf-8").strip()
                    self.log_text.insert(tk.END, f"{datos}\n")
                    self.log_text.yview(tk.END)

                    lines = self.log_text.get("1.0", tk.END).count("\n")
                    if lines > self.max_log_lines:
                        self.log_text.delete("1.0", f"{lines - self.max_log_lines}.0")
            except serial.SerialException as e:
                self.log_text.insert(tk.END, f"Error al leer datos: {e}\n")
                break

    def manejar_lectura_datos(self):
        thread_lectura = threading.Thread(target=self.leer_datos, daemon=True)
        thread_lectura.start()

    def update_interface(self):
        # Tu código existente aquí

        # Llamar a self.update_interface nuevamente después de un tiempo
        self.root.after(100, self.update_interface)

    def close_application(self):
        if self.arduino:
            self.arduino.close()  # Cerrar la conexión serial si está abierta
        self.root.destroy()  # Cerrar la aplicación

if __name__ == "__main__":
    root = tk.Tk()
    app = ArduinoInterface(root)
    root.mainloop()
