const $ = (id) => document.getElementById(id);

const chat = $("chat");
const form = $("form-chat");
const entrada = $("entrada");
const btnEnviar = $("btn-enviar");
const btnLimpiar = $("btn-limpiar");

let historial = [];
let generando = false;

function actualizarEstadoServidor(ok, detalle) {
  const cont = $("estado-servidor");
  const txt = $("estado-texto");
  cont.className = "estado " + (ok ? "estado-ok" : "estado-error");
  txt.textContent = ok ? "Servidor IA y modelo listos" : detalle;
}

function crearMensaje(rol, contenido) {
  const div = document.createElement("div");
  div.className = "mensaje " + rol;
  const burbuja = document.createElement("div");
  burbuja.className = "burbuja";
  burbuja.textContent = contenido || " ";
  div.appendChild(burbuja);
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return burbuja;
}

function actualizarParametros() {
  $("temp-out").textContent = $("temperatura").value;
  $("tok-out").textContent = $("max_tokens").value;
}

async function cargarMetrics() {
  try {
    const res = await fetch("/api/metrics");
    const m = await res.json();
    $("m-peticiones").textContent = m.peticiones;
    $("m-tps").textContent = m.peticiones ? m.promedio_tokens_s + " tok/s" : "—";
    $("m-lat").textContent = m.peticiones ? m.promedio_latencia_s + " s" : "—";
    $("m-primer").textContent = m.peticiones ? m.promedio_primer_token_s + " s" : "—";
    $("m-errores").textContent = m.errores;
  } catch { /* sin datos aún */ }
}

async function verificarServidor() {
  try {
    const res = await fetch("/health");
    const estado = await res.json();
    if (estado.status === "ok" && estado.cargado) {
      actualizarEstadoServidor(true, "Servidor IA y modelo listos");
      $("modelo").innerHTML = estado.modelos
        .map((m) => `<option value="${m}">${m}</option>`).join("");
    } else if (estado.status === "ok") {
      actualizarEstadoServidor(false, "Modelo no descargado (vea README)");
    } else {
      actualizarEstadoServidor(false, "Ollama no disponible: " + (estado.detalle || ""));
    }
  } catch {
    actualizarEstadoServidor(false, "No se pudo contactar el servidor");
  }
}

async function enviarPrompt(e) {
  e.preventDefault();
  const prompt = entrada.value.trim();
  if (!prompt || generando) return;

  const temperatura = parseFloat($("temperatura").value);
  const max_tokens = parseInt($("max_tokens").value, 10);
  const sistema = $("usar-sistema").checked;

  crearMensaje("user", prompt);
  entrada.value = "";
  entrada.style.height = "auto";

  const burbuja = crearMensaje("bot", "");
  generando = true;
  btnEnviar.disabled = true;
  btnEnviar.textContent = "Generando…";

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt,
        temperatura,
        max_tokens,
        sistema,
        historial: historial.slice(-6).map((m) => ({ role: m.role, content: m.content })),
      }),
    });
    if (!res.ok) throw new Error("HTTP " + res.status);

    const lector = res.body.getReader();
    const decodificador = new TextDecoder();
    let texto = "";
    while (true) {
      const { value, done } = await lector.read();
      if (done) break;
      texto += decodificador.decode(value, { stream: true });
      burbuja.textContent = texto;
      chat.scrollTop = chat.scrollHeight;
    }
    burbuja.classList.add("finalizado");
    historial.push({ role: "user", content: prompt });
    historial.push({ role: "assistant", content: texto });
  } catch (err) {
    burbuja.textContent = "[Error al conectar con el servidor: " + err.message + "]";
  } finally {
    generando = false;
    btnEnviar.disabled = false;
    btnEnviar.textContent = "Enviar";
    cargarMetrics();
  }
}

entrada.addEventListener("input", () => {
  btnEnviar.disabled = generando || !entrada.value.trim();
  entrada.style.height = "auto";
  entrada.style.height = Math.min(entrada.scrollHeight, 160) + "px";
});
entrada.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); enviarPrompt(e); }
});
$("temperatura").addEventListener("input", actualizarParametros);
$("max_tokens").addEventListener("input", actualizarParametros);
btnLimpiar.addEventListener("click", () => {
  chat.querySelectorAll(".mensaje").forEach((el) => el.remove());
  historial = [];
});

verificarServidor();
cargarMetrics();
setInterval(cargarMetrics, 5000);