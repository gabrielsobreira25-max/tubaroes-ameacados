#!/usr/bin/env python3
"""
Reproduz a base sintética e os arquivos CSV/XLSX.
SIMULAÇÃO DE INTELIGÊNCIA ARTIFICIAL: não são entrevistas reais.
Requisitos: pandas, numpy, scipy, openpyxl.
"""
import math
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

SEED, N = 20261123, 500
rng = np.random.default_rng(SEED)
ages = rng.choice(["18–24","25–34","35–44","45–54","55+"],N,p=[.20,.25,.21,.18,.16])
genders = rng.choice(["Mulher","Homem","Não binário","Prefiro não informar"],N,p=[.51,.45,.02,.02])
edu_levels=["Fundamental","Médio","Superior","Pós-graduação"]
education=rng.choice(edu_levels,N,p=[.13,.39,.35,.13])
edu_score=pd.Series(education).map(dict(zip(edu_levels,[0,1,2,3]))).to_numpy()
age_score=pd.Series(ages).map({"18–24":0,"25–34":1,"35–44":2,"45–54":3,"55+":4}).to_numpy()
latent=.65*edu_score+rng.normal(0,1,N)+.12*age_score
sig=lambda x:1/(1+np.exp(-x))
knows_shark=rng.random(N)<sig(-.75+.48*latent)
knows_threat=rng.random(N)<sig(-.85+.52*latent)
knows_impact=rng.random(N)<sig(-.60+.62*latent)
knows_generic=rng.random(N)<sig(-.55+.58*latent)
fish=rng.random(N)<.82
cacao=rng.random(N)<np.where(fish,.53,.07)
freq=[rng.choice(["Semanal","Mensal","Raramente"],p=[.13,.34,.53]) if c else "Nunca" for c in cacao]
checks=rng.random(N)<sig(-1.45+.28*latent)
risk=rng.random(N)<sig(.05+.45*latent)
stop=rng.random(N)<sig(.25+.70*latent+.28*knows_impact.astype(float))
inspection=rng.choice(["Suficiente","Insuficiente","Não sabe"],N,p=[.12,.57,.31])
label=rng.random(N)<.91
campaign=rng.random(N)<.94
pay=rng.choice(["Sim","Talvez","Não"],N,p=[.43,.43,.14])
concern=["Alta" if rng.random()<sig(-.1+.7*latent[i]+.25*knows_impact[i]) else "Baixa/moderada" for i in range(N)]
df=pd.DataFrame({
"ID":[f"SIM{i:03d}" for i in range(1,N+1)],"Q1_faixa_etaria":ages,"Q2_genero":genders,"Q3_escolaridade":education,
"Q4_consumo_pescado":np.where(fish,"Sim","Não"),"Q5_ja_consumiu_cacao":np.where(cacao,"Sim","Não"),
"Q6_frequencia_cacao":freq,"Q7_sabe_cacao_pode_ser_tubarao":np.where(knows_shark,"Sim","Não"),
"Q8_conhece_especies_ameacadas":np.where(knows_threat,"Sim","Não"),"Q9_conhece_impactos_pesca_excessiva":np.where(knows_impact,"Sim","Não"),
"Q10_sabe_varias_especies_nome_cacao":np.where(knows_generic,"Sim","Não"),
"Q11_verifica_especie_procedencia":np.where(checks,"Sempre/às vezes","Nunca/raramente"),
"Q12_acredita_risco_extincao":np.where(risk,"Sim","Não/não sabe"),"Q13_deixaria_cacao_ameacado":np.where(stop,"Sim","Não/depende"),
"Q14_avaliacao_fiscalizacao":inspection,"Q15_importancia_nome_especie":np.where(label,"Sim","Não"),
"Q16_apoia_campanhas":np.where(campaign,"Sim","Não"),"Q17_pagaria_sustentavel":pay,
"indice_preocupacao_conservacao":concern})
df.to_csv("pesquisa_500.csv",index=False,encoding="utf-8-sig")
metrics={"Participantes":len(df),"Consumiram cação (%)":100*(df.Q5_ja_consumiu_cacao=="Sim").mean(),
"Sabem que cação pode ser tubarão (%)":100*(df.Q7_sabe_cacao_pode_ser_tubarao=="Sim").mean(),
"Conhecem espécies ameaçadas (%)":100*(df.Q8_conhece_especies_ameacadas=="Sim").mean(),
"Deixariam de consumir se ameaçado (%)":100*(df.Q13_deixaria_cacao_ameacado=="Sim").mean()}
with pd.ExcelWriter("pesquisa_500.xlsx") as w:
    df.to_excel(w,sheet_name="Dados_500",index=False)
    pd.DataFrame({"Indicador":metrics.keys(),"Valor":metrics.values()}).to_excel(w,sheet_name="Indicadores",index=False)
with pd.ExcelWriter("analise_estatistica.xlsx") as w:
    pd.DataFrame({"Indicador":metrics.keys(),"Resultado":metrics.values()}).to_excel(w,sheet_name="Resumo",index=False)
    tests=[]
    for i,(a,b) in enumerate([
    ("Q1_faixa_etaria","Q7_sabe_cacao_pode_ser_tubarao"),
    ("Q3_escolaridade","Q8_conhece_especies_ameacadas"),
    ("Q5_ja_consumiu_cacao","Q9_conhece_impactos_pesca_excessiva"),
    ("Q9_conhece_impactos_pesca_excessiva","Q13_deixaria_cacao_ameacado"),
    ("Q6_frequencia_cacao","indice_preocupacao_conservacao")],1):
        tab=pd.crosstab(df[a],df[b]); tab.to_excel(w,sheet_name=f"C{i}_contagem")
        (pd.crosstab(df[a],df[b],normalize="index")*100).to_excel(w,sheet_name=f"C{i}_percentual")
        x2,p,dof,exp=chi2_contingency(tab); v=math.sqrt(x2/(len(df)*max(1,min(tab.shape[0]-1,tab.shape[1]-1))))
        tests.append({"Cruzamento":f"{a} × {b}","Qui-quadrado":x2,"gl":dof,"p-valor":p,"V de Cramer":v})
    pd.DataFrame(tests).to_excel(w,sheet_name="Testes_associacao",index=False)
print("Concluído: 500 respondentes sintéticos e planilhas geradas.")
