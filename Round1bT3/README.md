# Round 1B - Persona-Driven Document Intelligence

## 📥 Input
- `persona.txt`: Text describing the user (e.g., "PhD researcher...")
- `job.txt`: Task to be done (e.g., "Write a literature review...")
- 3–10 PDFs in `app/input/`

## 🧠 Output
- `challenge1b_output.json` in `app/output/`

## 🐳 Build

```bash
docker build --platform linux/amd64 -t pdf-intelligence:latest .
