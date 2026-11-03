"""
=============================================================================
  CORRIDAS MASIVAS DE PARTIDAS COMPLETAS (BENCHMARKING DE ESTRATEGIAS)
=============================================================================
Simulación masiva vectorizada de 3,000 partidas completas de Yahtzee
(13 rondas reglamentarias por partida = 39,000 turnos) contrastando tres
políticas de decisión bajo incertidumbre:
1. Agente Aleatorio (Línea base ciega de control).
2. Agente Heurístico Codicioso (Greedy humano basado en patrones inmediatos).
3. Agente IA Monte Carlo (Optimización estocástica mediante Valor Esperado - EV
   con valoración marginal del Bono Superior de +35 puntos y costo de oportunidad).
"""

from collections import Counter
from typing import List, Dict, Tuple, Optional
import numpy as np
import pandas as pd

from .rules import (
    CATEGORIAS,
    CATEGORIAS_SUPERIORES,
    CATEGORIAS_INFERIORES,
    INDICE_CATEGORIA,
    NUMERO_DE_CATEGORIA,
    UMBRAL_BONO_SUPERIOR,
    PUNTOS_BONO_SUPERIOR,
    MASCARAS_ARRAY,
    TABLA_PUNTOS_OMEGA,
    calcular_puntos,
    mejor_puntaje,
    codificar_manos_base6,
)


def _construir_tabla_utilidad_estrategica() -> np.ndarray:
    """
    Construye una matriz (7776, 13) de utilidad esperada estratégica por estado y categoría.
    Incorpora a los puntos inmediatos:
      1. El valor marginal hacia el Bono Superior (+35 pts al sumar >= 63, paridad = 3*cara):
         obtener k >= 3 dados de una cara alta impulsa decisivamente el bono; anotar k < 3
         en caras altas conlleva una fuerte pérdida de ritmo hacia el umbral de 63.
      2. El costo de oportunidad de quemar prematuramente casillas comodín ('libre') o
         desperdiciar casillas de alto techo ('yahtzee', 'escalera_larga', 'poker', 'full')
         con 0 puntos cuando existen casillas de sacrificio de bajo costo ('unos', 'doses').
    """
    utilidad = TABLA_PUNTOS_OMEGA.astype(np.float64).copy()

    # Ajustes en sección superior (columnas 0..5 -> caras 1..6)
    for col_j, cat in enumerate(CATEGORIAS_SUPERIORES):
        cara = NUMERO_DE_CATEGORIA[cat]
        pts = TABLA_PUNTOS_OMEGA[:, col_j]
        k_dados = pts // cara  # cantidad de dados con esa cara (0..5)
        desvio_paridad = (k_dados - 3) * cara  # superávit o déficit frente a la meta 3*cara
        # Premio proporcional al avance hacia +35 y penalización por sacrificar caras altas
        ajuste_bono = np.where(
            k_dados >= 3,
            3.5 + 0.75 * desvio_paridad,
            0.90 * desvio_paridad,  # negativo cuando k < 3 (ej. 0 en seises = -16.2, 0 en unos = -2.7)
        )
        utilidad[:, col_j] += ajuste_bono

    # Costos de oportunidad en sección inferior para preservar comodines y jugadas mayores
    penalizacion_cero = {
        "trio": -7.0,
        "poker": -10.5,
        "full": -11.5,
        "escalera_corta": -12.5,
        "escalera_larga": -13.5,
        "yahtzee": -14.5,
    }
    for cat, pen in penalizacion_cero.items():
        col_j = INDICE_CATEGORIA[cat]
        pts = TABLA_PUNTOS_OMEGA[:, col_j]
        utilidad[:, col_j] = np.where(pts == 0, pen, pts + 3.0)

    # Reservar 'libre' (Chance) como red de seguridad salvo manos realmente altas
    col_libre = INDICE_CATEGORIA["libre"]
    utilidad[:, col_libre] = TABLA_PUNTOS_OMEGA[:, col_libre] - 7.5

    return utilidad


TABLA_UTILIDAD_ESTRATEGICA = _construir_tabla_utilidad_estrategica()
MASCARAS_3D = MASCARAS_ARRAY[:, None, :]  # (32, 1, 5) para broadcasting


