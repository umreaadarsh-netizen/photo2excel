from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io, os, re
from PIL import Image
import pytesseract
from openpyxl import Workbook

app=FastAPI(title="Photo2Excel AI")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ExcelData(BaseModel):
    rows:list[list[str]]

def clean(s):
    return re.sub(r"\s+"," ",str(s)).strip()

def parse_text(text):
    lines=[clean(x) for x in text.splitlines() if clean(x)]
    rows=[]
    for line in lines:
        parts=re.split(r"\s{2,}|\t|\s*\|\s*",line)
        rows.append([clean(x) for x in parts if clean(x)])
    if not rows:
        return [["No data detected"]]
    width=max(map(len,rows))
    return [r+[""]*(width-len(r)) for r in rows]

@app.post("/extract")
async def extract(file:UploadFile=File(...)):
    if not file.filename.lower().endswith((".png",".jpg",".jpeg")):
        raise HTTPException(400,"For this starter build, upload PNG/JPG/JPEG images.")
    raw=await file.read()
    try:
        img=Image.open(io.BytesIO(raw)).convert("RGB")
        text=pytesseract.image_to_string(img, config="--psm 6")
        return {"rows":parse_text(text)}
    except Exception as e:
        raise HTTPException(500,f"OCR failed: {e}")

@app.post("/excel")
def excel(data:ExcelData):
    wb=Workbook(); ws=wb.active; ws.title="Extracted Data"
    for row in data.rows: ws.append(row)
    for col in ws.columns:
        letter=col[0].column_letter
        maxlen=max(len(str(c.value or "")) for c in col)
        ws.column_dimensions[letter].width=min(max(maxlen+2,12),40)
    out=io.BytesIO(); wb.save(out); out.seek(0)
    return StreamingResponse(out,media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition":"attachment; filename=cleaned_table.xlsx"})
