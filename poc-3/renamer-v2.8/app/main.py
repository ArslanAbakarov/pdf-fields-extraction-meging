# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
import io, uuid, logging, sys
from fastapi.responses import RedirectResponse

# Import the simplified renamer regardless for fallback
from app.simple_renamer import simple_rename_pdf

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import the full renamer, fall back to simple one
try:
    from app.renamer import rename_pdf
    logger.info("Using full vector-based renamer")
    USE_FULL_RENAMER = True
except Exception as e:1
    logger.warning(f"Could not load full renamer: {e}")
    logger.info("Using simplified text-based renamer")
    USE_FULL_RENAMER = False

app = FastAPI(title="PDF Widget Renamer")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/rename")
async def rename_pdf_endpoint(request: Request, file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(415, "Only PDF files are accepted")
    
    data = await file.read()
    logger.info(f"Processing PDF file: {file.filename}, size: {len(data)} bytes")
    
    try:
        if USE_FULL_RENAMER:
            # Use the vector-based renamer
            logger.info("Using full vector-based renamer")
            out_bin, mapping_info = rename_pdf(data)
        else:
            # Use the simplified text-based renamer
            logger.info("Using simplified text-based renamer")
            out_bin, mapping_info = simple_rename_pdf(data)
            
        # Log results
        logger.info(f"Renaming complete: {mapping_info['total_widgets']} widgets, "
                   f"{mapping_info['changed_widgets']} changed, {mapping_info['unchanged_widgets']} unchanged")
        
    except Exception as e:
        logger.exception("Rename failed")
        
        # If full renamer failed, try simple renamer as fallback
        if USE_FULL_RENAMER:
            try:
                logger.info("Trying simplified renamer as fallback")
                out_bin, mapping_info = simple_rename_pdf(data)
                logger.info(f"Fallback successful: {mapping_info['total_widgets']} widgets processed")
            except Exception as inner_e:
                logger.exception("Fallback also failed")
                raise HTTPException(500, f"Rename failed: {e}, fallback also failed: {inner_e}")
        else:
            raise HTTPException(500, f"Rename failed: {e}")

    # Check the accept header from the request
    accept_header = request.headers.get("accept", "")
    if accept_header and "application/json" in accept_header:
        logger.info(f"Returning JSON response with {len(mapping_info['mapping_info'])} items")
        return mapping_info

    logger.info(f"Returning PDF file, size: {len(out_bin)} bytes")
    return StreamingResponse(
        io.BytesIO(out_bin),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{uuid.uuid4()}.pdf"'
        },
    )

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/static/index.html")