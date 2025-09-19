"""
Este módulo está descontinuado. As funcionalidades foram refatoradas e movidas para:
- app.services.document_processor
- app.services.vector_store
- app.services.query_service
"""

from app.services.document_processor import process_pdf_and_store
from app.services.query_service import (
    query_legal_document,
    query_legal_document_self_query
)

# Mantendo os imports para compatibilidade com código existente
__all__ = ['process_pdf_and_store', 'query_legal_document', 'query_legal_document_self_query']
