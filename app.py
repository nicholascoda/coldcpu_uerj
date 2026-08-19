import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# CONFIGURAÇÃO DA PÁGINA E FONTE
st.set_page_config(page_title="Controle Fuzzy de CPU", layout="centered")

st.markdown("""
    <style>
    /* Aplica Arial em todo o texto */
    html, body, p, h1, h2, h3, h4, h5, h6, li, div {
        font-family: 'Arial', sans-serif;
    }
    /* Protege a fonte especial dos ícones do Streamlit */
    .material-symbols-rounded, .material-icons {
        font-family: 'Material Symbols Rounded' !important;
    }
    </style>
""", unsafe_allow_html=True)

# BARRA LATERAL
with st.sidebar:
    st.write("**Disciplina:** Inteligência Computacional II")
    st.write("**Professor:** Thiago Dabouit")
    st.write("**Instituição:** UERJ")
    st.divider()
    st.header("👨‍💻 Equipe do Projeto")
    st.write("- Nicholas Coda")
    st.write("- Matheus Corrêa")
    st.write("- Luiz Gustavo Guaycuruz")
   


# CABEÇALHO PRINCIPAL
st.title("⚙️ Sistema Especialista Fuzzy")
st.markdown("**Domínio:** Ajuste Dinâmico de Frequência da CPU (Thermal Throttling)")
st.write("Mova as barras abaixo para simular a demanda do usuário e a temperatura atual do processador.")
st.divider()


# 1. LÓGICA FUZZY
@st.cache_resource
def criar_sistema_fuzzy():
    demanda = ctrl.Antecedent(np.arange(1.0, 5.1, 0.1), 'demanda')
    temperatura = ctrl.Antecedent(np.arange(30, 101, 1), 'temperatura')
    frequencia = ctrl.Consequent(np.arange(1.0, 5.1, 0.1), 'frequencia')

    demanda['baixa'] = fuzz.trimf(demanda.universe, [0.0, 1.0, 2.8])
    demanda['media'] = fuzz.trimf(demanda.universe, [2.0, 3.0, 4.0])
    demanda['alta'] = fuzz.trimf(demanda.universe, [3.2, 5.0, 6.0])

    temperatura['segura'] = fuzz.trimf(temperatura.universe, [0, 30, 65])
    temperatura['elevada'] = fuzz.trimf(temperatura.universe, [50, 70, 85])
    temperatura['critica'] = fuzz.trimf(temperatura.universe, [75, 100, 110])

    frequencia['underclock'] = fuzz.trimf(frequencia.universe, [0.0, 1.0, 2.8])
    frequencia['base'] = fuzz.trimf(frequencia.universe, [2.0, 3.0, 4.0])
    frequencia['turbo'] = fuzz.trimf(frequencia.universe, [3.2, 5.0, 6.0])

    r1 = ctrl.Rule(demanda['baixa'], frequencia['underclock'])
    r2 = ctrl.Rule(demanda['media'] & temperatura['segura'], frequencia['base'])
    r3 = ctrl.Rule(demanda['alta'] & temperatura['segura'], frequencia['turbo'])
    r4 = ctrl.Rule(demanda['alta'] & temperatura['elevada'], frequencia['base'])
    r5 = ctrl.Rule(demanda['alta'] & temperatura['critica'], frequencia['underclock'])
    r6 = ctrl.Rule(demanda['media'] & temperatura['critica'], frequencia['underclock'])
    r7 = ctrl.Rule(demanda['media'] & temperatura['elevada'], frequencia['base'])

    sistema_controle = ctrl.ControlSystem([r1, r2, r3, r4, r5, r6, r7])
    return sistema_controle, frequencia

sistema_controle, var_frequencia = criar_sistema_fuzzy()
simulador = ctrl.ControlSystemSimulation(sistema_controle)

# 2. INTERFACE DO USUÁRIO
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Entradas (Sensores)")
    in_demanda = st.slider("Demanda de Processamento (GHz)", min_value=1.0, max_value=5.0, value=3.0, step=0.1)
    in_temp = st.slider("Temperatura (°C)", min_value=30, max_value=100, value=50, step=1)

# 3. PROCESSAMENTO FUZZY E RESULTADOS
simulador.input['demanda'] = in_demanda
simulador.input['temperatura'] = in_temp
simulador.compute()
resultado_ghz = simulador.output['frequencia']
porcentagem_uso = int((resultado_ghz / 5.0) * 100)

with col2:
    st.subheader("Saída Fuzzy (Decisão)")
    st.metric(label="Frequência Aplicada à CPU", value=f"{resultado_ghz:.2f} GHz")
    st.write("Capacidade de Clock:")
    st.progress(porcentagem_uso / 100.0)

st.divider()

