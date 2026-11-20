from pandas import DataFrame
from numpy import sqrt, sum, array
import matplotlib.pyplot as plt
from converti import converti
from mylib import LinearFit

plt.style.use("ggplot")

cost_temp_termometro = 95.8

# 2 costanti di tempo per considerare il tempo di accendere la resistenza e la reazione del termometro
inf_tlim = 3*cost_temp_termometro 
P_a = 100.82 # kPa

def c_to_k(T):
    return T+273.15

a_all = []
da_all = []

m_exp = 1

CHI2 = DataFrame({
    "chi2": [],
    "ni": [],
})

N_misure = 4
for i in range(2, N_misure+1):
    dati_T = converti(f"./misure/temperatura gl/temp{i}.txt")
    dati_T["Temperatura(C)"] = c_to_k(dati_T["Temperatura(C)"])
    dati_P = converti(f"./misure/pressione gl/press{i}.txt")
    # fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    # ax[0].plot(dati_P["Tempo(s)"], dati_P["Pressione(kPa)"], "o", label="$P(t)$", markersize=1)
    # ax[0].set_xlabel("$t$ [s]")
    # ax[0].set_ylabel("$P$ [kPa]")
    # ax[1].plot(dati_T["Tempo(s)"], dati_T["Temperatura(C)"], "o",label="$T(t)$", markersize=1)
    # ax[1].set_xlabel("$t$ [s]")
    # ax[1].set_ylabel("$T$ [K]")
    # fig.savefig(f"./grafici/gl/T(t)_P(t)_{i}.png")
    P_0 = P_a
    dP_0 = dP_a = 0.01
    # escludo il transiente iniziale
    dati_T = dati_T[(dati_T["Tempo(s)"] >= inf_tlim)]
    dati_P = dati_P[(dati_P["Tempo(s)"] >= inf_tlim)]
    fig, ax = plt.subplots(figsize=(8, 6))
    # ax.plot(dati_T["Temperatura(C)"], dati_P["Pressione(kPa)"], "o", label="$P(t)$", markersize=1)
    # ax.set_xlabel("$T$ [K]")
    # ax.set_ylabel("$P(T)$ [kPa]")
    # fig.savefig(f"./grafici/gl/P(T)_{i}_cut.png")
    dati_T = dati_T.loc[dati_T.groupby("Temperatura(C)")["Tempo(s)"].idxmin()].sort_values("Tempo(s)")[-20:]
    dati_P = dati_P[dati_P['Tempo(s)'].isin(dati_T['Tempo(s)'])][-20:]

    dati_T0 = converti(f"./misure/temperatura gl/temp{i}_1.txt")
    dati_T0["Temperatura(C)"] = c_to_k(dati_T0["Temperatura(C)"])
    # fig, ax = plt.subplots()
    # ax.plot(dati_T0["Tempo(s)"], dati_T0["Temperatura(C)"], "o",label="$T(t)$", markersize=1)
    # ax.set_xlabel("$t$ [s]")
    # ax.set_ylabel("$T$ [K]")
    # plt.show()

    T_0 = dati_T0["Temperatura(C)"].mean()
    dT_0 = sqrt(dati_T0["Temperatura(C)"].std(ddof=1)**2/dati_T0.__len__() + (0.05/sqrt(12))**2)

    t = dati_P["Tempo(s)"].to_numpy()
    P = (dati_P["Pressione(kPa)"].to_numpy() + P_0)/P_0
    T = dati_T["Temperatura(C)"].to_numpy()/T_0
    dP = sqrt(((1/P_0)**2)*(0.005**2/12) + ((dati_P["Pressione(kPa)"].to_numpy()/P_0**2)**2)*(0.01**2)) # kPa
    dT = sqrt(((1/T_0)**2)*((0.05/sqrt(12))**2) + ((dati_T["Temperatura(C)"].to_numpy()/(T_0)**2)**2)*(dT_0)**2) # °C = K
    # dP = 0.005/(sqrt(12)*(P_0 + P_a)) # kPa
    # dT = 0.05/(sqrt(12)*T_0) # °C = K

    df_fit = DataFrame({
        "P": P,
        "T": T,
        "dP": dP, # brutto ma funziona
    })

    fit = LinearFit(df_fit, "T", "P", "dP", True)
    a = fit.get_fit_params()[0][0]

    # stimo le nuove incertezze contanto anche quelle su T
    dP_new = sqrt(dP**2 + (a*dT)**2)
    df_fit["dP"] = dP_new

    if i==2 or i==4:
        fit = LinearFit(df_fit, "T", "P")
        # metodo dei residui
        dP_new_res = fit.get_chi2()[1]
        df_fit["dP"] = [dP_new_res for ti in t]

    # fit finale
    fit = LinearFit(df_fit, "T", "P", "dP", True)
    p, cov = fit.get_fit_params()

    chi2 = fit.get_chi2().chi2
    df = fit.get_chi2().df
    CHI2.loc[i] = [chi2, df]
    a = p[0]
    da = sqrt(cov[0][0])
    a_all.append(a)
    da_all.append(da)

    print(f"q = {p[1]} +- {sqrt(cov[1][1])}")

    print(f"a = {a} +- {da}")
    print("chi2 = ", chi2)
    print("df = ", df)
    print("sqrt(df) = ", sqrt(df))
    print("\n")


    # fig, ax = plt.subplots(figsize=(10, 6))
    # fit.graph(ax, ("$T$ [K]", "$P(T)$ [kPa]"), 3, 18, 12)
    # fig.savefig(f"./grafici/gl/P(T)_{i}.png")

a_all = array(a_all)
da_all = array(da_all)

m = sum(a_all/(da_all**2))/sum(1/(da_all**2))
dm = 1/sqrt(sum(1/da_all**2))

print(f"m = {m} +- {dm}")
z = abs(m_exp - m)/dm
print("z = ", z)

print(DataFrame({
    "m": a_all,
    "dm": da_all,
}).to_latex())

print(CHI2.round(2).to_latex())
