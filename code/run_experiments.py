import csv
from Algoritmo_Genetico import executar_experimentos

if __name__ == '__main__':
    # Parâmetros do experimento
    runs = 100
    tamanho_pop = 100
    taxa_mut = 0.1
    taxa_cross = 0.8
    num_geracoes = 2000
    fitness_alvo = 2.0

    print(f"Executando {runs} runs (pop={tamanho_pop}, geracoes={num_geracoes})...")
    results = executar_experimentos(runs=runs,
                                    tamanho_pop=tamanho_pop,
                                    taxa_mut=taxa_mut,
                                    taxa_cross=taxa_cross,
                                    num_geracoes=num_geracoes,
                                    fitness_alvo=fitness_alvo)

    csv_path = 'experiment_results.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['run', 'generation_found'])
        for i, gen in enumerate(results, start=1):
            writer.writerow([i, gen])

    print(f"Resultados salvos em: {csv_path}")