# 4. DIAGNÓSTICO INTERATIVO
st.subheader("Análise do Sistema")

if in_temp >= 85:
    st.error("🔥 **ALERTA CRÍTICO:** Risco de dano físico! Aplicando *Thermal Throttling* severo (Underclock) para forçar o resfriamento imediato da CPU, ignorando a demanda do usuário.")
elif in_temp >= 70 and in_demanda > 3.5:
    st.warning("⚠️ **Gargalo Térmico Moderado:** O usuário quer desempenho, mas a temperatura está subindo. Segurando a frequência na base para não superaquecer.")
elif in_demanda >= 4.0 and in_temp < 65:
    st.success("🚀 **TURBO BOOST ATIVADO:** Condições térmicas perfeitas! Liberando potência máxima de forma segura.")
elif in_demanda < 2.0:
    st.info("💤 **Modo Ocioso:** Sistema com baixa demanda. Reduzindo o clock para economizar energia e manter a máquina fria.")
else:
    st.info("⚖️ **Operação Normal:** O sistema encontrou um equilíbrio ideal entre a tarefa atual e o aquecimento da máquina.")

st.divider()

# 5. GRÁFICO DINÂMICO
st.subheader("📊 Visualização da Defuzzificação")
st.write("A área preenchida mostra os trapézios cortados pelas regras ativadas. A **linha preta grossa** indica o exato **Centro de Área** (ponto de equilíbrio) calculado.")

var_frequencia.view(sim=simulador)

fig_resultado = plt.gcf()
ax_resultado = plt.gca()
ax_resultado.set_ylabel("Grau de Pertinência")
ax_resultado.set_xlabel("Frequência da CPU (GHz)")
fig_resultado.set_size_inches(8, 3) 
plt.title("") 

st.pyplot(fig_resultado)
plt.close(fig_resultado)

# 6. VISUALIZAÇÃO DOS GRÁFICOS ESTÁTICOS
st.divider()
st.subheader("📚 Dicionário Fuzzy (Funções de Pertinência)")

with st.expander("Clique aqui para ver as regras do jogo (Gráficos Base)"):
    st.write("Estes gráficos mostram como o sistema interpreta os limites das variáveis.")

    x_dem = np.arange(1.0, 5.1, 0.1)
    x_temp = np.arange(30, 101, 1)
    x_freq = np.arange(1.0, 5.1, 0.1)
    
    # Gráfico 1: Demanda
    fig_dem, ax0 = plt.subplots(figsize=(8, 3))
    ax0.plot(x_dem, fuzz.trimf(x_dem, [0.0, 1.0, 2.8]), 'b', linewidth=2, label='Baixa')
    ax0.plot(x_dem, fuzz.trimf(x_dem, [2.0, 3.0, 4.0]), 'g', linewidth=2, label='Média')
    ax0.plot(x_dem, fuzz.trimf(x_dem, [3.2, 5.0, 6.0]), 'r', linewidth=2, label='Alta')
    ax0.set_title("1. Demanda de Processamento (GHz)")
    ax0.set_ylabel("Grau de Pertinência")
    ax0.legend()
    st.pyplot(fig_dem)
    plt.close(fig_dem)

    # Gráfico 2: Temperatura
    fig_temp, ax1 = plt.subplots(figsize=(8, 3))
    ax1.plot(x_temp, fuzz.trimf(x_temp, [0, 30, 65]), 'b', linewidth=2, label='Segura')
    ax1.plot(x_temp, fuzz.trimf(x_temp, [50, 70, 85]), 'orange', linewidth=2, label='Elevada')
    ax1.plot(x_temp, fuzz.trimf(x_temp, [75, 100, 110]), 'r', linewidth=2, label='Crítica')
    ax1.set_title("2. Temperatura Atual (°C)")
    ax1.set_ylabel("Grau de Pertinência")
    ax1.legend()
    st.pyplot(fig_temp)
    plt.close(fig_temp)
    
    # Gráfico 3: Frequência
    fig_freq, ax2 = plt.subplots(figsize=(8, 3))
    ax2.plot(x_freq, fuzz.trimf(x_freq, [0.0, 1.0, 2.8]), 'b', linewidth=2, label='Underclock')
    ax2.plot(x_freq, fuzz.trimf(x_freq, [2.0, 3.0, 4.0]), 'g', linewidth=2, label='Base')
    ax2.plot(x_freq, fuzz.trimf(x_freq, [3.2, 5.0, 6.0]), 'r', linewidth=2, label='Turbo')
    ax2.set_title("3. Decisão da Frequência (GHz)")
    ax2.set_ylabel("Grau de Pertinência")
    ax2.legend()
    st.pyplot(fig_freq)
    plt.close(fig_freq)
