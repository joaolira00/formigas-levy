# 🐜 ACO-Lévy: A Novel Ant Colony Optimization Algorithm With Lévy Flight

Este projeto implementa um algoritmo de **Otimização por Colônia de Formigas** (Ant Colony Optimization — ACO) com **saltos Lévy (Lévy Flight)**, inspirado no artigo:

> **A Novel Ant Colony Optimization Algorithm With Lévy Flight**  

O objetivo principal é resolver o **Problema do Caixeiro Viajante (TSP)**, testando a melhoria da convergência ao introduzir movimentos aleatórios de longa distância (Lévy flights) no comportamento das formigas.

---

## ✨ Principais características

- 🧠 Modelo ACO baseado em feromônios e heurísticas
- 🎯 Suporte a instâncias do TSP no formato **TSPLIB**
- 📈 Plot da melhor rota e evolução da solução ao longo das iterações
- ✨ Incremento por *Lévy flight*:
  - Evita mínimos locais
  - Aumenta diversidade da busca
  - Melhora o desempenho em mapas complexos

---

## 🔧 Requisitos e instalação

- Python >= 3.12

- Rode o comando abaixo para instalar as dependências:
```
$ pip install -r requirements.txt
```

## ▶️ Execução

Na linha 207, você pode trocar qual TSP você quer calcular, apenas substitua o nome do arquivo atual pelo que você desejar:

```
tsp = load_tsp("TSP/{nomeDoTSP}.tsp")
```

Use o comando abaixo para rodar o programa:

```
$ python main.py
```

📊 Resultados

O script gera:

📌 Comprimento da melhor rota

📈 Custo de cada rota

🗺️ Gráfico com o melhor caminho encontrado




