"""
Sales-specific touchpoint resolution.

This module provides sales-specific touchpoint resolvers that understand
sales context, division-based channels, and sales-specific touchpoint logic.
"""

from typing import Optional, TYPE_CHECKING

from connectors.resolvers import DefaultTouchpointResolver
from connectors.protocols import TouchpointHint, TouchpointInferenceProtocol

if TYPE_CHECKING:
    from .models import SalesSession, SalesOpportunity, ProductAcquisition


class SalesTouchpointResolver(DefaultTouchpointResolver):
    """
    Sales-specific touchpoint resolver with division-based channels and sales context.
    
    This resolver extends the generic DefaultTouchpointResolver with sales-specific
    logic for handling division-based sales channels, opportunity context, and
    sales-specific touchpoint creation patterns.
    """
    
    def _get_connector_type(self, subject: TouchpointInferenceProtocol) -> str:
        """Get connector type for sales interactions."""
        return 'sales'
    
    def _ensure_required_fields(self, subject: TouchpointInferenceProtocol, hint: TouchpointHint) -> TouchpointHint:
        """
        Ensure sales-specific required fields with division-based channels.
        
        This method provides sales-specific defaults and ensures division-based
        channel resolution for proper sales team attribution.
        
        Args:
            subject: The sales interaction requesting touchpoint resolution
            hint: The touchpoint hint from the connector's inference
            
        Returns:
            TouchpointHint: The hint with sales-specific required fields ensured
        """
        # Ensure channel code is set with division-specific logic
        if not hint.channel_code or hint.channel_code == "sales":
            hint = TouchpointHint(
                code=hint.code,
                channel_code=self._get_division_specific_channel(subject),
                medium_code=hint.medium_code,
                label=hint.label,
                metadata=hint.metadata
            )
        
        # Ensure medium code is set
        if not hint.medium_code:
            hint = TouchpointHint(
                code=hint.code,
                channel_code=hint.channel_code,
                medium_code='sales_contact',
                label=hint.label,
                metadata=hint.metadata
            )
        
        # Ensure label is set with sales context
        if not hint.label:
            hint = TouchpointHint(
                code=hint.code,
                channel_code=hint.channel_code,
                medium_code=hint.medium_code,
                label=self._generate_sales_label(subject, hint),
                metadata=hint.metadata
            )
        
        return hint
    
    def _get_division_specific_channel(self, subject: TouchpointInferenceProtocol) -> str:
        """
        Get division-specific sales channel code.
        
        Priority order:
        1. Representative's division (highest priority)
        2. Product's division (fallback)
        3. Default sales channel (lowest priority)
        
        Args:
            subject: The sales interaction
            
        Returns:
            str: Division-specific channel code
        """
        # Priority 1: Representative's division (highest priority)
        representative_division = self._get_representative_division(subject)
        if representative_division:
            return f"sales_{representative_division.code.lower()}"
        
        # Priority 2: Product's division (fallback)
        product_division = self._get_product_division(subject)
        if product_division:
            return f"sales_{product_division.code.lower()}"
        
        # Priority 3: Default fallback
        return "sales"
    
    def _get_representative_division(self, subject: TouchpointInferenceProtocol):
        """
        Get the division that the sales representative works for.
        
        The representative is a human User. AI agents are handled as whole touchpoints.
        
        Args:
            subject: The sales interaction
            
        Returns:
            Division or None: The representative's division
        """
        # Check if subject has a representative
        if not hasattr(subject, 'representative') or not subject.representative:
            return None
        
        representative = subject.representative
        
        # Handle human User representatives
        if hasattr(representative, 'position') or hasattr(representative, 'division'):
            return self._get_human_representative_division(representative)
        
        return None
    
    
    def _get_human_representative_division(self, human_representative):
        """
        Get the division for a human representative.
        
        Args:
            human_representative: The User instance
            
        Returns:
            Division or None: The human representative's division
        """
        # Try to get division from representative's position/unit
        try:
            if hasattr(human_representative, 'position') and human_representative.position:
                position = human_representative.position
                if hasattr(position, 'unit') and position.unit:
                    return position.unit.division
        except AttributeError:
            pass
        
        # Alternative: Check if representative has a direct division assignment
        try:
            if hasattr(human_representative, 'division') and human_representative.division:
                return human_representative.division
        except AttributeError:
            pass
        
        # Alternative: Check if representative has a team with a division
        try:
            if hasattr(human_representative, 'team') and human_representative.team:
                if hasattr(human_representative.team, 'division') and human_representative.team.division:
                    return human_representative.team.division
        except AttributeError:
            pass
        
        return None
    
    def _get_product_division(self, subject: TouchpointInferenceProtocol):
        """
        Get the division associated with the product being sold.
        
        Args:
            subject: The sales interaction
            
        Returns:
            Division or None: The product's division
        """
        # For SalesSession, get division from opportunity -> product -> category
        if hasattr(subject, 'opportunity') and subject.opportunity:
            if (subject.opportunity.product and 
                subject.opportunity.product.category and 
                subject.opportunity.product.category.division):
                return subject.opportunity.product.category.division
        
        # For ProductAcquisition, get division from offering -> product -> category
        if hasattr(subject, 'offering') and subject.offering:
            if (subject.offering.product and 
                subject.offering.product.category and 
                subject.offering.product.category.division):
                return subject.offering.product.category.division
        
        return None
    
    def _generate_sales_label(self, subject: TouchpointInferenceProtocol, hint: TouchpointHint) -> str:
        """
        Generate sales-specific label based on context.
        
        Args:
            subject: The sales interaction
            hint: The current hint
            
        Returns:
            str: Generated label
        """
        medium_label = self._get_medium_display_name(hint.medium_code)
        
        # Add context based on interaction type
        if hasattr(subject, 'opportunity') and subject.opportunity:
            return f"Sesión de ventas vía {medium_label}"
        elif hasattr(subject, 'offering') and subject.offering:
            return f"Adquisición de producto vía {medium_label}"
        else:
            return f"Interacción de ventas vía {medium_label}"
    
    def _get_medium_display_name(self, medium_code: str) -> str:
        """Get display name for medium code."""
        medium_names = {
            'email': 'Correo electrónico',
            'phone': 'Teléfono',
            'video': 'Video llamada',
            'whatsapp': 'WhatsApp',
            'sms': 'Mensaje de texto',
            'in_person': 'Presencial',
            'other': 'Otro medio',
            'unknown': 'Desconocido',
            'sales_contact': 'Contacto comercial',
        }
        return medium_names.get(medium_code, medium_code.title())
    
    def _get_or_create_touchpoint(self, hint: TouchpointHint):
        """
        Create touchpoint with sales-specific defaults.
        
        Args:
            hint: The touchpoint hint
            
        Returns:
            Touchpoint: The created touchpoint
        """
        from interactions.models import Touchpoint, Channel
        
        # Ensure channel exists
        channel = self._ensure_channel_exists(hint.channel_code, hint.metadata)
        
        # Create touchpoint with sales-specific defaults
        touchpoint, created = Touchpoint.objects.get_or_create(
            code=hint.code,
            defaults={
                'name': hint.label,
                'channel': channel,
                'funnel_stage': self._get_funnel_stage_for_code(hint.code),
                'description': self._generate_sales_description(hint)
            }
        )
        
        # If touchpoint already exists but doesn't have a channel, update it
        if not created and not touchpoint.channel:
            touchpoint.channel = channel
            touchpoint.save()
        
        return touchpoint
    
    def _ensure_channel_exists(self, channel_code: str, metadata: dict = None):
        """
        Ensure sales channel exists with proper naming.
        
        Args:
            channel_code: The channel code to ensure exists
            metadata: Additional metadata that may contain division information
            
        Returns:
            Channel: The channel instance
        """
        from interactions.models import Channel
        
        # Generate channel name based on metadata or code
        if channel_code.startswith('sales_') and metadata and 'division' in metadata:
            # Use actual division name from metadata
            division_name = metadata['division']
            channel_name = f"Ventas - {division_name}"
        elif channel_code.startswith('sales_'):
            # Fallback: derive name from code
            division_name = channel_code.replace('sales_', '').replace('_', ' ').title()
            channel_name = f"Ventas - {division_name}"
        else:
            channel_name = "Ventas"
        
        channel, created = Channel.objects.get_or_create(
            code=channel_code,
            defaults={
                'name': channel_name,
                'description': f"Canal de ventas para {channel_name.replace('Ventas - ', '')}"
            }
        )
        
        return channel
    
    def _get_funnel_stage_for_code(self, code: str) -> str:
        """
        Get appropriate funnel stage for touchpoint code.
        
        Args:
            code: The touchpoint code
            
        Returns:
            str: Funnel stage
        """
        if 'session' in code:
            return 'engage'  # Sales sessions are engagement
        elif 'acquisition' in code:
            return 'do'      # Product acquisitions are decision/action
        elif 'opportunity' in code:
            return 'think'   # Opportunities are consideration
        else:
            return 'engage'  # Default to engagement
    
    def _generate_sales_description(self, hint: TouchpointHint) -> str:
        """
        Generate sales-specific description.
        
        Args:
            hint: The touchpoint hint
            
        Returns:
            str: Generated description
        """
        descriptions = {
            'sales.session.email': 'Sesión de ventas realizada por correo electrónico',
            'sales.session.phone': 'Sesión de ventas realizada por teléfono',
            'sales.session.video': 'Sesión de ventas realizada por video llamada',
            'sales.session.whatsapp': 'Sesión de ventas realizada por WhatsApp',
            'sales.session.sms': 'Sesión de ventas realizada por mensaje de texto',
            'sales.session.in_person': 'Sesión de ventas realizada presencialmente',
            'sales.acquisition': 'Adquisición de producto registrada',
            'sales.opportunity': 'Oportunidad de venta creada o actualizada',
        }
        
        return descriptions.get(hint.code, f"Interacción de ventas: {hint.label}")


class SalesMappingProvider:
    """
    Sales-specific mapping provider with business logic for sales touchpoints.
    
    This provider handles sales-specific mapping rules and provides defaults
    for common sales scenarios.
    """
    
    def lookup_mapping(self, subject: TouchpointInferenceProtocol, hint: TouchpointHint):
        """
        Look up sales-specific mapping rules.
        
        Args:
            subject: The sales interaction
            hint: The touchpoint hint
            
        Returns:
            TouchpointMappingRule or None: The applicable mapping rule
        """
        from connectors.models import TouchpointMappingRule
        
        # Look for specific sales mapping rules
        try:
            # Try exact match first
            rule = TouchpointMappingRule.objects.get(
                connector_type='sales',
                event_code=hint.code or '',
                is_active=True
            )
            return rule
        except TouchpointMappingRule.DoesNotExist:
            pass
        
        # Try generic sales rules
        try:
            rule = TouchpointMappingRule.objects.get(
                connector_type='sales',
                event_code=hint.code.split('.')[-1] if hint.code else '',  # Get last part
                is_active=True
            )
            return rule
        except TouchpointMappingRule.DoesNotExist:
            pass
        
        # No specific mapping found
        return None
