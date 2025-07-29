import pdfplumber
import re

def extract_bibliography(pdf_path):
    section_keywords = ["bibliografía"]

    # 🔍 Triggers para detectar inicio de nueva cita
    triggers = [
        r'\(\d{4}\)', r'\(s\.f\.\)', r'^Ley', r'^Decreto', r'^Gaceta Oficial',
        r'^https?://', r'^Recuperado de:\s*https?://'
    ]

    # 🧭 Patrones de estilo bibliográfico
    patterns = {
        "APA": r'[A-Z][a-z]+(?:, [A-Z]\.?)*(?: y [A-Z][a-z]+)* \((\d{4}|s\.f\.)\).*',
        "Chicago": r'[A-Z][a-z]+, [A-Z][a-z]+\. ".+?" .*?\d{4}',
        "MLA": r'[A-Z][a-z]+, [A-Z][a-z]+\. .*?\.[A-Za-z ]+, \d{4}',
        "APA_Chicago_Hybrid": r'.*Vol\. \d+, núm\. \d+, p\. \d+-\d+.*',
        "URL": r'https?://[^\s]+|Recuperado de:\s*https?://[^\s]+',
        "Legal": r'(Ley|Decreto|Gaceta Oficial).*?\d{4}'
    }

    bibliography = {style: [] for style in patterns}
    in_section = False
    section_text = ""

    # 📖 Extraer texto desde el PDF
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lowered_text = text.lower()
            if not in_section:
                for keyword in section_keywords:
                    if keyword.lower() in lowered_text:
                        in_section = True
                        idx = lowered_text.find(keyword.lower())
                        section_text = text[idx + len(keyword):].strip()
                        break
            else:
                section_text += "\n\n" + text

    # 🧠 Agrupación de líneas por heurística de cita
    lines = section_text.splitlines()
    blocks = []
    current = ""

    def starts_new_citation(line):
        line = line.strip()
        return any(re.search(trigger, line, re.IGNORECASE) for trigger in triggers)

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 🔗 Unir líneas cortadas por guión sin separar cita
        if current.endswith('-'):
            current = current[:-1] + line
            continue

        if starts_new_citation(line):
            if current:
                blocks.append(current.strip())
            current = line
        else:
            current += " " + line

    if current:
        blocks.append(current.strip())

    # 📌 Clasificar bloques por estilo
    for block in blocks:
        matched = False
        for style, pattern in patterns.items():
            if re.search(pattern, block, re.IGNORECASE):
                if block not in bibliography[style]:
                    bibliography[style].append(block)
                matched = True
                break

        # 🎯 Heurística adicional para institucionales con año
        if not matched and re.search(r'\((\d{4}|s\.f\.)\)', block):
            if block not in bibliography["APA"]:
                bibliography["APA"].append(block)

    return bibliography

# 🧪 Ejemplo de uso
pdf_path = "pruebaBibliografia.pdf"
bibliography = extract_bibliography(pdf_path)

# 📋 Impresión ordenada
print("\n📚 Citas extraídas y agrupadas por estilo:\n")
for estilo, citas in bibliography.items():
    print(f"🔖 Estilo: {estilo} ({len(citas)} cita(s))\n")
    for i, cita in enumerate(citas, 1):
        print(f"  {i}. {cita}\n")
    print("-" * 60 + "\n")
