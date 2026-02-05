#!/usr/bin/env python3
"""
bridge_validator.py
===================
Validador automático contra BRIDGE_PROTOCOL (5 camadas, 8 violações)

Uso:
    python bridge_validator.py --file seu_arquivo.md
    python bridge_validator.py --file seu_arquivo.md --output json

Integrado em: PCU/tools/
"""

import re
import json
import sys
from pathlib import Path

class BridgeValidator:
    """Validador de BRIDGE_PROTOCOL"""
    
    VIOLATIONS = {
        1: "Dado confundido com interpretação",
        2: "Símbolo vago ou redefinido",
        3: "Conceito circular",
        4: "Formalismo incompleto",
        5: "Extrapolação além escopo",
        6: "Camadas confundidas",
        7: "Autoridade circular",
        8: "Ausência de limites"
    }
    
    def __init__(self):
        self.violations = []
        self.warnings = []
    
    def validate(self, filepath: str) -> dict:
        """Valida arquivo contra BRIDGE_PROTOCOL"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            return {"error": f"Arquivo não encontrado: {filepath}"}
        
        # Verifica camadas
        self._check_layer_0(content)  # Observação
        self._check_layer_1(content)  # Símbolo
        self._check_layer_2(content)  # Conceito
        self._check_layer_3(content)  # Formalismo
        self._check_layer_4(content)  # Interpretação
        
        score = 1.0 - (len(self.violations) * 0.1)
        score = max(0, min(1, score))
        
        return {
            "file": filepath,
            "score": score,
            "violations": self.violations,
            "warnings": self.warnings,
            "approved": score >= 0.8
        }
    
    def _check_layer_0(self, content: str):
        """Verifica se dados têm fonte"""
        # Procura por fontes (http, doi, arxiv, etc.)
        has_source = bool(re.search(r'(http|doi|arxiv|ref|fonte|source)', content, re.IGNORECASE))
        if not has_source and len(content) > 500:
            self.warnings.append("Camada 0: Nenhuma fonte citada")
    
    def _check_layer_1(self, content: str):
        """Verifica se termos técnicos estão definidos"""
        # Termos suspeitos sem definição
        vague_terms = ['energia', 'realidade', 'verdade', 'consciência', 'essência']
        for term in vague_terms:
            if term in content.lower() and f'{term} =' not in content.lower():
                self.violations.append({
                    "type": 2,
                    "description": f"Símbolo '{term}' pode estar vago"
                })
    
    def _check_layer_2(self, content: str):
        """Verifica circularidade"""
        if re.search(r'\b\w+\s+\w+\s+\1\b', content):
            self.violations.append({
                "type": 3,
                "description": "Possível definição circular detectada"
            })
    
    def _check_layer_3(self, content: str):
        """Verifica formalismo"""
        # Procura por palavras declarativas ("assume-se", "considere", etc.)
        declarative = re.findall(r'(assume-se|considera-se|seja|seja dado)', content, re.IGNORECASE)
        if len(declarative) > 5:
            self.violations.append({
                "type": 4,
                "description": f"Formalismo declarativo ({len(declarative)} instâncias)"
            })
    
    def _check_layer_4(self, content: str):
        """Verifica escopo e limites"""
        # Procura por termos de limitação
        has_limits = bool(re.search(r'(limita|escopo|fora de|n\u00e3o aborda|restr|validade)', content, re.IGNORECASE))
        if not has_limits:
            self.violations.append({
                "type": 8,
                "description": "Nenhuma limitação ou escopo explícito declarado"
            })
        
        # Procura por afirmações absolutas
        absolutes = re.findall(r'(sempre|jamais|nunca|completamente|absolutamente)', content, re.IGNORECASE)
        if len(absolutes) > 3:
            self.warnings.append(f"Camada 4: {len(absolutes)} afirmações absolutas")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validador BRIDGE_PROTOCOL')
    parser.add_argument('--file', required=True, help='Arquivo a validar')
    parser.add_argument('--output', default='text', choices=['text', 'json'], help='Formato de saída')
    
    args = parser.parse_args()
    
    validator = BridgeValidator()
    result = validator.validate(args.file)
    
    if args.output == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\u2705 Arquivo: {result.get('file', 'N/A')}")
        print(f"Score: {result.get('score', 0):.2f}/1.0")
        print(f"Aprovado: {'SIM' if result.get('approved') else 'NÃO'}")
        
        if result.get('violations'):
            print(f"\n⚠️ Violações ({len(result['violations'])})")
            for v in result['violations']:
                print(f"  - Tipo {v['type']}: {v['description']}")
        
        if result.get('warnings'):
            print(f"\n📄 Avisos ({len(result['warnings'])})")
            for w in result['warnings']:
                print(f"  - {w}")

if __name__ == "__main__":
    main()
