import argparse
import os
import random
import sys

from tqdm import tqdm # type: ignore

from app.processing import process_pdf_and_store

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)



def main():
    parser = argparse.ArgumentParser(
        description="Processa uma amostra aleatória de 500 arquivos PDF e salva a lista de nomes."
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

    all_pdf_files = [
        os.path.join(target_folder, f)
        for f in os.listdir(target_folder)
        if f.lower().endswith(".pdf")
    ]

    if not all_pdf_files:
        print(f"Nenhum arquivo PDF encontrado no diretório '{target_folder}'.")
        return

    print(f"Encontrados {len(all_pdf_files)} arquivos PDF no total.")

    sample_size = 500
    if len(all_pdf_files) > sample_size:
        print(f"Selecionando uma amostra aleatória de {sample_size} arquivos...")
        pdf_files_to_process = random.sample(all_pdf_files, sample_size)
    else:
        print(
            f"O número total de arquivos ({len(all_pdf_files)}) é menor ou igual a {sample_size}. Processando todos os arquivos."
        )
        pdf_files_to_process = all_pdf_files

    output_filename = "processed_files_sample.txt"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            for file_path in pdf_files_to_process:
                f.write(os.path.basename(file_path) + "\n")
        print(
            f"Lista de {len(pdf_files_to_process)} arquivos a serem processados foi salva em '{output_filename}'."
        )
    except IOError as e:
        print(f"Erro ao salvar a lista de arquivos: {e}")

    print(f"\nIniciando o processamento de {len(pdf_files_to_process)} arquivos.")

    for pdf_file in tqdm(pdf_files_to_process, desc="Processando Amostra de PDFs"):
        try:
            process_pdf_and_store(pdf_file)
        except Exception as e:
            tqdm.write(f"Erro ao processar o arquivo {os.path.basename(pdf_file)}: {e}")
            continue

    print("\nProcessamento da amostra concluído com sucesso!")


if __name__ == "__main__":
    main()
