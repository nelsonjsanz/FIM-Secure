# 🛡️ FIM-Secure: Monitor de Integridad de Archivos

**Unidad Curricular:** Programación Orientada a la Ingeniería en Ciberseguridad  
**Institución:** Universidad Nacional de las Ciencias Dr. Humberto Fernández Morán  

## 👥 Equipo de Trabajo (Metodología SCRUM)
* **Nelson Sánchez (PO / Dev 2):** Product Owner & Especialista en Python / Integración.
* **[Andrea Pernil] (Scrum Master):** Facilitador SCRUM & Gestión de Tablero.
* **[Pedro Diaz] (Dev 1):** Especialista en Bajo Nivel (Lenguaje C - Win32 CryptoAPI).

---

## 🚀 Descripción del Proyecto
FIM-Secure es una herramienta defensiva desarrollada en arquitectura híbrida C/Python para Windows. 
El núcleo compilado en **C** calcula la firma criptográfica **SHA-256** de archivos críticos utilizando la API nativa `wincrypt.h`, mientras que el orquestador en **Python** almacena la línea base, ejecuta auditorías y emite alertas ante modificaciones no autorizadas.

---

## 🛠️ Compilación y Ejecución en Windows

### 1. Requisitos Previos
* Compilador GCC (MinGW-w64) o MSVC configurado en el PATH.
* Python 3.x instalado.

### 2. Compilar el Motor en C
Ejecutar el script automático en CMD o PowerShell:
```cmd
build.bat