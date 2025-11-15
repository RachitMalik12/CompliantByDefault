from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from pathlib import Path
from typing import Dict
import json

from ..utils.logger import logger


class PDFReportGenerator:
    """Generate PDF reports from JSON report data."""
    
    def __init__(self, output_dir: str = "./reports"):
        """
        Initialize PDF generator.
        
        Args:
            output_dir: Directory to save PDF reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section Header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#374151'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Score style
        self.styles.add(ParagraphStyle(
            name='ScoreText',
            parent=self.styles['Normal'],
            fontSize=48,
            textColor=colors.HexColor('#2563EB'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def generate_pdf(self, job_id: str, report_data: Dict) -> Path:
        """
        Generate PDF report from report data.
        
        Args:
            job_id: Report job ID
            report_data: Complete report data dictionary
            
        Returns:
            Path to generated PDF file
        """
        logger.info(f"Generating PDF report for job {job_id}")
        
        pdf_path = self.output_dir / f"{job_id}_report.pdf"
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        story = []
        
        # Add content
        story.extend(self._create_cover_page(report_data))
        story.append(PageBreak())
        story.extend(self._create_executive_summary(report_data))
        story.append(PageBreak())
        story.extend(self._create_control_coverage(report_data))
        story.append(PageBreak())
        story.extend(self._create_recommendations(report_data))
        story.append(PageBreak())
        story.extend(self._create_findings_details(report_data))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"PDF report generated: {pdf_path}")
        return pdf_path
    
    def _create_cover_page(self, report_data: Dict) -> list:
        """Create cover page content."""
        story = []
        
        # Title
        story.append(Spacer(1, 1.5*inch))
        story.append(Paragraph("SOC 2 Compliance Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Score
        summary = report_data.get('summary', {})
        score = summary.get('readiness_score', 0)
        grade = summary.get('grade', 'N/A')
        
        story.append(Paragraph(f"{score}/100", self.styles['ScoreText']))
        story.append(Paragraph(f"Grade: {grade}", self.styles['Heading2']))
        story.append(Spacer(1, 0.5*inch))
        
        # Metadata
        metadata = report_data.get('metadata', {})
        meta_data = [
            ['Report ID:', report_data.get('id', 'N/A')],
            ['Repository:', metadata.get('repository', 'N/A')],
            ['Scan Type:', metadata.get('scan_type', 'N/A').upper()],
            ['Generated:', datetime.fromisoformat(report_data.get('generated_at', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M:%S')],
        ]
        
        meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(meta_table)
        
        return story
    
    def _create_executive_summary(self, report_data: Dict) -> list:
        """Create executive summary section."""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        summary = report_data.get('summary', {})
        score_data = report_data.get('score', {})
        
        # Summary stats
        stats_data = [
            ['Total Findings', str(summary.get('total_findings', 0))],
            ['Risk Level', summary.get('risk_level', 'Unknown')],
            ['Controls Compliant', f"{score_data.get('controls_compliant', 0)}/{score_data.get('controls_total', 0)}"],
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F4F6')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D1D5DB')),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Severity distribution
        story.append(Paragraph("Severity Distribution", self.styles['SectionHeader']))
        severity_impact = score_data.get('severity_impact', {})
        severity_counts = severity_impact.get('counts', {})
        
        severity_data = [['Severity', 'Count']]
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                severity_data.append([severity.upper(), str(count)])
        
        if len(severity_data) > 1:
            severity_table = Table(severity_data, colWidths=[3*inch, 3*inch])
            severity_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D1D5DB')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
            ]))
            story.append(severity_table)
        
        return story
    
    def _create_control_coverage(self, report_data: Dict) -> list:
        """Create SOC 2 control coverage section."""
        story = []
        
        story.append(Paragraph("SOC 2 Control Coverage", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        controls = report_data.get('controls', {})
        
        # Create table data
        table_data = [['Control ID', 'Name', 'Status', 'Score', 'Findings']]
        
        for control_id, control_info in sorted(controls.items()):
            status = control_info.get('status', 'unknown')
            status_symbol = {
                'compliant': '✓',
                'partial': '⚠',
                'non_compliant': '✗',
                'unknown': '?'
            }.get(status, '?')
            
            table_data.append([
                control_id,
                control_info.get('name', '')[:40] + '...' if len(control_info.get('name', '')) > 40 else control_info.get('name', ''),
                status_symbol + ' ' + status,
                str(control_info.get('score', 0)),
                str(control_info.get('findings_count', 0))
            ])
        
        if len(table_data) > 1:
            control_table = Table(table_data, colWidths=[1*inch, 2.5*inch, 1.2*inch, 0.8*inch, 0.8*inch])
            control_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 0), (4, -1), 'CENTER'),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
            ]))
            story.append(control_table)
        
        return story
    
    def _create_recommendations(self, report_data: Dict) -> list:
        """Create recommendations section."""
        story = []
        
        story.append(Paragraph("Top Recommendations", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        recommendations = report_data.get('recommendations', [])
        
        for i, rec in enumerate(recommendations[:10], 1):
            priority = rec.get('priority', 'medium')
            priority_color = {
                'critical': colors.HexColor('#DC2626'),
                'high': colors.HexColor('#F59E0B'),
                'medium': colors.HexColor('#10B981'),
                'low': colors.HexColor('#6B7280')
            }.get(priority, colors.gray)
            
            # Recommendation header
            header_style = ParagraphStyle(
                'RecHeader',
                parent=self.styles['Normal'],
                fontSize=12,
                fontName='Helvetica-Bold',
                textColor=priority_color,
                spaceAfter=4
            )
            story.append(Paragraph(f"{i}. [{priority.upper()}] {rec.get('issue', 'Issue')}", header_style))
            
            # Recommendation details
            story.append(Paragraph(f"<b>Control:</b> {rec.get('control', 'N/A')}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Action:</b> {rec.get('action', 'Review and remediate')}", self.styles['Normal']))
            story.append(Paragraph(f"<b>File:</b> {rec.get('file', 'N/A')}", self.styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
        
        return story
    
    def _create_findings_details(self, report_data: Dict) -> list:
        """Create detailed findings section."""
        story = []
        
        story.append(Paragraph("Detailed Findings", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        findings = report_data.get('findings', [])
        
        # Group by severity
        findings_by_severity = {}
        for finding in findings:
            severity = finding.get('severity', 'info')
            if severity not in findings_by_severity:
                findings_by_severity[severity] = []
            findings_by_severity[severity].append(finding)
        
        # Display findings by severity
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            if severity in findings_by_severity:
                story.append(Paragraph(f"{severity.upper()} Severity Findings", self.styles['SectionHeader']))
                
                for finding in findings_by_severity[severity][:20]:  # Limit to 20 per severity
                    finding_text = f"""
                    <b>Type:</b> {finding.get('type', 'Unknown').replace('_', ' ').title()}<br/>
                    <b>File:</b> {finding.get('file', 'N/A')}<br/>
                    <b>Line:</b> {finding.get('line', 'N/A')}<br/>
                    <b>Control:</b> {finding.get('control', 'N/A')}<br/>
                    <b>Message:</b> {finding.get('message', 'No message')}<br/>
                    """
                    
                    if finding.get('recommendation'):
                        finding_text += f"<b>Recommendation:</b> {finding.get('recommendation')}<br/>"
                    
                    story.append(Paragraph(finding_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
        
        return story


def generate_pdf_report(job_id: str, report_data: Dict) -> Path:
    """
    Helper function to generate PDF report.
    
    Args:
        job_id: Report job ID
        report_data: Report data dictionary
        
    Returns:
        Path to generated PDF
    """
    generator = PDFReportGenerator()
    return generator.generate_pdf(job_id, report_data)
