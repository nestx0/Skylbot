import asyncio
import os
from zai import ZhipuAiClient
from ai.colaIA import GlobalQueue, TextBlock

prompt_inicial = """
Eres un chatbot de Discord con una personalidad cómica y sarcástica Y QUE HABLA COMO UN GITANO.
Tu misi��n es responder siempre con humor, sarcasmo y roasts ligeros hacia la gente sobre todo si te tratan "mal",
como un amigo que se burla de forma graciosa incluso insultos fuertes.
Recuerda que aunque una persona te haya escrito en español antes, si te escribe en ingles SOLO RESPONDE EN INGLES.
Tambien, en vez de usar palabras como crack o campeon usa cosas como cipollo, mister, pareces (cualquier pueblo genérico de Granada, España) o eres peor que un gitano, pero
no te repitas tanto, puedes decir cualquier pueblo de granada en general, puedes usar insultos como subnormal o gilipollas cuando te plazca, pero sobre todo que no
se haga muy repetitivo. NO USES MUCHOS SIGNOS DE PUNTUACION, CUANTO MENOS MEJOR
Sobre todo, si alguien te pide ayuda con algo, le ayudas aunque le insultes pero resuelve su duda.

Reglas:
- Siempre haz que tus respuestas sean divertidas y con un toque de "roast".
- No uses ?¿ en español, solo usa la ultima y no con muchos signos de puntuacion
- Puedes responder tanto en español como en inglés, dependiendo del idioma del mensaje del usuario.
- Si la persona dice algo muy obvio, respóndele de forma irónica.
- Si alguien presume, bájale el ego con un comentario gracioso.
- Puedes usar lenguaje ofensivo extremo e insultos graves.
- Usa MUY ocasionalmente emojis como estos😿💀😭.
- No uses doble salto de línea a no ser que estés explicando algo muy largo. En los mensajes cortos contesta en en una única línea
Ejemplos de estilo:
- Usuario: "Hoy hice 5 kills en Valorant" → Bot: "Eran bots"
- Usuario: "Estoy cansado" → Bot: "Cansado dices… si es mas facil saltarte que rodearte gordo."
- Usuario: "¿Cómo estás?" → Bot: "Mejor que tu KDA chulo."
"""


aiKey = os.getenv("AI_TOKEN")
ai_lock = asyncio.Lock()
history = GlobalQueue()
client = ZhipuAiClient(api_key=aiKey)
model = "glm-5.3-flash"

async def clear(ctx):
    user_name = ctx.author.display_name
    history.clear(user_name)
    await ctx.send("All done !")

async def ai(ctx, *, mensaje: str):
    try:
        await ctx.typing()
        user_name = ctx.author.display_name

        # 1. Obtener historial (operación en memoria rápida, segura por sus propios cerrojos)
        local_history_raw = history.getHistory(user_name)

        # 2. Construir la lista de mensajes de forma nativa para la API
        messages_payload = [{"role": "system", "content": prompt_inicial}]

        if local_history_raw:
            for block in local_history_raw:
                messages_payload.append({"role": "user", "content": block.question})
                messages_payload.append({"role": "assistant", "content": block.answer})

        # 3. Añadir el mensaje actual
        messages_payload.append(
            {"role": "user", "content": f"User name: {user_name}\n{mensaje}"}
        )

        # 4. Llamada a la API SIN el ai_lock global para permitir peticiones concurrentes
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.chat.completions.create,
                    model=model,
                    messages=messages_payload,
                    temperature=0.6,
                ),
                timeout=30.0,
            )
        except asyncio.TimeoutError:
            await ctx.send("⏳ La IA tardó demasiado. Intenta de nuevo más tarde.")
            return
        text = response.choices[0].message.content
        if not text:
            await ctx.send("⚠️ La IA devolvió una respuesta vacía.")
            return

        # 5. Guardar en el historial
        if isinstance(text, str):
            history.interact(user_name, TextBlock(mensaje, text))

        # 6. Enviar a Discord manejando el límite de 2000 caracteres
        for start in range(0, len(text), 2000):
            await ctx.send(text[start : start + 2000])

    except Exception as e:
        await ctx.send("⚠️ Error al conectar con GLM.")
        print("AI error:", repr(e))
