#!/usr/bin/env python3
"""
Script para crear datos de prueba para la aplicación Campaigns
Ejecutar con: docker-compose exec backend python create_campaigns_data.py
"""

import os
import sys
import django
from datetime import date, timedelta
import random

# Configurar Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import models
from campaigns.models import Campaign, CampaignTouchpoint
from world.models import Industry, MarketSegment, FunctionOrResponsibility, Tag
from our_institution.models import Division, Team
from interactions.models import Channel, Touchpoint

def create_campaigns_data():
    """Crear datos de prueba para campaigns"""
    
    print("🎯 Creando datos de prueba para Campaigns...")
    
    # Verificar si ya existen datos
    if Campaign.objects.count() > 0:
        print("⚠️  Ya existen campañas. Saltando creación de datos.")
        return
    
    # Obtener datos base requeridos
    try:
        division = Division.objects.first()
        team = Team.objects.first()
        
        if not division or not team:
            print("❌ Error: Se requieren divisiones y equipos. Ejecutar create_organization_structure primero.")
            return
            
    except Exception as e:
        print(f"❌ Error al obtener datos organizacionales: {e}")
        return
    
    # Datos de campañas de ejemplo
    campaigns_data = [
        {
            'name': 'Black Friday 2024',
            'code': 'BF2024',
            'description': 'Campaña promocional especial Black Friday con descuentos en productos seleccionados',
            'content_type': 'product',
            'funnel_stage': 'do',
            'budget': 45000.00,
            'days_ago': 15,
            'duration': 60
        },
        {
            'name': 'Brand Awareness Q1 2025',
            'code': 'BA-Q1-2025',
            'description': 'Campaña de posicionamiento de marca para el primer trimestre del año',
            'content_type': 'brand',
            'funnel_stage': 'see',
            'budget': 25000.00,
            'days_ago': 30,
            'duration': 90
        },
        {
            'name': 'Lead Generation MBA Executive',
            'code': 'LG-MBA-EXEC',
            'description': 'Campaña especializada para captura de leads interesados en programas MBA',
            'content_type': 'product',
            'funnel_stage': 'think',
            'budget': 30000.00,
            'days_ago': 5,
            'duration': 120
        },
        {
            'name': 'Customer Retention Program',
            'code': 'CR-PROG-2024',
            'description': 'Programa de retención y fidelización de clientes actuales',
            'content_type': 'affinity',
            'funnel_stage': 'care',
            'budget': 20000.00,
            'days_ago': 45,
            'duration': 180
        },
        {
            'name': 'Digital Marketing Categories',
            'code': 'DM-CAT-2025',
            'description': 'Campaña integral de marketing digital por categorías de productos',
            'content_type': 'category',
            'funnel_stage': 'any',
            'budget': 35000.00,
            'days_ago': 10,
            'duration': 75
        }
    ]
    
    # Crear campañas
    created_campaigns = []
    
    for data in campaigns_data:
        try:
            start_date = date.today() - timedelta(days=data['days_ago'])
            end_date = start_date + timedelta(days=data['duration'])
            
            campaign = Campaign.objects.create(
                name=data['name'],
                code=data['code'],
                description=data['description'],
                start_date=start_date,
                end_date=end_date,
                budget=data['budget'],
                content_type=data['content_type'],
                funnel_stage=data['funnel_stage'],
                division=division,
                team=team,
                is_active=True
            )
            
            created_campaigns.append(campaign)
            print(f"✅ Campaña creada: {campaign.name}")
            
        except Exception as e:
            print(f"❌ Error creando campaña {data['name']}: {e}")
    
    # Asignar relaciones semánticas
    print("\n🔗 Asignando relaciones semánticas...")
    
    # Canales
    if Channel.objects.exists():
        channels = list(Channel.objects.all())
        for campaign in created_campaigns:
            selected_channels = random.sample(channels, min(random.randint(1, 3), len(channels)))
            campaign.channels.set(selected_channels)
            print(f"   📡 {campaign.name}: {len(selected_channels)} canales asignados")
    
    # Industrias
    if Industry.objects.exists():
        industries = list(Industry.objects.all())
        for campaign in created_campaigns:
            selected_industries = random.sample(industries, min(random.randint(1, 2), len(industries)))
            campaign.related_industries.set(selected_industries)
            print(f"   🏭 {campaign.name}: {len(selected_industries)} industrias asignadas")
    
    # Segmentos de mercado
    if MarketSegment.objects.exists():
        segments = list(MarketSegment.objects.all())
        for campaign in created_campaigns:
            selected_segments = random.sample(segments, min(random.randint(1, 2), len(segments)))
            campaign.target_segments.set(selected_segments)
            print(f"   🎯 {campaign.name}: {len(selected_segments)} segmentos asignados")
    
    # Funciones
    if FunctionOrResponsibility.objects.exists():
        functions = list(FunctionOrResponsibility.objects.all())
        for campaign in created_campaigns:
            selected_functions = random.sample(functions, min(random.randint(0, 2), len(functions)))
            campaign.related_functions.set(selected_functions)
            print(f"   👔 {campaign.name}: {len(selected_functions)} funciones asignadas")
    
    # Tags
    if Tag.objects.exists():
        tags = list(Tag.objects.all())
        for campaign in created_campaigns:
            selected_tags = random.sample(tags, min(random.randint(0, 3), len(tags)))
            campaign.tags.set(selected_tags)
            print(f"   🏷️ {campaign.name}: {len(selected_tags)} tags asignados")
    
    # Crear relaciones con touchpoints
    print("\n📍 Creando relaciones campaña-touchpoint...")
    
    if Touchpoint.objects.exists():
        touchpoints = list(Touchpoint.objects.all())
        
        for campaign in created_campaigns:
            # Seleccionar 2-4 touchpoints por campaña
            num_touchpoints = random.randint(2, min(4, len(touchpoints)))
            selected_touchpoints = random.sample(touchpoints, num_touchpoints)
            
            for i, touchpoint in enumerate(selected_touchpoints):
                try:
                    # Distribuir presupuesto entre touchpoints
                    base_budget = float(campaign.budget) / num_touchpoints
                    variation = random.uniform(0.5, 1.5)
                    allocated_budget = base_budget * variation
                    
                    CampaignTouchpoint.objects.create(
                        campaign=campaign,
                        touchpoint=touchpoint,
                        weight=round(random.uniform(1.0, 5.0), 1),
                        priority=random.randint(1, 3),
                        expected_conversions=random.randint(20, 150),
                        budget_allocated=round(allocated_budget, 2)
                    )
                    
                except Exception as e:
                    print(f"   ⚠️ Error asignando touchpoint {touchpoint.name} a {campaign.name}: {e}")
            
            print(f"   ✅ {campaign.name}: {num_touchpoints} touchpoints asignados")
    
    # Crear una subcampaña de ejemplo
    print("\n🏗️ Creando estructura jerárquica...")
    
    if created_campaigns:
        parent_campaign = created_campaigns[0]  # Black Friday como padre
        
        subcampaigns_data = [
            {
                'name': 'Black Friday - Email Marketing',
                'code': 'BF2024-EMAIL',
                'description': 'Subcampaña de email marketing para Black Friday',
                'funnel_stage': 'think'
            },
            {
                'name': 'Black Friday - Social Media',
                'code': 'BF2024-SOCIAL',
                'description': 'Subcampaña de redes sociales para Black Friday',
                'funnel_stage': 'see'
            }
        ]
        
        for sub_data in subcampaigns_data:
            try:
                subcampaign = Campaign.objects.create(
                    name=sub_data['name'],
                    code=sub_data['code'],
                    description=sub_data['description'],
                    start_date=parent_campaign.start_date,
                    end_date=parent_campaign.end_date,
                    budget=parent_campaign.budget * 0.3,  # 30% del presupuesto padre
                    content_type=parent_campaign.content_type,
                    funnel_stage=sub_data['funnel_stage'],
                    division=parent_campaign.division,
                    team=parent_campaign.team,
                    parent=parent_campaign,
                    is_active=True
                )
                
                print(f"   ✅ Subcampaña creada: {subcampaign.name}")
                
            except Exception as e:
                print(f"   ❌ Error creando subcampaña {sub_data['name']}: {e}")
    
    # Estadísticas finales
    print(f"\n📊 Resumen de creación:")
    print(f"   Total campañas: {Campaign.objects.count()}")
    print(f"   Campañas padre: {Campaign.objects.filter(parent__isnull=True).count()}")
    print(f"   Subcampañas: {Campaign.objects.filter(parent__isnull=False).count()}")
    print(f"   Relaciones campaña-touchpoint: {CampaignTouchpoint.objects.count()}")
    print(f"   Presupuesto total: ${Campaign.objects.aggregate(total=models.Sum('budget'))['total']:,.2f}")
    
    print("\n🎉 Datos de campañas creados exitosamente!")
    print("\n📋 Endpoints disponibles:")
    print("   GET /api/campaigns/campaigns/")
    print("   GET /api/campaigns/campaigns/analytics/")
    print("   GET /api/campaigns/campaigns/active_now/")
    print("   GET /api/campaigns/campaign-touchpoints/")

if __name__ == "__main__":
    create_campaigns_data()
