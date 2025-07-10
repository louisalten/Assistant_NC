# backend/document_generator.py

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
import json
from typing import Dict, Any

def generate_nc_pdf(nc_data: Dict[Any, Any]) -> BytesIO:
    """
    Génère un PDF professionnel pour une non-conformité
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#23395d')
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#2ecc71')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        textColor=colors.black
    )
    
    # Contenu du document
    story = []
    
    # Titre principal
    nc_ref = "Non renseignée"
    nc_id = nc_data.get('id', 'N/A')
    if nc_data.get('d0_initialisation') and isinstance(nc_data['d0_initialisation'], dict):
        nc_ref = nc_data['d0_initialisation'].get('referenceNC', nc_ref)
    elif nc_data.get('d0_initialisation') and isinstance(nc_data['d0_initialisation'], str):
        try:
            d0_data = json.loads(nc_data['d0_initialisation'])
            nc_ref = d0_data.get('referenceNC', nc_ref)
        except:
            pass
    
    story.append(Paragraph(f"Rapport de Non-Conformité #{nc_id}", title_style))
    story.append(Paragraph(f"Référence : {nc_ref}", normal_style))
    story.append(Spacer(1, 20))
    
    # Informations générales
    story.append(Paragraph("📋 Informations Générales", section_style))
    
    general_data = [
        ["Statut", nc_data.get('statut', 'Non défini')],
        ["Date de création", nc_data.get('date_creation', 'Non définie')],
        ["Date de résolution", nc_data.get('date_resolution', 'Non résolue')],
    ]
    
    general_table = Table(general_data)
    general_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
    ]))
    
    story.append(general_table)
    story.append(Spacer(1, 20))
    
    # Sections D0 à D8
    sections = [
        ('d0_initialisation', '🎯 D0 - Initialisation', [
            ('referenceNC', 'Référence NC'),
            ('dateDetection', 'Date de détection'),
            ('produitRef', 'Produit/Référence'),
            ('LieuDetection', 'Lieu de détection'),
            ('detectePar', 'Détecté par'),
            ('descriptionInitiale', 'Description initiale'),
            ('Criticite', 'Criticité'),
            ('FonctionCrea', 'Fonction créateur')
        ]),
        ('d1_team', '👥 D1 - Équipe', [
            ('chefEquipe', 'Chef d\'équipe'),
            ('Sponsor', 'Sponsor')
        ]),
        ('d2_problem', '🔍 D2 - Description du Problème', [
            ('descriptionDetaillee', 'Description détaillée (QQOQCCP)')
        ]),
        ('d3_containment', '🛡️ D3 - Actions de Sécurisation', [
            ('actions3D', 'Actions curatives immédiates')
        ]),
        ('d4_rootcause', '🎯 D4 - Analyse des Causes Racines', [
            ('causesRacinesIdentifiees', 'Causes racines identifiées'),
            ('verificationCauses', 'Vérification des causes')
        ]),
        ('d5_correctiveactions', '⚡ D5 - Actions Correctives', [
            ('actionsCorrectives', 'Actions correctives définies')
        ]),
        ('d6_implementvalidate', '✅ D6 - Implémentation et Validation', [
            ('actionsImplantation', 'Plan d\'implantation'),
            ('resultatsValidation', 'Résultats de validation')
        ]),
        ('d7_preventrecurrence', '🔒 D7 - Prévention de la Récurrence', [
            ('actionsPreventives', 'Actions préventives'),
            ('systemesAmeliorees', 'Systèmes améliorés')
        ]),
        ('d8_congratulate', '🎉 D8 - Reconnaissance de l\'Équipe', [
            ('resumeResultats', 'Résumé des résultats'),
            ('leconsApprises', 'Leçons apprises'),
            ('dateCloture', 'Date de clôture'),
            ('teamRecognitionMessage', 'Message de reconnaissance')
        ])
    ]
    
    for section_key, section_title, fields in sections:
        section_data = nc_data.get(section_key)
        
        # Parser JSON si nécessaire
        if isinstance(section_data, str):
            try:
                section_data = json.loads(section_data)
            except:
                section_data = {}
        
        if not section_data:
            section_data = {}
        
        # Vérifier s'il y a des données dans cette section
        has_data = any(section_data.get(field_key) for field_key, _ in fields)
        
        if has_data:
            story.append(Paragraph(section_title, section_style))
            
            section_table_data = []
            for field_key, field_label in fields:
                value = section_data.get(field_key, 'Non renseigné')
                
                # Formatage spécial pour les objets complexes
                if isinstance(value, dict):
                    if field_key == 'chefEquipe':
                        value = f"{value.get('prenom', '')} {value.get('nom', '')} ({value.get('support', '')})"
                    elif field_key == 'descriptionDetaillee':
                        # QQOQCCP
                        qqoqccp_parts = []
                        for q_key, q_value in value.items():
                            if q_value:
                                qqoqccp_parts.append(f"{q_key}: {q_value}")
                        value = "; ".join(qqoqccp_parts) if qqoqccp_parts else "Non renseigné"
                    else:
                        value = str(value)
                elif isinstance(value, list):
                    if value:
                        value = "; ".join([str(item) for item in value])
                    else:
                        value = "Non renseigné"
                elif not value:
                    value = "Non renseigné"
                
                section_table_data.append([field_label, str(value)])
            
            if section_table_data:
                section_table = Table(section_table_data, colWidths=[2*inch, 4*inch])
                section_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                
                story.append(section_table)
                story.append(Spacer(1, 15))
    
    # Pied de page avec informations de génération
    story.append(Spacer(1, 30))
    story.append(Paragraph("─" * 80, normal_style))
    story.append(Paragraph(f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 
                          ParagraphStyle('FooterStyle', parent=normal_style, fontSize=8, textColor=colors.grey)))
    
    # Construire le PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_nc_summary_html(nc_data: Dict[Any, Any]) -> str:
    """
    Génère un résumé HTML formaté pour affichage rapide
    """
    nc_id = nc_data.get('id', 'N/A')
    nc_ref = "Non renseignée"
    description = "Non renseignée"
    
    # Extraire les informations de base
    if nc_data.get('d0_initialisation'):
        d0_data = nc_data['d0_initialisation']
        if isinstance(d0_data, str):
            try:
                d0_data = json.loads(d0_data)
            except:
                d0_data = {}
        
        nc_ref = d0_data.get('referenceNC', nc_ref)
        description = d0_data.get('descriptionInitiale', description)
    
    html = f"""
    <div style='background: white; padding: 16px; border-radius: 8px; border-left: 4px solid #2ecc71; margin: 8px 0;'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
            <span style='background: #2ecc71; color: white; padding: 4px 12px; border-radius: 16px; font-size: 0.9em; font-weight: bold;'>
                NC #{nc_id}
            </span>
            <span style='color: #666; font-size: 0.8em;'>
                Référence: {nc_ref}
            </span>
        </div>
        <div style='color: #333; line-height: 1.4; margin-bottom: 12px;'>
            <strong>Description:</strong> {description[:200]}{'...' if len(description) > 200 else ''}
        </div>
        <div style='color: #666; font-size: 0.8em;'>
            Statut: {nc_data.get('statut', 'Non défini')} | 
            Créé le: {nc_data.get('date_creation', 'Non défini')}
        </div>
    </div>
    """
    
    return html


def generate_source_pdf(source_data: Dict) -> BytesIO:
    """
    Génère un PDF simple pour une source de non-conformité
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#23395d')
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#2ecc71')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        textColor=colors.black
    )
    
    # Contenu du document
    story = []
    
    # Titre principal
    nc_id = source_data.get('nc_id', 'Non spécifié')
    story.append(Paragraph(f"Non-Conformité {nc_id}", title_style))
    story.append(Spacer(1, 20))
    
    # Informations générales
    story.append(Paragraph("📋 Informations sur la Source", section_style))
    
    # Récupérer les métadonnées
    metadata = source_data.get('metadata', {})
    content = source_data.get('content', 'Aucun contenu disponible')
    
    # Créer une liste de données pour le tableau
    general_data = []
    for key, value in metadata.items():
        if value and str(value).strip():
            general_data.append([key, str(value)])
    
    # Si des métadonnées sont disponibles, afficher un tableau
    if general_data:
        general_table = Table(general_data, colWidths=[2*inch, 3.5*inch])
        general_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        story.append(general_table)
    else:
        story.append(Paragraph("Aucune métadonnée disponible", normal_style))
    
    story.append(Spacer(1, 20))
    
    # Contenu de la source
    story.append(Paragraph("📝 Contenu", section_style))
    story.append(Paragraph(content, normal_style))
    
    # Génération du document
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_source_html_summary(source_data: Dict) -> str:
    """
    Génère un résumé HTML simple pour une source de non-conformité
    """
    nc_id = source_data.get('nc_id', 'Non spécifié')
    metadata = source_data.get('metadata', {})
    content = source_data.get('content', 'Aucun contenu disponible')
    
    # Construire le HTML
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #23395d; text-align: center; margin-bottom: 30px;">Non-Conformité {nc_id}</h1>
        
        <div style="background: #f8f9fa; border-left: 4px solid #2ecc71; padding: 15px; margin: 20px 0;">
            <h2 style="color: #2ecc71; margin-top: 0;">📋 Informations sur la Source</h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
    """
    
    # Ajouter les métadonnées
    if metadata:
        for key, value in metadata.items():
            if value and str(value).strip():
                html += f"""
                <tr>
                    <th style="text-align: left; padding: 8px; background-color: #f1f1f1; width: 30%;">{key}</th>
                    <td style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">{value}</td>
                </tr>
                """
    else:
        html += """
            <tr><td colspan="2" style="text-align: center; padding: 8px;">Aucune métadonnée disponible</td></tr>
        """
    
    html += """
            </table>
        </div>
        
        <div style="background: #f8f9fa; border-left: 4px solid #2ecc71; padding: 15px; margin: 20px 0;">
            <h2 style="color: #2ecc71; margin-top: 0;">📝 Contenu</h2>
            <div style="white-space: pre-wrap; font-family: monospace; background: white; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
    """
    
    # Ajouter le contenu formaté pour éviter les problèmes HTML
    html += content.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
    
    html += """
            </div>
        </div>
    </div>
    """
    
    return html
