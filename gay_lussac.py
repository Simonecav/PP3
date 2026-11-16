from pandas import DataFrame
from numpy import sqrt
import matplotlib.pyplot as plt
from converti import converti
from mylib import LinearFit

plt.style.use("ggplot")

cost_temp_termometro = 95.8

# 2 costanti di tempo per considerare il tempo di accendere la resistenza e la reazione del termometro
inf_tlim = 3*cost_temp_termometro 
P_0 = 100.82 # kPa
dP = 0.005/sqrt(12) # kPa
dT = 0.05/sqrt(12) # °C = K


N_misure = 4
for i in range(1, N_misure+1):
    dati_T = converti(f"./misure/temperatura gl/temp{i}.txt")
    dati_P = converti(f"./misure/pressione gl/press{i}.txt")
    T_0 = (dati_T["Temperatura(C)"].to_numpy()+273.15)[0]
    # escludo il transiente iniziale
    dati_T = dati_T[dati_T["Tempo(s)"] >= inf_tlim]
    dati_P = dati_P[dati_P["Tempo(s)"] >= inf_tlim]
    dati_T = dati_T.loc[dati_T.groupby("Temperatura(C)")["Tempo(s)"].idxmin()].sort_values("Tempo(s)")
    dati_P = dati_P[dati_P['Tempo(s)'].isin(dati_T['Tempo(s)'])]
    

    t = dati_P["Tempo(s)"].to_numpy()
    P = dati_P["Pressione(kPa)"].to_numpy()
    T = dati_T["Temperatura(C)"].to_numpy()
    T = T+273.13 # K
    
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(t, P, "o", label="$P(t)$", markersize=3)
    ax[0].set_xlabel("$t$ [s]")
    ax[0].set_ylabel("$P$ [kPa]")
    ax[1].plot(t, T, "o",label="$T(t)$", markersize=3)
    ax[1].set_xlabel("$t$ [s]")
    ax[1].set_ylabel("$T$ [K]")
    # fig.savefig(f"./grafici/gl/T(t)_P(t)_{i}.png")
    plt.show()

    df_fit = DataFrame({
        "P": P,
        "T": T,
        "dP": [dP for ti in t], # brutto ma funziona
    })

    fit = LinearFit(df_fit, "T", "P", "dP", True)
    a = fit.get_fit_params()[0][0]

    # stimo le nuove incertezze contanto anche quelle su T
    dP_new = sqrt(dP**2 + (a*dT**2))
    df_fit["dP"] = [dP_new for ti in t]

    # fit finale
    fit = LinearFit(df_fit, "T", "P", "dP", True)
    p, cov = fit.get_fit_params()

    chi2 = fit.get_chi2().chi2
    df = fit.get_chi2().df
    a = p[0]
    da = sqrt(cov[0][0])
    a_exp = (P[0]+P_0)/T_0

    print(f"a = {a} +- {da}")
    print("a_exp = ", a_exp)
    print("chi2 = ", chi2)
    print("df = ", df)
    print("sqrt(df) = ", sqrt(df))

    z = abs(a_exp - a)/da
    print("z = ", z)
    print("\n")

    fig, ax = plt.subplots()
    fit.graph(ax, ("$T$ [K]", "$P(T)$ [kPa]"), 3, 15)
    # fig.savefig(f"./grafici/gl/P(T)_{i}.png")
    plt.show()
    




