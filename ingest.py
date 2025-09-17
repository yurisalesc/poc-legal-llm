import argparse
import os
import sys

from tqdm import tqdm  # type: ignore

from app.processing import process_pdf_and_store

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


def main():
    parser = argparse.ArgumentParser(
        description="Processa todos os arquivos PDF em uma pasta e os adiciona ao ChromaDB."
    )
    parser.add_argument(
        "folder_path",
        type=str,
        help="Caminho para a pasta contendo os PDFs a serem processados.",
    )
    args = parser.parse_args()
    target_folder = args.folder_path

    if not os.path.isdir(target_folder):
        print(f"Erro: O caminho '{target_folder}' não é um diretório válido.")
        return

    pdf_files_to_process = [
        os.path.join(target_folder, f)
        for f in os.listdir(target_folder)
        if f.lower().endswith(".pdf")
    ]

    if not pdf_files_to_process:
        print(f"Nenhum arquivo PDF encontrado no diretório '{target_folder}'.")
        return

    print(f"Encontrados {len(pdf_files_to_process)} arquivos PDF para processar.")

    for pdf_file in tqdm(pdf_files_to_process, desc="Processando PDFs"):
        try:
            print(f"\nIniciando processamento de: {os.path.basename(pdf_file)}")
            process_pdf_and_store(pdf_file)
            print(f"Finalizado: {os.path.basename(pdf_file)}")
        except Exception as e:
            print(f"Erro ao processar o arquivo {os.path.basename(pdf_file)}: {e}")
            continue

    print("\nProcessamento em massa concluído com sucesso!")


if __name__ == "__main__":
    main()
