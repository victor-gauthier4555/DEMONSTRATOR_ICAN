
#differents functions in order to have our model scores


def score_ECG (M0_LVESV_3D,M0_LVED_3D,M0_LA_tot_EmF,M0_LA_strain_conduit) :
    return 2.628 + (0.035*M0_LVESV_3D) - (0.034*M0_LVED_3D) - (0.053*M0_LA_tot_EmF) - (0.261*M0_LA_strain_conduit)


def score_Clinical (GLYC, Urea) :
    return -68.028 + (3.126*GLYC) + (6.953*Urea)

def score_Metabolites (Arginine, Met_MetSufoxide, Kynurenine):
    return 36.33 - (3.79*Arginine) - (27.73*Met_MetSufoxide) + (3.60*Kynurenine)


