import os
from typing import List


def ensure_directory_exists(directory: str) -> None:
    """
    Garante que um diretório existe, criando-o se necessário.

    Esta função utiliza os.makedirs com a flag exist_ok=True para:
    - Criar o diretório se não existir
    - Não gerar erro se o diretório já existir
    - Criar diretórios intermediários se necessário (como mkdir -p)

    Args:
        directory (str): Caminho do diretório a ser verificado/criado
    """
    os.makedirs(directory, exist_ok=True)


def get_pdf_files(directory: str) -> List[str]:
    """
    Obtém uma lista de todos os arquivos PDF em um diretório.

    Esta função:
    1. Valida se o diretório existe
    2. Lista todos os arquivos do diretório
    3. Filtra apenas arquivos PDF (case-insensitive)
    4. Retorna caminhos completos dos arquivos

    Args:
        directory (str): Caminho do diretório a ser pesquisado

    Returns:
        List[str]: Lista de caminhos completos para os arquivos PDF

    Raises:
        ValueError: Se o diretório não existir ou não contiver PDFs
    """
    if not os.path.isdir(directory):
        raise ValueError(f"O caminho '{directory}' não é um diretório válido.")

    pdf_files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(".pdf")
    ]

    if not pdf_files:
        raise ValueError(f"Nenhum arquivo PDF encontrado no diretório '{directory}'.")

    return pdf_files
