import azure.functions as func
import logging
import json
import base64
import fitz  # PyMuPDF

# Authenticate the function app with function level authentication!!
# This function app serves for splitting PDF files given a page range. It is intended to be invoked from Power Automate Cloud Flows using HTTP with function level authentication.
# The function app expects a JSON payload with the following structure:
# {
#     "pdf": "base64_encoded_pdf",
#     "pages": [1, 3, 5]
# }
# The "pdf" field is the base64 encoded PDF file, and the "pages" field is an array of page numbers to be extracted from the PDF file.
# The function app returns a JSON payload with the following structure:
# {
#     "$content-type": "application/pdf",
#     "$content": "base64_encoded_pdf"
# }
# The "content-type" field specifies the content type of the response, and the "content" field contains the base64 encoded PDF file with the extracted pages.
# Which is what Power Automate Cloud Flows expects as a response (a JSON payload with the content type and content fields).
# ⭐ The PA Cloud Flow that I created is named 'SPLIT PDF VIA AZURE FUNCTION' (under my aagirre92@66z6zy.onmicrosoft.com account, default environment)


# Create a function app

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="merge_and_split_pdf")
def merge_and_split_pdf(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == 'POST':
        try:
            # Parse the request body
            req_body = req.get_json()
            
            # Decode the base64 PDF content
            pdf_base64 = req_body['pdf']
            page_range = req_body['pages']
            
            # Convert base64 to PDF bytes
            pdf_bytes = base64.b64decode(pdf_base64)
            
            # Open the PDF document
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # Create a new PDF with selected pages
            result_doc = fitz.open()
            
            # Add specified pages to the new document
            for page_num in page_range:
                if 1 <= page_num <= doc.page_count:
                    result_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
            
            # Convert the new PDF to bytes
            result_pdf_bytes = result_doc.write()
            
            # Encode result back to base64
            result_base64 = base64.b64encode(result_pdf_bytes).decode('utf-8')
            
            # Return the result
            return func.HttpResponse(
                body=json.dumps({
                    "$content-type": "application/pdf",
                    "$content": result_base64
                }),
                mimetype="application/json",
                status_code=200
            )
        
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return func.HttpResponse(
                str(e),
                status_code=400
            )