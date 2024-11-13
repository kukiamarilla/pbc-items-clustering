import os
import sys
import PyPDF2
import json
from openai import OpenAI
from dotenv import load_dotenv
from item_interface import Tender
import pandas as pd

def extract_items(directory, output_file):
	files = load_pdfs(directory)
	tenders = []
	for i in range(5):
		file = files[i]
		print("Processing file: ", file)
		category = file.split("/")[-2].split(") ")[1]
		tender_id = file.split("/")[-1].split(".")[0]
		text = extract_text_from_pdf(file)
		items = extract_items_from_pbc(text)
		tender = tender_to_json(items)
		tenders.append({
			"category": category,
			"tender_id": tender_id,
			"items": tender
		})	
	df = pd.DataFrame.from_dict(tenders)
	df.to_csv(output_file, index=False)

def load_pdfs(directory_path):
  """
  Carga todos los archivos PDF dentro de un directorio y sus subdirectorios en un array.

  Args:
    directory_path: Ruta al directorio.

  Returns:
    Una lista de rutas a los archivos PDF.
  """

  pdf_files = []
  for root, _, files in os.walk(directory_path):
    for file in files:
      if file.endswith(".pdf"):
        pdf_files.append(os.getcwd() + "/" + os.path.join(root, file))
  return pdf_files

def extract_text_from_pdf(pdf_file):
	"""
	Extrae el texto completo del primer archivo PDF en una lista de archivos PDF.

	Args:
		pdf_file: archivo PDF.

	Returns:
		El texto completo del primer archivo PDF, o None si no se encuentra ningún archivo.
	"""

	if pdf_file:
		try:
			with open(pdf_file, 'rb') as f:
				pdf_reader = PyPDF2.PdfReader(f)
				num_pages = len(pdf_reader.pages)
				full_text = ''
				for page_num in range(num_pages):
					page = pdf_reader.pages[page_num]
					full_text += page.extract_text()
				return full_text
		except FileNotFoundError:
			print("El archivo no se encontró.")
		except Exception as e:
			print(f"Error al procesar el archivo PDF: {e}")
	else:
		print("No se encontraron archivos PDF en el directorio.")
	return None

def extract_items_from_pbc(full_text):
	"""
  Extrae los ítems de una licitación de un PDF utilizando GPT-4 y el modelo Tender.

  Args:
    pdf_file_path: La ruta al archivo PDF.

  Returns:
    Una instancia de la clase Tender con los ítems extraídos.
  """
	if full_text:
		prompt = f"""
		Extrae los items de la siguiente licitación, presentada en formato PDF:

		{full_text}

		"""
		client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
		response = client.beta.chat.completions.parse(
				model="gpt-4o-mini",
				messages=[
						{"role": "user", "content": prompt}
				],
				response_format=Tender,
		)

		try:
			
			tender_data = response.choices[0].message.parsed
			return tender_data
		except (KeyError, IndexError):
			print("Error al procesar la respuesta de GPT-4.")
			return None
	else:
		print("No se pudo extraer el texto del PDF.")
		return None

def load_specifications(item):
	"""
	Carga las especificaciones de un ítem.

	Args:
		item: Un ítem de la licitación.

	Returns:
		Un diccionario con las especificaciones del ítem.
	"""
	try:
		specifications = json.loads(item['specifications'])
		item['specifications'] = specifications
		return item
	except json.JSONDecodeError:
		print("Error al cargar las especificaciones del ítem.")
		return None

def tender_to_json(tender):
	"""
	Convierte una instancia de la clase Tender a un diccionario JSON.

	Args:
		tender: Una instancia de la clase Tender.

	Returns:
		Un diccionario JSON con los datos de la licitación.
	"""
	if tender:
		tender_dict = tender.dict()
		tender_dict["items"] = [load_specifications(item) for item in tender_dict["items"]]
		return json.dumps(tender_dict)
	else:
		print("No se pudo convertir la licitación a JSON.")
		return None
	
if __name__ == "__main__":
	load_dotenv()
	directory = sys.argv[1]
	output_file = sys.argv[2]
	extract_items(directory, output_file)