class PartidaYahtzeeSimulador:
    """
    Simula una partida oficial completa de 13 rondas de Yahtzee para un agente dado.
    """

    def __init__(
        self,
        tipo_agente: str = "montecarlo",
        sims_ev: int = 100,
        rng: Optional[np.random.Generator] = None,
    ):
        self.tipo_agente = tipo_agente
        self.sims_ev = sims_ev
        self.rng = rng if rng is not None else np.random.default_rng()
        self.tarjeta: Dict[str, int] = {}

    def tirar_dados(
        self,
        dados_actuales: Optional[List[int]] = None,
        mascara: Optional[List[bool]] = None,
    ) -> List[int]:
        if dados_actuales is None:
            return [int(x) for x in self.rng.integers(1, 7, size=5)]

        nuevos = list(dados_actuales)
        for i in range(5):
            if not mascara[i]:
                nuevos[i] = int(self.rng.integers(1, 7))
        return nuevos

    def decidir_retencion_aleatoria(self) -> List[bool]:
        """Agente Aleatorio: elige una máscara binaria equiprobable al azar."""
        idx = int(self.rng.integers(0, 32))
        return MASCARAS_ARRAY[idx].tolist()

    def decidir_retencion_heuristica(self, dados: List[int], libres: List[str]) -> List[bool]:
        """
        Agente Heurístico Humano (Greedy de patrones):
        - Si tiene un par, trío o póker, retiene los dados repetidos.
        - Si no, y tiene 3+ consecutivos, retiene la secuencia.
        - En otro caso, retiene caras altas (5 y 6).
        """
        conteo = Counter(dados)
        mas_comun, max_frec = conteo.most_common(1)[0]

        if max_frec >= 2:
            return [d == mas_comun for d in dados]

        unicos = sorted(set(dados))
        if len(unicos) >= 3:
            for l_idx in range(len(unicos) - 2):
                if unicos[l_idx + 1] == unicos[l_idx] + 1 and unicos[l_idx + 2] == unicos[l_idx] + 2:
                    seq = {unicos[l_idx], unicos[l_idx + 1], unicos[l_idx + 2]}
                    return [d in seq for d in dados]

        return [d in (5, 6) for d in dados]

    def decidir_retencion_montecarlo(self, dados: List[int], libres_idx: List[int]) -> List[bool]:
        """
        Agente IA Monte Carlo Vectorizado:
        Evalúa simultáneamente las 32 máscaras de retención mediante 'sims_ev'
        simulaciones estocásticas cada una (32 * sims_ev tiradas por decisión)
        y selecciona la máscara que maximiza el Valor Esperado Estratégico.
        """
        dados_arr = np.array(dados, dtype=np.int32)  # (5,)
        # Usamos Números Aleatorios Comunes (CRN) entre máscaras para reducir varianza diferencial
        azar = self.rng.integers(1, 7, size=(1, self.sims_ev, 5), dtype=np.int32)
        manos_sim = np.where(MASCARAS_3D, dados_arr, azar)  # (32, sims_ev, 5)
        codigos = codificar_manos_base6(manos_sim)  # (32, sims_ev)

        # Máxima utilidad alcanzable en cada escenario sobre las categorías libres
        utilidades = TABLA_UTILIDAD_ESTRATEGICA[codigos][:, :, libres_idx]
        ev_por_mascara = utilidades.max(axis=2).mean(axis=1)  # (32,)
        mejor_idx = int(np.argmax(ev_por_mascara))
        return MASCARAS_ARRAY[mejor_idx].tolist()

    def seleccionar_categoria_montecarlo(self, dados: List[int], libres: List[str]) -> Tuple[str, int]:
        """
        Selecciona la categoría óptima al cierre del turno maximizando la utilidad
        estratégica esperada (puntaje real + valor marginal del Bono Superior + costo de oportunidad).
        """
        idx_mano = int(codificar_manos_base6(np.array(dados, dtype=np.int32)))
        fila_util = TABLA_UTILIDAD_ESTRATEGICA[idx_mano]
        fila_pts = TABLA_PUNTOS_OMEGA[idx_mano]

        # Si el Bono Superior ya está matemáticamente asegurado o es inalcanzable, usar puntaje directo + preservación
        suma_sup_actual = sum(self.tarjeta.get(c, 0) for c in CATEGORIAS_SUPERIORES)
        max_sup_restante = sum(5 * NUMERO_DE_CATEGORIA[c] for c in libres if c in NUMERO_DE_CATEGORIA)
        bono_decidido = (suma_sup_actual >= UMBRAL_BONO_SUPERIOR) or (
            suma_sup_actual + max_sup_restante < UMBRAL_BONO_SUPERIOR
        )

        mejor_cat = libres[0]
        mejor_val = -1e9
        for cat in libres:
            col_j = INDICE_CATEGORIA[cat]
            if bono_decidido and cat in NUMERO_DE_CATEGORIA:
                # Si el bono ya se definió, valorar puntos reales conservando sacrificio ordenado
                pts_c = int(fila_pts[col_j])
                val = float(pts_c) - (0.5 * NUMERO_DE_CATEGORIA[cat] if pts_c == 0 else 0.0)
            else:
                val = float(fila_util[col_j])

            if val > mejor_val:
                mejor_val = val
                mejor_cat = cat

        return mejor_cat, int(fila_pts[INDICE_CATEGORIA[mejor_cat]])

    def jugar_ronda(self) -> None:
        libres = [c for c in CATEGORIAS if c not in self.tarjeta]
        if not libres:
            return
        libres_idx = [INDICE_CATEGORIA[c] for c in libres]

        # Tirada 1
        dados = self.tirar_dados()

        # Decisión tras Tirada 1 -> Tirada 2
        if self.tipo_agente == "aleatorio":
            mask1 = self.decidir_retencion_aleatoria()
        elif self.tipo_agente == "heuristico":
            mask1 = self.decidir_retencion_heuristica(dados, libres)
        else:
            mask1 = self.decidir_retencion_montecarlo(dados, libres_idx)

        if not all(mask1):
            dados = self.tirar_dados(dados, mask1)

            # Decisión tras Tirada 2 -> Tirada 3
            if self.tipo_agente == "aleatorio":
                mask2 = self.decidir_retencion_aleatoria()
            elif self.tipo_agente == "heuristico":
                mask2 = self.decidir_retencion_heuristica(dados, libres)
            else:
                mask2 = self.decidir_retencion_montecarlo(dados, libres_idx)

            if not all(mask2):
                dados = self.tirar_dados(dados, mask2)

        # Asignación final en la tarjeta de puntuación
        if self.tipo_agente == "aleatorio":
            cat_elegida = str(self.rng.choice(libres))
            pts = calcular_puntos(cat_elegida, dados)
        elif self.tipo_agente == "heuristico":
            cat_elegida, pts = mejor_puntaje(dados, libres)
        else:
            cat_elegida, pts = self.seleccionar_categoria_montecarlo(dados, libres)

        self.tarjeta[cat_elegida] = pts

    def jugar_partida_completa(self) -> Dict[str, float]:
        self.tarjeta = {}
        for _ in range(13):
            self.jugar_ronda()

        suma_sup = sum(self.tarjeta.get(c, 0) for c in CATEGORIAS_SUPERIORES)
        bono = PUNTOS_BONO_SUPERIOR if suma_sup >= UMBRAL_BONO_SUPERIOR else 0
        suma_inf = sum(self.tarjeta.get(c, 0) for c in CATEGORIAS_INFERIORES)
        total = suma_sup + bono + suma_inf

        res: Dict[str, float] = {
            "estrategia": self.tipo_agente,
            "suma_superior": suma_sup,
            "bono": bono,
            "bono_obtenido": bool(bono > 0),
            "suma_inferior": suma_inf,
            "puntaje_total": total,
        }
        for c in CATEGORIAS:
            res[f"cat_{c}"] = self.tarjeta.get(c, 0)

        return res


