import numpy as np
import matplotlib.pyplot as plt
from converti import converti

plt.style.use("ggplot")

cost_temp_termometro = 95.8

# 2 costanti di tempo per considerare il tempo di accendere la resistenza e la reazione del termometro
inf_tlim = 2*cost_temp_termometro 

N_misure = 4
for i in range(1, N_misure+1):
    dati_P = converti(f"./misure/pressione gl/press{i}.txt")
    dati_T = converti(f"./misure/temperatura gl/temp{i}.txt")
    # escludo il transiente iniziale
    dati_P = dati_P.drop(dati_P[(dati_P["Tempo(s)"] < inf_tlim)].index)
    dati_T = dati_T.drop(dati_T[(dati_T["Tempo(s)"] < inf_tlim)].index)

    t = dati_P["Tempo(s)"]
    p = dati_P["Pressione(kPa)"]
    T = dati_T["Temperatura(C)"]
    T = T+273.13 # K
    
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(t, p, "o", label="$P(t)$", markersize=0.5)
    ax[0].set_xlabel("$t$ [s]")
    ax[0].set_ylabel("$P$ [kPa]")
    ax[1].plot(t, T, "o",label="$T(t)$", markersize=0.5)
    ax[1].set_xlabel("$t$ [s]")
    ax[1].set_ylabel("$T$ [K]")
    # fig.savefig(f"./grafici/gl/T(t)_P(t)_{i}.png")
    plt.show()



