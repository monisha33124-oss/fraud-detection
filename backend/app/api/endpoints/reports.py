import io
import csv
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api import deps
from app.db.models import User, Transaction, InvestigationCase, FraudPrediction, AuditLog, FraudAlert

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    REPORTLAB_INSTALLED = True
except ImportError:
    REPORTLAB_INSTALLED = False

router = APIRouter()

@router.get("/generate")
def generate_report(
    request: Request,
    format: str = Query(..., description="csv or pdf"),
    report_type: str = Query(..., description="transaction, fraud, risk, investigation, customer, model, audit"),
    start_date: str = None,
    end_date: str = None,
    customer_id: str = None,
    risk_level: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin)
):
    """Generate a dynamic report in CSV or PDF format."""
    
    if format not in ["csv", "pdf"]:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'pdf'.")
        
    if format == "pdf" and not REPORTLAB_INSTALLED:
        raise HTTPException(status_code=500, detail="reportlab not installed.")
        
    # Create Audit Log for report generation
    ip_address = request.client.host if request.client else "unknown"
    audit = AuditLog(
        user_id=current_user.id,
        role=current_user.role.value if current_user.role else "UNKNOWN",
        action=f"GENERATED_{report_type.upper()}_REPORT",
        resource=f"Format:{format}",
        status="SUCCESS",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    # --- Fetch Data based on report_type ---
    data = []
    headers = []
    title = f"{report_type.capitalize()} Report"
    
    if report_type == "transaction":
        query = db.query(Transaction)
        if customer_id:
            query = query.filter(Transaction.customer_id == customer_id)
        # simplistic date filter for demo
        transactions = query.limit(500).all()
        headers = ["Transaction ID", "Customer ID", "Amount", "Date", "Location", "Merchant"]
        for t in transactions:
            data.append([t.transaction_id, str(t.customer_id), f"{t.amount:.2f}", str(t.date_time), t.location, t.merchant])
            
    elif report_type == "fraud":
        query = db.query(Transaction).join(FraudPrediction).filter(FraudPrediction.prediction == "FRAUDULENT")
        if risk_level:
            query = query.filter(FraudPrediction.risk_level == risk_level)
        transactions = query.limit(500).all()
        headers = ["Transaction ID", "Customer ID", "Amount", "Risk Score", "Risk Level", "Date"]
        for t in transactions:
            data.append([t.transaction_id, str(t.customer_id), f"{t.amount:.2f}", f"{t.prediction.risk_score:.2f}", t.prediction.risk_level, str(t.date_time)])
            
    elif report_type == "investigation":
        query = db.query(InvestigationCase)
        if status:
            query = query.filter(InvestigationCase.status == status)
        cases = query.limit(500).all()
        headers = ["Case ID", "Transaction ID", "Status", "Priority", "Decision", "Created At"]
        for c in cases:
            data.append([c.case_id, str(c.transaction_id), c.status, c.priority, c.decision or "N/A", str(c.created_at)])
            
    elif report_type == "audit":
        query = db.query(AuditLog)
        logs = query.order_by(AuditLog.timestamp.desc()).limit(500).all()
        headers = ["Timestamp", "User ID", "Role", "Action", "Resource", "Status", "IP Address"]
        for log in logs:
            data.append([str(log.timestamp), str(log.user_id), log.role, log.action, log.resource, log.status, log.ip_address])
            
    else:
        # Generic fallback
        headers = ["Data"]
        data = [["Report type not fully implemented in demo data."]]
        
    # --- Generate Output ---
    filename = f"{report_type}_report_{datetime.utcnow().strftime('%Y%md%H%M')}.{format}"
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(data)
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]), 
            media_type="text/csv", 
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    elif format == "pdf":
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, title)
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        y_pos = height - 100
        
        # Table Header
        c.setFont("Helvetica-Bold", 8)
        x_offsets = [50 + (i * ( (width - 100) / len(headers) )) for i in range(len(headers))]
        for i, header in enumerate(headers):
            c.drawString(x_offsets[i], y_pos, str(header)[:15])
        
        y_pos -= 15
        
        # Table Data
        c.setFont("Helvetica", 8)
        for row in data:
            if y_pos < 50:
                c.showPage()
                c.setFont("Helvetica", 8)
                y_pos = height - 50
                
            for i, cell in enumerate(row):
                c.drawString(x_offsets[i], y_pos, str(cell)[:20])
            y_pos -= 15
            
        c.save()
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
