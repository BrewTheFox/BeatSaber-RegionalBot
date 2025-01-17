# BeatSaber Regional Bot

## Descripción del Proyecto

Este bot de Discord está diseñado para mejorar la experiencia de la comunidad de Beat Saber, especialmente para jugadores de una región específica (en mi caso, `CO`). Se integra con las APIs de ScoreSaber y BeatLeader para proporcionar información en tiempo real y fomentar la competencia amistosa. El bot ofrece una variedad de funcionalidades que mantienen a los jugadores conectados y motivados.

## Características Principales

### 🔔 Alertas en Tiempo Real
  *   Recibe notificaciones instantáneas en Discord cada vez que un jugador de tu país completa una partida en Beat Saber.
  *   La información incluye detalles del jugador, la canción, la puntuación, el PP ganado y más.
  *   Soporte para ScoreSaber y BeatLeader.

### 🔗 Vinculación de Cuentas
  *   Permite a los usuarios vincular sus perfiles de ScoreSaber y BeatLeader a sus cuentas de Discord.
  *   Facilita el acceso rápido a estadísticas personales y de otros jugadores.

### 📊 Información de Jugadores
  *   Accede a perfiles detallados de jugadores de ScoreSaber y BeatLeader directamente en Discord.
  *   Muestra información relevante como el rango global, rango en el país, PP, puntuación total y número de partidas jugadas.

### 🏆 Retos Personalizables
  *   Genera retos aleatorios basados en diferentes niveles de dificultad (Fácil, Difícil y Experto+).
  *   Los retos pueden ser basados en puntaje, estrellas del mapa o PP.
  *   Los usuarios pueden solicitar y cancelar retos.
  *   Recibe felicitaciones del bot cuando se completa un reto.

### 📢 Feed de Jugadores
  *   Canal dedicado para notificar quien esta jugando y cuando, fomentando la participación activa de la comunidad.
  *   Muestra mensajes personalizados cuando un jugador supera a otro en el leaderboard.

### ⚙️ Configuración Sencilla
  *   Administra fácilmente los canales para retos, alertas de puntuaciones y feed de jugadores utilizando comandos en Discord.

## Comandos del Bot

| Comando                      | Descripción                                                               | Permisos Requeridos |
| ---------------------------- | ------------------------------------------------------------------------- | -------------------- |
| `/blperfil`                  | Muestra tu perfil de BeatLeader.                                           | Ninguno              |
| `/verblperfil <miembro>`     | Muestra el perfil de BeatLeader de un usuario específico del servidor.     | Ninguno              |
| `/ssperfil`                  | Muestra tu perfil de ScoreSaber.                                            | Ninguno              |
| `/verssperfil <miembro>`     | Muestra el perfil de ScoreSaber de un usuario específico del servidor.      | Ninguno              |
| `/vincular <link>`          | Vincula tu perfil de Beat Saber (ScoreSaber o BeatLeader) a Discord.         | Ninguno              |
| `/desvincular`               | Desvincula tu cuenta de Beat Saber de Discord.                             | Ninguno              |
| `/reto <dificultad>`         | Genera un reto de Beat Saber basado en la dificultad seleccionada.       | Ninguno              |
| `/cancelar`                  | Cancela el reto actual.                                                     | Ninguno              |
| `/establecer_canal_retos`    | Establece el canal para los mensajes de retos del servidor.                 | Administrador        |
| `/establecer_canal_scores`   | Establece el canal para los mensajes de alertas de puntuaciones del servidor. | Administrador        |
| `/establecer_canal_feed`    | Establece el canal para los mensajes de actividad de jugadores del servidor.     | Administrador        |
| `/eliminar_canal`          | Elimina el canal actual de las notificaciones del bot. | Administrador       |

## Instalación

1.  **Clona el Repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_REPOSITORIO>
    ```

2.  **Configura el Entorno:**
    *   En el archivo `.env` agrega tu token de Discord:
        ```env
        token=TU_TOKEN_DE_DISCORD
        ```
    *   Configura el archivo `config.json` con tus preferencias, como el país, los parámetros de los retos y los textos personalizados.

3.  **Instala las Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecuta el Bot:**
    ```bash
    python src/main.py
    ```

## Contacto

Si tienes alguna pregunta o sugerencia, no dudes en contactarme.

---
**Creado por Brew**