def ejecutar_corridas_masivas_estrategias(
    n_partidas_por_estrategia: int = 1_000,
    sims_ev_montecarlo: int = 100,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ejecuta un torneo masivo de simulación comparando las tres políticas de decisión.
    Retorna:
      - DataFrame detallado con las 3 * n_partidas_por_estrategia partidas completas.
      - DataFrame resumen con estadísticas descriptivas e intervalos de confianza del 95%.
    """
    rng = np.random.default_rng(seed)
    estrategias = ["aleatorio", "heuristico", "montecarlo"]
    resultados = []

    for est in estrategias:
        sims_ev = sims_ev_montecarlo if est == "montecarlo" else 0
        simulador = PartidaYahtzeeSimulador(tipo_agente=est, sims_ev=sims_ev, rng=rng)

        for _ in range(n_partidas_por_estrategia):
            resultados.append(simulador.jugar_partida_completa())

    df_detalle = pd.DataFrame(resultados)

    etiquetas = {
        "aleatorio": "Aleatorio",
        "heuristico": "Heuristico",
        "montecarlo": "Montecarlo",
    }

    resumen_list = []
    for est in estrategias:
        sub = df_detalle[df_detalle["estrategia"] == est]
        totales = sub["puntaje_total"]
        n_sub = len(sub)
        media = float(totales.mean())
        std = float(totales.std(ddof=1))
        se = std / np.sqrt(n_sub)
        tasa_bono = float(sub["bono_obtenido"].mean() * 100.0)

        resumen_list.append({
            "Estrategia": etiquetas[est],
            "Partidas Simuladas": n_sub,
            "Puntaje Medio": media,
            "Desv. Estándar": std,
            "Error Estándar Media": se,
            "IC 95% Inferior": media - 1.96 * se,
            "IC 95% Superior": media + 1.96 * se,
            "Mediana": float(totales.median()),
            "Mínimo": int(totales.min()),
            "Máximo": int(totales.max()),
            "Percentil 25": float(totales.quantile(0.25)),
            "Percentil 75": float(totales.quantile(0.75)),
            "Tasa Bono (+35 pts)": f"{tasa_bono:.1f}%",
            "Tasa Bono Pct": tasa_bono,
            "Subtotal Superior Medio": float(sub["suma_superior"].mean()),
            "Bono Medio": float(sub["bono"].mean()),
            "Subtotal Inferior Medio": float(sub["suma_inferior"].mean()),
        })

    df_resumen = pd.DataFrame(resumen_list)
    return df_detalle, df_resumen
