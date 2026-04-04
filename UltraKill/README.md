# ULTRAKILL .bepis Decoder / Editor

**BLOOD IS FUEL.**
**BYTES ARE FUEL.**
**MY BRAIN HEMORRHAGE WAS ALSO FUEL.**

## ¿Qué es esto?

Un decoder/editor para archivos .bepis de ULTRAKILL.

Nació de un problema muy simple:
“Quería más armas.”

Terminó en:
parsing binario
offsets
estructuras tipo C#
y una ligera hemorragia cerebral

Ahora esa hemorragia es combustible reutilizable para cualquiera que quiera entender o modificar sus saves.

¿Qué hace?
Decodifica streams binarios tipo serialization
Exporta todo a .txt legible
Muestra offsets exactos (hex-level)
Permite editar valores directamente en el archivo

Esto no es un “trainer”.

Esto es cirugía.

# Uso
`python UltraKillDecoder.py <PATH de tu archivo .Bepis>`

Al ejecutarlo genera:
savefile.txt
Y luego entra en modo interactivo para editar valores directamente en el archivo binario.

Requisitos
python -m pip install rich

# ⚠️ DISCLAIMER
Este proyecto existe para:
aprendizaje
análisis
modding offline

No está hecho para:
arruinar experiencias de otros
exploits en entornos online
uso malicioso
No está afiliado con ULTRAKILL ni sus desarrolladores.

## Origen

Durante el desarrollo de esta herramienta:
Perdí neuronas
Gané offsets
Entendí cosas que probablemente no debía

Pero ahora:
La sangre derramada alimenta a otros.

--- 

### Nota técnica

El formato .bepis parece derivar de:

serialización binaria estilo C#
estructuras con metadata + referencias

El script:
reconstruye clases
interpreta tipos primitivos
permite modificación directa vía offsets

Posibles mejoras
Soporte completo de objetos complejos
Sistema de backup automático antes de editar
Interfaz más amigable
Detección de tipos más robusta

Autor
Aztharot
https://github.com/Aztharot-RO0t3d

Licencia
GPLv3 —
Haz lo que quieras con esto menos venderlo no seai rata.

Solo recuerda:
Si rompes tu save… probablemente de eso murio la humanidad en ultrakill.
