import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

class PDFGenerator:
    """Generates EcoRoute AI Collection Summary and Sustainability PDF Certificates."""

    @staticmethod
    def generate_collection_report(collection_data):
        """
        Creates a PDF buffer for a waste collection report.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1B5E20'),
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#6B7280'),
            spaceAfter=15
        )
        h2_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#2E7D32'),
            spaceBefore=10,
            spaceAfter=8
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#1F2937')
        )

        elements = []

        # Header Title
        elements.append(Paragraph("EcoRoute AI – Official Waste Collection Report", title_style))
        elements.append(Paragraph("Smarter Routes. Cleaner Communities. | Verified Sustainability Document", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#43A047'), spaceAfter=15))

        # Basic Info Table
        info_data = [
            [Paragraph("<b>Society Name:</b>", body_style), Paragraph(str(collection_data.get('society_name', 'N/A')), body_style),
             Paragraph("<b>Report ID:</b>", body_style), Paragraph(f"ECR-COL-{collection_data.get('id', '1001')}", body_style)],
            [Paragraph("<b>Date & Time:</b>", body_style), Paragraph(str(collection_data.get('collected_at', 'N/A')), body_style),
             Paragraph("<b>Worker / Driver:</b>", body_style), Paragraph(str(collection_data.get('worker_name', 'N/A')), body_style)],
            [Paragraph("<b>Vehicle Number:</b>", body_style), Paragraph(str(collection_data.get('vehicle_number', 'N/A')), body_style),
             Paragraph("<b>Status:</b>", body_style), Paragraph("<font color='#2E7D32'><b>VERIFIED & COMPLETED</b></font>", body_style)]
        ]
        info_table = Table(info_data, colWidths=[110, 160, 110, 160])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F5F7F4')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 15))

        # Waste Breakdown Section
        elements.append(Paragraph("Waste Category Breakdown (kg)", h2_style))
        
        breakdown_data = [
            ['Waste Category', 'Weight (kg)', '% of Total', 'Environmental Destination'],
            ['Organic / Wet Waste', f"{collection_data.get('wet_waste_kg', 0.0):.2f} kg", "48%", "Bio-Composting Plant"],
            ['Dry & Paper Waste', f"{collection_data.get('dry_waste_kg', 0.0):.2f} kg", "28%", "Paper Recycling Mill"],
            ['Recyclable Plastic', f"{collection_data.get('recyclable_kg', 0.0):.2f} kg", "16%", "Polymer Processing Unit"],
            ['Hazardous / E-Waste', f"{collection_data.get('hazardous_kg', 0.0):.2f} kg", "8%", "Authorized Treatment Facility"],
            ['TOTAL COLLECTED', f"{collection_data.get('total_weight_kg', 0.0):.2f} kg", "100%", "Zero-Waste Landfill Diversion"]
        ]

        table_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1B5E20')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('TOPPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#81C784')),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (1,1), (2,-1), 'CENTER'),
        ])
        
        breakdown_table = Table(breakdown_data, colWidths=[150, 110, 90, 190])
        breakdown_table.setStyle(table_style)
        elements.append(breakdown_table)
        elements.append(Spacer(1, 15))

        # Carbon Savings Impact Section
        elements.append(Paragraph("AI Carbon Offset & Environmental Impact", h2_style))
        co2_saved = collection_data.get('co2_saved', collection_data.get('total_weight_kg', 0.0) * 1.85)
        trees_eq = round(co2_saved / 21.77, 1)

        impact_text = f"""
        This waste collection successfully diverted <b>{collection_data.get('total_weight_kg', 0.0):.2f} kg</b> of waste from municipal landfills, preventing approximately <b>{co2_saved:.2f} kg CO2 equivalent</b> greenhouse gas emissions. This is equivalent to planting <b>{trees_eq} mature trees</b> for a full year.
        """
        elements.append(Paragraph(impact_text, body_style))
        elements.append(Spacer(1, 20))

        # Footer Signoff
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E5E7EB'), spaceAfter=10))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=9,
            textColor=colors.HexColor('#6B7280'),
            alignment=1 # Center
        )
        elements.append(Paragraph("Generated automatically by EcoRoute AI Platform • http://ecoroute.ai", footer_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer
