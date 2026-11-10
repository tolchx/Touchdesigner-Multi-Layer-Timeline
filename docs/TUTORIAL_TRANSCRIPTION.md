# Transcripción y Estudio Técnico del Tutorial: TouchDesigner Multi-Layer Timeline (TD-MTL)

- **Video:** [TouchDesigner Multi-Layer Timeline en YouTube](https://www.youtube.com/watch?v=GxShURxpJXk)
- **Autor / Creador:** Tim Franklin
- **Proyecto asociado:** [franklin113/Touchdesigner-Multi-Layer-Timeline](https://github.com/franklin113/Touchdesigner-Multi-Layer-Timeline)

---

## 1. Resumen Ejecutivo y Arquitectura

Tim Franklin presenta el diseño interno de **TD-MTL**, una línea de tiempo multi-capa acelerada por GPU para TouchDesigner, diseñada para secuenciar medios, comandos OSC/TCP, presets tox y transiciones.

### Puntos Arquitectónicos Clave revelados en el video:
1. **Renderizado en GPU por Instancing 3D:**
   - La línea de tiempo no está hecha con decenas de nodos pesados de panel 2D (COMPs). Todo el canvas, pistas y cues se dibujan en un entorno 3D mediante **Geometry Instancing**.
   - Cada cue es una instancia que lee sus propiedades desde tablas/CHOPs de instancias (`instance id`).
2. **Sistema de Doble Cámara:**
   - **Main Camera:** Controla el canvas de tiempo y las cues (hace zoom horizontal y scroll temporal siguiendo al playhead).
   - **Settings / Layers Camera:** Renderiza la barra fija de capas/labels a la izquierda con una cámara ortográfica independiente, evitando que el zoom horizontal distorsione los nombres de las capas, pero sincronizando el scroll vertical.
3. **Outlines y Fades procedurales vía GLSL Shaders:**
   - Las selecciones (borde blanco para selección activa, amarillo para selecciones múltiples anteriores) y contornos se generan en el pixel shader sin texturas.
   - Los tweens de entrada y salida (*fade in / fade out*) usan una geometría lineal instanciada de 4 vértices reubicada dinámicamente en el **Vertex Shader** usando los atributos personalizados de la página `Instance 3`.
4. **Interacción con RenderPick:**
   - El arrastre, selección y redimensionamiento de cues utiliza `RenderPick` basado en `instance id`, evitando mapeos manuales de coordenadas UV.
5. **Motor de Tiempo (Timer CHOP / Segment DAT):**
   - El componente `Time` mapea cada cue a filas de un `Segment DAT` para que el temporizador maestro (`Timer CHOP`) emita pulsos de precarga (`preload`), disparo (`trigger`) y posiciones normalizadas de reproducción.

---

## 2. Transcripción y Desglose por Marcas de Tiempo

### [00:00 - 01:00] Presentación, Selección y Multi-selección
> **Original (EN):**  
> *"Okay so I've been working on this for you know the past few days and with everything that's going on I have to kind of move on so I just wanted to do kind of a quick video and I was just gonna post it on github... the general idea is we have multi-layer timeline and we have cues that we can place down. You can select it, there's an outline, you can do multi select... the most recent one you select is white, previous ones are yellow and then you can drag them all and do multi select which is pretty cool."*

* **Explicación técnica:**  
  La interfaz adopta la convención visual de TouchDesigner:
  - Cue activa: contorno blanco.
  - Cues seleccionadas adicionales: contorno amarillo.
  - Mover una cue seleccionada traslada en bloque a todas las demás seleccionadas manteniendo sus distancias relativas.

---

### [01:00 - 02:00] Navegación: Zoom, Scroll y Playhead
> **Original (EN):**  
> *"One of the things I was pretty happy with was the zooming... you can actually use the keyboard so it's ctrl + -, so you can zoom in with a keyboard. You can scroll, so if you turn off 'camera follows playhead' you can scroll through by holding shift and the up and down mouse wheel... but I like the camera follows playhead idea."*

* **Explicación técnica:**  
  - Zoom mediante atajos de teclado o rueda con modificadores.
  - Modo `Camera follows playhead`: la cámara principal reubica automáticamente su eje X para mantener el cabezal de reproducción siempre visible durante el transporte.
  - Al desactivarlo, se permite navegación libre horizontal y vertical (`Shift + Rueda del ratón`).

---

### [02:00 - 03:08] Edición de Parámetros de la Cue
> **Original (EN):**  
> *"Whenever you click on a cue it changes this here so you can make some changes... this cue here we can change the in-and-out duration, so there's a fade in and you can change that duration. The idea was that you would send this data to your play engine... you set your cue lengths and then you set your start time... so when you move this around you're changing the start time here... you just set the layer and it will move it up and down."*

* **Explicación técnica:**  
  Al hacer clic en una cue, el panel inspector carga los parámetros:
  - `In/Out Duration` (Fades de entrada y salida visualizados como rampas).
  - `Cue Length` (duración del bloque).
  - `Start Time` (instante de inicio en la línea temporal).
  - `Layer` (índice de la pista vertical a la que pertenece).

---

### [03:08 - 05:00] Estructura Interna: Cámaras y Capas 3D
> **Original (EN):**  
> *"Internally how it's built: we have our time code (very optimized readouts), the layers (also a 3d render)... inside of here you have the render, the canvas, the cues, the layers. We have a main camera here and then we have the settings camera. I didn't want these to be affected by the zoom, so I put that on a separate camera and a separate render. When you zoom out it doesn't affect this 3D, but I did want to attach the camera to when I scrolled up and down... canvas has background, lines/hash marks, layers, and playhead moving in space."*

* **Explicación técnica:**  
  - Desacoplamiento de cámaras: La columna izquierda de nombres de pistas (`Settings / Layers`) se dibuja mediante un `Render TOP` secundario con una cámara ortográfica fija en X, pero vinculada en Y al paneo vertical del canvas principal.
  - El fondo, líneas de división (grid marks) y el cursor de reproducción (*playhead*) son primitivas geométricas 3D animadas.

---

### [05:00 - 07:28] Instancing en GPU, Shaders GLSL y Tweens
> **Original (EN):**  
> *"The cues: this is fairly complicated... everything kind of lives in this 3D environment and everything is instances. These are all instance geometry... each cue component is actually just your instance information. So Q0, when you move this around, you're changing your instance data... background color changes here... outlines are all handled in the shader, I didn't want to tie it to any texture... instance geometry starts with a line of four points, and inside the vertex shader I'm positioning it based on instance 3 page (fade in, four positions, height of cue)."*

* **Explicación técnica:**  
  - Cada cue NO es un botón individual ni un COMP pesado; los datos se condensan en tablas y CHOPs de instancias.
  - La silueta trapezoidal de los fades se resuelve en el **Vertex Shader** desplazando los 4 puntos de una línea base según los parámetros de `FadeIn`, `FadeOut`, `Start`, `Length` y `Height`.
  - El renderizado final del borde de selección se resuelve en el shader de fragmentos.

---

### [07:28 - 09:20] Componente Time, Timer CHOP y Segment DAT
> **Original (EN):**  
> *"We're taking all this timing data and sending it to the time component. Here we have a replicator grabbing info for each cue... fade in, fade out, length. These are directly going to be part of the segment dat (begin, length)... so when this playhead moves it is following this timer... wouldn't be too challenging to line this up with a movie to actually play the movie under it... sending out timecode to the top level."*

* **Explicación técnica:**  
  - El componente `Time` construye dinámicamente un `Segment DAT` con columnas `begin` y `length`.
  - El `Timer CHOP` ejecuta el transporte y notifica los instantes de entrada/salida de cada bloque.
  - Esto facilita disparar un `Movie File In TOP`, un trigger DMX/sACN o comandos OSC/Python exactamente sincronizados al llegar a cada segmento.

---

### [09:20 - 10:56] RenderPick por Instance ID y Parámetros Centrales
> **Original (EN):**  
> *"Layers are being rendered by this second camera... again instancing because I wanted to be able to easily click on it. I didn't want to deal with clicking UV coordinates, so the whole system really goes off of instanceId... these are all just rectangles. Almost all settings for the entire system are right here under user settings and system settings, where I can reference calculations anywhere in the project."*

* **Explicación técnica:**  
  - Para la interactividad de selección y clic sobre las pistas y cues, TouchDesigner utiliza el operador `RenderPick DAT/CHOP` configurado para consultar el canal de `instance id`.
  - Esto garantiza alta tasa de cuadros (60 fps estables) sin importar cuántas cues o capas existan.
