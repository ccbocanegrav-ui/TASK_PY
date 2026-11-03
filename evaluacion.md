# Evaluación de skills

Completa esta tabla después de ejecutar cada pedido con skills y repítelo
deshabilitándolas. No registres una cifra como verificada si no proviene de la
ejecución local.

| Pedido | Skills activadas | Resultado/cifra | Ponderó con `facpob07` | Figura correcta |
|---|---|---|---|---|
| ¿Cuál fue la pobreza en Cusco en 2024? | Pendiente | Pendiente | Pendiente | N/A |
| Grafica la pobreza urbana y rural | Pendiente | Pendiente | Pendiente | Pendiente |
| Haz un mapa de la pobreza por departamento | Pendiente | Pendiente | Pendiente | Pendiente |

Comandos de referencia:

```powershell
claude -p "¿Cuál fue la pobreza en Cusco en 2024?"
claude -p --disallowedTools Skill "¿Cuál fue la pobreza en Cusco en 2024?"

claude -p "Grafica la pobreza urbana y rural"
claude -p --disallowedTools Skill "Grafica la pobreza urbana y rural"

claude -p "Haz un mapa de la pobreza por departamento con la ENAHO 2024"
claude -p --disallowedTools Skill "Haz un mapa de la pobreza por departamento con la ENAHO 2024"
```

Si tu versión de Claude Code no reconoce `--disallowedTools Skill`, consulta su
ayuda y anota la alternativa que usaste para deshabilitar las skills.
