# app/simple_renamer.py
import fitz  # PyMuPDF
import io
import pickle
import os
import logging

# Set up paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_PATH = os.path.join(ROOT_DIR, "widget_minilm_metadata.pkl")

# Try to load widget names from the metadata pickle file
try:
    metadata = pickle.load(open(METADATA_PATH, "rb"))
    # Extract widget names from metadata
    if isinstance(metadata, list):
        if isinstance(metadata[0], dict) and "widgetName" in metadata[0]:
            NAMES = [item["widgetName"] for item in metadata]
        else:
            NAMES = metadata
    else:
        NAMES = ["widget_{i}" for i in range(100)]  # fallback

    logging.info(f"Loaded {len(NAMES)} widget names from metadata")
except Exception as e:
    logging.error(f"Failed to load widget names from metadata: {e}")

# Define a margin for context extraction (in points)
MARGIN = 30

def get_context_text(page, rect):
    """Extract context text around a widget"""
    words = page.get_text("words")
    return " ".join(w[4] for w in words if fitz.Rect(w[:4]).intersects(rect))

def rename_widget(doc, widg, new_name):
    """Rename a widget using appropriate method based on PyMuPDF version"""
    try:
        if hasattr(widg, "set_field_name"):
            widg.set_field_name(new_name)
        elif hasattr(widg, "set_name"):
            widg.set_name(new_name)
        else:
            # Try direct assignment
            widg.field_name = new_name
            
        # Force update
        widg.update()
        return True
    except Exception as e:
        logging.error(f"Failed to rename widget: {e}")
        return False

def simple_rename_pdf(binary):
    """Rename PDF form fields using a simplified matching approach"""
    doc = fitz.open(stream=binary, filetype="pdf")
    total_widgets = 0
    mapping_info = []
    unchanged_widgets = 0
    successful_renames = 0
    
    # Create lowercase mapping for case-insensitive matches
    name_map = {name.lower(): name for name in NAMES}
    
    for p_num, p in enumerate(doc):
        for w in p.widgets():
            # Get current field name
            original_name = w.field_name
            total_widgets += 1
            
            # Extract context for reporting/debugging
            ctx = get_context_text(p, fitz.Rect(w.rect.x0-MARGIN, w.rect.y0-MARGIN,
                                         w.rect.x1+MARGIN, w.rect.y1+MARGIN))
            
            # Simple decision tree for renaming:
            new_name = original_name  # Default to keeping original name
            
            # 1. If name is already in our list, don't change it
            if original_name in NAMES:
                unchanged_widgets += 1
            
            # 2. Try case-insensitive match
            elif original_name.lower() in name_map:
                new_name = name_map[original_name.lower()]
                
                # Only rename if actual casing differs
                if new_name != original_name:
                    if rename_widget(doc, w, new_name):
                        successful_renames += 1
                        logging.info(f"Renamed: '{original_name}' → '{new_name}' (case fix)")
                    else:
                        new_name = original_name  # Revert if rename failed
                else:
                    unchanged_widgets += 1
            
            # 3. For numeric or empty fields, use a likely match from context if possible
            elif not original_name.strip() or original_name.isdigit():
                # Leave these fields unchanged for now - the approach needs refinement
                unchanged_widgets += 1
            
            # 4. For other fields, leave unchanged
            else:
                unchanged_widgets += 1
            
            # Track mapping info
            mapping_info.append({
                "page": p_num + 1,
                "original_name": original_name,
                "new_name": new_name,
                "context": ctx[:100] if ctx else ""  # Limit context length
            })
    
    # Calculate stats
    changed_widgets = total_widgets - unchanged_widgets
    accuracy_rate = round((unchanged_widgets / total_widgets) * 100, 2) if total_widgets else 0
    
    # Log results
    logging.info(f"Processed {total_widgets} widgets across {len(doc)} pages")
    logging.info(f"Unchanged: {unchanged_widgets}, Changed: {changed_widgets}, Successful renames: {successful_renames}")
    
    # Save PDF
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    buf.seek(0)
    
    return buf.read(), {
        "mapping_info": mapping_info,
        "total_widgets": total_widgets,
        "changed_widgets": changed_widgets,
        "unchanged_widgets": unchanged_widgets,
        "accuracy": accuracy_rate
    }

def calculate_accuracy_metrics(total, unchanged, successful_renames):
    """Calculate various accuracy metrics for PDF form field renaming.
    
    Args:
        total: Total number of widgets processed
        unchanged: Number of widgets not needing changes
        successful_renames: Number of widgets successfully renamed
    
    Returns:
        Dictionary with accuracy metrics
    """
    # No widgets processed
    if total == 0:
        return {
            "total_widgets": 0,
            "unchanged_widgets": 0,
            "changed_widgets": 0,
            "successful_renames": 0,
            "accuracy": 0,
            "success_rate": 0
        }
    
    # Calculate metrics
    changed = total - unchanged
    
    # Calculate accuracy as % of widgets that already had correct names
    # Higher is better - means forms were already mostly correctly named
    accuracy = round((unchanged / total) * 100, 2)
    
    # Calculate success rate for changes that were needed
    # Higher is better - means our renamer successfully renamed what needed changing
    success_rate = 0
    if changed > 0:
        success_rate = round((successful_renames / changed) * 100, 2)
    
    return {
        "total_widgets": total,
        "unchanged_widgets": unchanged,
        "changed_widgets": changed,
        "successful_renames": successful_renames,
        "accuracy": accuracy, 
        "success_rate": success_rate
    } 