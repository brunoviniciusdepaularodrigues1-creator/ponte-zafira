import time
import json
import os

INPUT_FILE = "input_bridge.txt"
STATE_FILE = "memory_vault.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "capital": 100,
            "volatilidade": 0.1,
            "historico": [],
            "padroes": {"exploracao": 0, "manutencao": 0, "defesa": 0},
            "errors": []
        }
    with open(STATE_FILE, "r") as f:
        try:
            state = json.load(f)
            if "padroes" not in state:
                state["padroes"] = {"exploracao": 0, "manutencao": 0, "defesa": 0}
            if "errors" not in state:
                state["errors"] = []
            return state
        except json.JSONDecodeError:
            return {
                "capital": 100,
                "volatilidade": 0.1,
                "historico": [],
                "padroes": {"exploracao": 0, "manutencao": 0, "defesa": 0},
                "errors": []
            }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def read_input():
    if not os.path.exists(INPUT_FILE):
        return None
    with open(INPUT_FILE, "r") as f:
        data = f.read().strip()
    return data if data else None

def clear_input():
    open(INPUT_FILE, "w").close()

def processar(entrada, estado):
    try:
        volatilidade = estado.get("volatilidade", 0.1)

        # 🔍 REGIME
        if volatilidade < 0.2:
            regime = "calmaria"
        elif volatilidade < 0.5:
            regime = "instavel"
        else:
            regime = "caos"

        # ⚡ DECISÃO
        if volatilidade > 0.7:
            acao = "defesa"
            motivo = "volatilidade extrema"
        else:
            if regime == "calmaria":
                acao = "exploracao"
                motivo = "baixo risco"
            elif regime == "instavel":
                acao = "manutencao"
                motivo = "risco moderado"
            else:
                acao = "defesa"
                motivo = "risco elevado"

        # 📊 SCORE SIMPLES
        if acao == "exploracao":
            score = 1.0
        elif acao == "manutencao":
            score = 0.8
        else:
            score = 0.7

        # 📈 CONTADOR DE PADRÕES
        estado["padroes"][acao] += 1

        # ⚠️ DETECÇÃO DE INCOERÊNCIA (simples)
        # Se o usuário pede risco alto mas o sistema decide por algo conservador (manutenção ou defesa)
        if "risco alto" in entrada.lower() and acao != "exploracao":
            estado["errors"].append({
                "input": entrada,
                "motivo": f"tentativa de risco alto em regime de {regime}",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })

        decisao = {
            "input": entrada,
            "regime": regime,
            "acao": acao,
            "motivo": motivo,
            "score": score,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        return decisao

    except Exception as e:
        estado["errors"].append({
            "erro": str(e),
            "input": entrada,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

        return {
            "input": entrada,
            "acao": "erro_controlado",
            "motivo": str(e),
            "score": 0.0,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

def main():
    print("="*40)
    print("🚀 ZAFIRA COHERENCE ENGINE - SESSÃO 25 (IMV)")
    print(f"Monitorando: {INPUT_FILE}")
    print(f"Persistência: {STATE_FILE}")
    print("="*40)

    while True:
        estado = load_state()
        entrada = read_input()

        if entrada:
            print(f"\n[{time.strftime('%H:%M:%S')}] Novo input detectado: {entrada}")

            decisao = processar(entrada, estado)

            # Atualizar histórico e estado
            estado["historico"].append(decisao)
            save_state(estado)

            # Limpar canal de entrada
            clear_input()

            print(f"[{time.strftime('%H:%M:%S')}] Decisão registrada: {decisao['acao']}")
            print(f"Score: {decisao['score']} | Motivo: {decisao['motivo']}")
            print("-" * 40)

        time.sleep(5)

if __name__ == "__main__":
    main()
