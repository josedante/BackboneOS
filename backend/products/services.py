from __future__ import annotations

from .models import Product


def duplicate_product(product: Product) -> Product:
    """Create a deep copy of a product, including all M2M relationships."""
    new_product = Product.objects.get(pk=product.pk)
    new_product.pk = None
    new_product.name = f"{product.name} (Copia)"
    new_product.code = f"{product.code}_COPY_{product.id}"
    new_product.save()

    new_product.included_products.set(product.included_products.all())
    new_product.modalities.set(product.modalities.all())
    new_product.target_segments.set(product.target_segments.all())
    new_product.related_industries.set(product.related_industries.all())
    new_product.related_functions.set(product.related_functions.all())
    new_product.related_skills.set(product.related_skills.all())
    new_product.descriptors.set(product.descriptors.all())
    new_product.tags.set(product.tags.all())

    return new_product
