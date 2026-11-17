from pandas import DataFrame
from numpy import sqrt, sum, array
import matplotlib.pyplot as plt
from converti import converti
from mylib import LinearFit

plt.style.use("ggplot")

cost_temp_termometro = 95.8

# 2 costanti di tempo per considerare il tempo di accendere la resistenza e la reazione del termometro
#inf_tlim = 3*cost_temp_termometro 
P_a = 100.82 # kPa

def c_to_k(T):
    return T+273.15

a_all = []
da_all = []

m_exp = 1


N_misure = 4
for i in range(1, N_misure+1):
    dati_T = converti(f"./misure/temperatura gl/temp{i}.txt")
    dati_T["Temperatura(C)"] = c_to_k(dati_T["Temperatura(C)"])
    dati_P = converti(f"./misure/pressione gl/press{i}.txt")
    T_0 = (dati_T["Temperatura(C)"].to_numpy())[0]
    P_0 = (dati_P["Pressione(kPa)"].to_numpy())[0]
    # escludo il transiente iniziale
    # dati_T = dati_T[dati_T["Tempo(s)"] >= dati_T["Tempo(s)"].to_numpy()[-1] - 20]
    # dati_P = dati_P[dati_P["Tempo(s)"] >= dati_T["Tempo(s)"].to_numpy()[-1] - 20]
    dati_T = dati_T.loc[dati_T.groupby("Temperatura(C)")["Tempo(s)"].idxmin()].sort_values("Tempo(s)")[-10:]
    dati_P = dati_P[dati_P['Tempo(s)'].isin(dati_T['Tempo(s)'])][-10:]


    t = dati_P["Tempo(s)"].to_numpy()
    P = (dati_P["Pressione(kPa)"].to_numpy()+P_a)/(P_0+P_a)
    T = dati_T["Temperatura(C)"].to_numpy()/T_0
    dP = 0.005/(P_0 + P_a) # kPa
    dT = 0.05/T_0 # °C = K
    
    # fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    # ax[0].plot(t, P, "o", label="$P(t)$", markersize=3)
    # ax[0].set_xlabel("$t$ [s]")
    # ax[0].set_ylabel("$P$ [kPa]")
    # ax[1].plot(t, T, "o",label="$T(t)$", markersize=3)
    # ax[1].set_xlabel("$t$ [s]")
    # ax[1].set_ylabel("$T$ [K]")
    # # fig.savefig(f"./grafici/gl/T(t)_P(t)_{i}.png")
    # plt.show()

    df_fit = DataFrame({
        "P": P,
        "T": T,
        "dP": [dP for ti in t], # brutto ma funziona
    })

    fit = LinearFit(df_fit, "T", "P", "dP", True)
    a = fit.get_fit_params()[0][0]

    # stimo le nuove incertezze contanto anche quelle su T
    dP_new = sqrt(dP**2 + (a*dT)**2)
    df_fit["dP"] = [dP_new for ti in t]

    # fit finale
    fit = LinearFit(df_fit, "T", "P", "dP", True)
    p, cov = fit.get_fit_params()

    chi2 = fit.get_chi2().chi2
    df = fit.get_chi2().df
    a = p[0]
    da = sqrt(cov[0][0])
    a_all.append(a)
    da_all.append(da)

    print(f"a = {a} +- {da}")
    print("chi2 = ", chi2)
    print("df = ", df)
    print("sqrt(df) = ", sqrt(df))
    print("\n")


    fig, ax = plt.subplots()
    fit.graph(ax, ("$T$ [K]", "$P(T)$ [kPa]"), 3, 15)
    # fig.savefig(f"./grafici/gl/P(T)_{i}.png")
    plt.show()

a_all = array(a_all)
da_all = array(da_all)

m = sum(a_all/(da_all**2))/sum(1/(da_all**2))
dm = 1/sqrt(sum(1/da_all**2))

print(f"m = {m} +- {dm}")
z = abs(m_exp - m)/dm
print("z = ", z)
