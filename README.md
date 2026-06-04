# DOS-CDP-FLOODING

---

> **Autor:** Randy Nin
> **Laboratorio de Seguridad de Redes | GNS3**

Script de Python que realiza un ataque de Denegación de Servicio (DoS) sobre dispositivos Cisco mediante inundación del protocolo CDP. Genera y envía frames CDP falsificados de forma masiva hacia la dirección multicast `01:00:0c:cc:cc:cc`, saturando la tabla de vecinos del dispositivo víctima y llevando su CPU al 100%.

---

## Contenido del repositorio

```
DOS-CDP-FLOODING/
├── cdp-flooding.py
├── Documentación Tecnica Profesional DOS-CDP FLOODING (Randy Nin -- 2025-0660).pdf
└── README.md
```

---

## Documentación técnica

La documentación técnica completa de este laboratorio está disponible en:

**[Documentación Tecnica Profesional DOS-CDP FLOODING (Randy Nin -- 2025-0660).pdf](./Documentación Tecnica Profesional DOS-CDP FLOODING (Randy Nin -- 2025-0660).pdf)**

Incluye:

- Contexto técnico del protocolo CDP y su vulnerabilidad
- Objetivos del laboratorio y del script
- Topología y entorno de laboratorio
- Requisitos, dependencias y parámetros de ejecución
- Análisis técnico completo del script
- Evidencia del ataque con capturas de pantalla
- Contramedidas y verificación post-mitigación

---

## Requisitos

**Sistema:** ParrotSec OS, Kali Linux o cualquier distribución Linux con soporte para envío de paquetes raw.

**Python:** 3.x con permisos de superusuario (`sudo`).

**Dependencias externas:**

| Librería | Instalación |
|:---|:---|
| `scapy` | `pip install scapy` |
| `pwntools` | `pip install pwntools` |

**Instalación rápida:**

```bash
pip install scapy pwntools
```

---

## Uso

```bash
sudo python3 cdp-flooding.py -i <interfaz>
```

**Parámetros:**

| Flag | Descripción | Default |
|:---|:---|:---:|
| `-i` / `--interface` | Interfaz de red desde la que se inyectan los frames | `ens4` |

**Ejemplo:**

```bash
sudo python3 cdp-flooding.py -i ens4
```

Presionar `Ctrl+C` para detener el ataque de forma limpia.

---

## Cómo funciona

Por cada iteración, el script genera un frame CDP con identidad completamente aleatoria:

- **Device ID:** prefijo `RANDYN` + 8 caracteres alfanuméricos aleatorios
- **MAC origen:** rango `02:00:00:XX:XX:XX` con los últimos 3 octetos aleatorios
- **Port ID:** formato `Fas X/X` aleatorio

El frame se construye con la siguiente estructura:

```
Ethernet (dst=01:00:0c:cc:cc:cc)
  └── LLC / SNAP
        └── CDP Raw (header v2 + TTL 180s + checksum calculado + TLVs)
```

El checksum se calcula manualmente mediante complemento a uno antes de cada envío, garantizando que el router lo acepte como válido y lo incorpore a su tabla de vecinos.

---

## Entorno de laboratorio

| Dispositivo | Rol | Interfaz | Sistema |
|:---|:---|:---|:---|
| R1 | Víctima | Fa 1/15 | Cisco 3725 / IOS 124-15.T14 |
| Parrot-1 | Atacante | ens4 | ParrotSec OS |

> CDP opera a Capa 2. No se requiere configuración de direccionamiento IP.

---

## Impacto observado

- Tabla de vecinos CDP saturada con **miles** de entradas falsas (`RANDYN...`)
- CPU del router elevado a `0%/100%` en varios segundos (modo interrupciones)
- Proceso `CDP Protocol` como el de mayor consumo en `show processes cpu sorted`

---

## Mitigación

**Deshabilitar CDP globalmente:**

```
R1(config)# no cdp run
```

**Deshabilitar CDP por interfaz:**

```
R1(config)# interface FastEthernet 1/15
R1(config-if)# no cdp enable
```

---

## Video demostrativo

*(pendiente - enlace de YouTube)*

---

## Disclaimer

Este script fue desarrollado con fines exclusivamente académicos y educativos. Su uso está permitido únicamente en entornos propios o autorizados como GNS3, EVE-NG, PNETLAB o laboratorios internos de prueba. El uso en redes de terceros sin autorización expresa constituye una violación legal.

---

*Randy Nin / Matrícula 2025-0660*

---

