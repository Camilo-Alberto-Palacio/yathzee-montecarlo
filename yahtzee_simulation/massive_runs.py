"""
=============================================================================
  CORRIDAS MASIVAS DE PARTIDAS COMPLETAS (BENCHMARKING DE ESTRATEGIAS)
=============================================================================
Simulación masiva de miles de partidas completas de Yahtzee (13 rondas por juego)
contrastando tres niveles de toma de decisiones bajo incertidumbre:
1. Agente Aleatorio (Baseline ciego).
2. Agente Heurístico Codicioso (Greedy humano basado en patrones inmediatos).
3. Agente IA Monte Carlo (Optimización estocástica mediante Valor Esperado - EV).
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from collections import Counter

from .rules import (
    CATEGORIAS,
    CATEGORIAS_SUPERIORES,
    CATEGORIAS_INFERIORES,
    calcular_puntos,
    mejor_puntaje,
    todas_las_mascaras,
    UMBRAL_BONO_SUPERIOR,
    PUNTOS_BONO_SUPERIOR
)


class PartidaYahtzeeSimulador:
    """
    Simula una partida individual de Yahtzee para un agente dado.
    """
    def __init__(self, tipo_agente: str = "montecarlo", sims_ev: int = 100, rng: Optional[np.random.Generator] = None):
        self.tipo_agente = tipo_agente
        self.sims_ev = sims_ev
        self.rng = rng if rng is not None else np.random.default_rng()
        self.tarjeta: Dict[str, int] = {}

    def tirar_dados(self, dados_actuales: Optional[List[int]] = None, mascara: Optional[List[bool]] = None) -> List[int]:
        if dados_actuales is None:
            return list(self.rng.integers(1, 7, size=5))

        nuevos = list(dados_actuales)
        for i in range(5):
            if not mascara[i]:
                nuevos[i] = int(self.rng.integers(1, 7))
        return nuevos

    def decidir_retencion_aleatoria(self) -> List[bool]:
        """Agente aleatorio: elige una máscara de retención al azar."""
        return list(self.rng.choice([True, False], size=5))

    def decidir_retencion_heuristica(self, dados: List[int], libres: List[str]) -> List[bool]:
        """
        Agente Heurístico Humano:
        - Si tiene 3 o más de un número, los retiene buscando Trío/Póker/Full/Yahtzee.
        - Si tiene un par, retiene el par.
        - Si tiene 3 o más consecutivos y falta escalera, retiene la secuencia.
        - Si no, retiene los dados de mayor denominación (5s y 6s).
        """
        conteo = Counter(dados)
        mas_comun, max_frec = conteo.most_common(1)[0]

        if max_frec >= 2:
            return [d == mas_comun for d in dados]

        # Secuencia
        unicos = sorted(set(dados))
        if len(unicos) >= 3:
            for l in range(len(unicos) - 2):
                if unicos[l+1] == unicos[l] + 1 and unicos[l+2] == unicos[l] + 2:
                    seq = {unicos[l], unicos[l+1], unicos[l+2]}
                    return [d in seq for d in dados]

        # Retener caras altas (5 y 6)
        return [d in (5, 6) for d in dados]

    def decidir_retencion_montecarlo(self, dados: List[int], libres: List[str]) -> List[bool]:
        """
        Agente IA Monte Carlo:
        Evalúa las 32 máscaras de retención mediante simulación y elige
        la que maximiza el Valor Esperado (EV).
        """
        mascaras = todas_las_mascaras()
        mejor_mask = mascaras[0]
        mejor_ev = -1.0

        for mask in mascaras:
            # Simulación rápida
            puntos_acum = 0.0
            for _ in range(self.sims_ev):
                sim_mano = list(dados)
                for pos in range(5):
                    if not mask[pos]:
                        sim_mano[pos] = int(self.rng.integers(1, 7))
                _, pts = mejor_puntaje(sim_mano, libres)
                puntos_acum += pts

            ev = puntos_acum / self.sims_ev
            if ev > mejor_ev:
                mejor_ev = ev
                mejor_mask = mask

        return mejor_mask

    def seleccionar_retencion(self, dados: List[int], libres: List[str]) -> List[bool]:
        if self.tipo_agente == "aleatorio":
            return self.decidir_retencion_aleatoria()
        elif self.tipo_agente == "heuristico":
            return self.decidir_retencion_heuristica(dados, libres)
        else:
            return self.decidir_retencion_montecarlo(dados, libres)

    def jugar_ronda(self) -> None:
        libres = [c for c in CATEGORIAS if c not in self.tarjeta]
        if not libres:
            return

        # Tirada 1
        dados = self.tirar_dados()

        # Tirada 2
        mask1 = self.seleccionar_retencion(dados, libres)
        if not all(mask1):
            dados = self.tirar_dados(dados, mask1)

            # Tirada 3
            mask2 = self.seleccionar_retencion(dados, libres)
            if not all(mask2):
                dados = self.tirar_dados(dados, mask2)

        # Asignación a tarjeta
        if self.tipo_agente == "aleatorio":
            cat_elegida = self.rng.choice(libres)
            pts = calcular_puntos(cat_elegida, dados)
        else:
            cat_elegida, pts = mejor_puntaje(dados, libres)

        self.tarjeta[cat_elegida] = pts

    def jugar_partida_completa(self) -> Dict[str, float]:
        self.tarjeta = {}
        for _ in range(13):
            self.jugar_ronda()

        suma_sup = sum(self.tarjeta.get(c, 0) for c in CATEGORIAS_SUPERIORES)
        bono = PUNTOS_BONO_SUPERIOR if suma_sup >= UMBRAL_BONO_SUPERIOR else 0
        suma_inf = sum(self.tarjeta.get(c, 0) for c in CATEGORIAS_INFERIORES)
        total = suma_sup + bono + suma_inf

        res = {
            "estrategia": self.tipo_agente,
            "suma_superior": suma_sup,
            "bono": bono,
            "bono_obtenido": bool(bono > 0),
            "suma_inferior": suma_inf,
            "puntaje_total": total
        }
        for c in CATEGORIAS:
            res[f"cat_{c}"] = self.tarjeta.get(c, 0)

        return res


def ejecutar_corridas_masivas_estrategias(
    n_partidas_por_estrategia: int = 1_000,
    seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ejecuta un torneo masivo de simulación comparando las tres estrategias.
    Retorna:
      - DataFrame detallado con el resultado de cada partida.
      - DataFrame resumen con estadísticas descriptivas (Media, Mediana, DesvStd, Tasa de Bono).
    """
    rng = np.random.default_rng(seed)
    estrategias = ["aleatorio", "heuristico", "montecarlo"]
    resultados = []

    for est in estrategias:
        sims_ev = 60 if est == "montecarlo" else 0
        simulador = PartidaYahtzeeSimulador(tipo_agente=est, sims_ev=sims_ev, rng=rng)

        for _ in range(n_partidas_por_estrategia):
            r = simulador.jugar_partida_completa()
            resultados.append(r)

    df_detalle = pd.DataFrame(resultados)

    # Métricas agregadas
    resumen_list = []
    for est in estrategias:
        sub = df_detalle[df_detalle["estrategia"] == est]
        totales = sub["puntaje_total"]
        tasa_bono = sub["bono_obtenido"].mean() * 100.0

        resumen_list.append({
            "Estrategia": est.capitalize(),
            "Partidas Simuladas": len(sub),
            "Puntaje Medio": totales.mean(),
            "Desv. Estándar": totales.std(),
            "Mediana": totales.median(),
            "Mínimo": totales.min(),
            "Máximo": totales.max(),
            "Percentil 25": totales.quantile(0.25),
            "Percentil 75": totales.quantile(0.75),
            "Tasa Bono (+35 pts)": f"{tasa_bono:.1f}%",
            "Subtotal Superior Medio": sub["suma_superior"].mean(),
            "Subtotal Inferior Medio": sub["suma_inferior"].mean()
        })

    df_resumen = pd.DataFrame(resumen_list)
    return df_detalle, df_resumen
