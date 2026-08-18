import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Controle Fuzzy de CPU", page_icon="⚙️", layout="centered")

st.title("⚙️ Sistema Especialista Fuzzy")
st.markdown("**Domínio:** Ajuste Dinâmico de Frequência da CPU (Thermal Throttling)")
st.write("Mova as barras abaixo para simular a demanda do usuário e a temperatura atual do processador.")
st.divider()

# ==========================================
# 1. LÓGICA FUZZY
# ==========================================
@st.cache_resource # Isso faz o Streamlit carregar a lógica mais rápido
def criar_sistema_fuzzy():
    # Variáveis
    demanda = ctrl.Antecedent(np.arange(1.0, 5.1, 0.1), 'demanda')
    temperatura = ctrl.Antecedent(np.arange(30, 101, 1), 'temperatura')
    frequencia = ctrl.Consequent(np.arange(1.0, 5.1, 0.1), 'frequencia')

    # Funções de Pertinência
    demanda['baixa'] = fuzz.trimf(demanda.universe, [1.0, 1.0, 2.8])
    demanda['media'] = fuzz.trimf(demanda.universe, [2.0, 3.0, 4.0])
    demanda['alta'] = fuzz.trimf(demanda.universe, [3.2, 5.0, 5.0])

    temperatura['segura'] = fuzz.trimf(temperatura.universe, [30, 30, 65])
    temperatura['elevada'] = fuzz.trimf(temperatura.universe, [50, 70, 85])
    temperatura['critica'] = fuzz.trimf(temperatura.universe, [75, 100, 100])

    frequencia['underclock'] = fuzz.trimf(frequencia.universe, [1.0, 1.0, 2.8])
    frequencia['base'] = fuzz.trimf(frequencia.universe, [2.0, 3.0, 4.0])
    frequencia['turbo'] = fuzz.trimf(frequencia.universe, [3.2, 5.0, 5.0])

    # Regras
    r1 = ctrl.Rule(demanda['baixa'], frequencia['underclock'])
    r2 = ctrl.Rule(demanda['media'] & temperatura['segura'], frequencia['base'])
    r3 = ctrl.Rule(demanda['alta'] & temperatura['segura'], frequencia['turbo'])
    r4 = ctrl.Rule(demanda['alta'] & temperatura['elevada'], frequencia['base'])
    r5 = ctrl.Rule(demanda['alta'] & temperatura['critica'], frequencia['underclock'])
    r6 = ctrl.Rule(demanda['media'] & temperatura['critica'], frequencia['underclock'])

    sistema_controle = ctrl.ControlSystem([r1, r2, r3, r4, r5, r6])
    return ctrl.ControlSystemSimulation(sistema_controle)

simulador = criar_sistema_fuzzy()

# ==========================================
# 2. INTERFACE DO USUÁRIO (Sliders)
# ==========================================
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Entradas (Sensores)")
    in_demanda = st.slider("Demanda de Processamento (GHz)", min_value=1.0, max_value=5.0, value=3.0, step=0.1)
    in_temp = st.slider("Temperatura (°C)", min_value=30, max_value=100, value=50, step=1)

# ==========================================
# 3. PROCESSAMENTO FUZZY E RESULTADOS
# ==========================================
# Passando valores para o simulador
simulador.input['demanda'] = in_demanda
simulador.input['temperatura'] = in_temp
simulador.compute()
resultado_ghz = simulador.output['frequencia']
porcentagem_uso = int((resultado_ghz / 5.0) * 100)

with col2:
    st.subheader("Saída Fuzzy (Decisão)")
    # Um card bonito mostrando a frequência calculada
    st.metric(label="Frequência Aplicada à CPU", value=f"{resultado_ghz:.2f} GHz")
    
    # Barra de progresso visual
    st.write("Capacidade de Clock:")
    st.progress(porcentagem_uso / 100.0)

st.divider()

# ==========================================
# 4. DIAGNÓSTICO INTERATIVO
# ==========================================
st.subheader("Análise do Sistema")

if in_temp >= 85:
    st.error("🥵 **ALERTA CRÍTICO:** Risco de dano físico! Aplicando *Thermal Throttling* severo (Underclock) para forçar o resfriamento imediato da CPU, ignorando a demanda do usuário.")
elif in_temp >= 70 and in_demanda > 3.5:
    st.warning("⚠️ **Gargalo Térmico Moderado:** O usuário quer desempenho, mas a temperatura está subindo. Segurando a frequência na base para não superaquecer.")
elif in_demanda >= 4.0 and in_temp < 65:
    st.success("🚀 **TURBO BOOST ATIVADO:** Condições térmicas perfeitas! Liberando potência máxima de forma segura.")
elif in_demanda < 2.0:
    st.info("💤 **Modo Ocioso:** Sistema com baixa demanda. Reduzindo o clock para economizar energia e manter a máquina fria.")
else:
    st.info("⚖️ **Operação Normal:** O sistema encontrou um equilíbrio ideal entre a tarefa atual e o aquecimento da máquina.")
