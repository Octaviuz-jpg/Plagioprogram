import pdfplumber
import re

def extract_bibliography(pdf_path):
    section_keywords = ["bibliografía", "referencias", "works cited", "references", "citations"]

    # Patrones mejorados para capturar citas con más variantes
    patterns = {
        "APA": r'[A-Z][a-z]+(?:, [A-Z]\.?){1,2} \(\d{4}\) .*?(?:Vol\. \d+, No\. \d+, pp\. \d+-\d+)?[\.\n]',
        "Chicago": r'[A-Z][a-z]+, [A-Z][a-z]+\. ".+?" .*?\d{4}[\.\n]',
        "MLA": r'[A-Z][a-z]+, [A-Z][a-z]+\. .*?\.[A-Za-z ]+, \d{4}[\.\n]',
        "APA_Chicago_Hybrid": r'[A-Z][a-z]+, [A-Z]\. \(\d{4}\):? “.+?”, .*?Vol\. \d+, núm\. \d+, p\. \d+-\d+.*[\.\n]',
        "URL": r'Recuperado de:\s*https?://[^\s]+|https?://[^\s]+'
    }

    bibliography = {style: [] for style in patterns}
    in_section = False
    section_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            if not in_section:
                for keyword in section_keywords:
                    if keyword.lower() in text.lower():
                        in_section = True
                        section_text = text.split(keyword, 1)[-1]
                        break
            else:
                section_text += "\n\n" + text

    section_text = re.sub(r'\s+', ' ', section_text).strip()

    for style, pattern in patterns.items():
        matches = re.findall(pattern, section_text, re.MULTILINE)
        if matches:
            bibliography[style].extend([match.strip() for match in matches])  # Limpia cada cita

    return bibliography

# Ejemplo de uso
pdf_path = "pruebaBibliografia.pdf"
bibliography = extract_bibliography(pdf_path)

# Imprimir con separación correcta
for style, refs in bibliography.items():
    print(f"\n=== {style.upper()} ===")
    for i, ref in enumerate(refs, 1):
        print(f"{i}. {ref}\n")  # Espaciado adecuado
