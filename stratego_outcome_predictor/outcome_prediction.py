import math
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression


ALL_FEATURE_MEANS = [5.10150370e+00, 5.07488738e+00, 6.19225266e-01, 6.25744087e-01, 4.91521206e-01, 4.89703763e-01, 5.69290718e+01, 6.08428395e+01, 5.76824974e+01, 5.69303630e+01, 8.26110580e-01, 8.03715309e-01, 9.77855885e-01, 1.01131545e+00, 1.61881257e+01, 1.67927196e+01, 2.89852725e+01, 2.85394885e+01, 2.47690107e+01, 2.50297635e+01, 1.80889425e+01, 1.83682013e+01, 4.81401578e-01, 4.81206653e-01, 6.19225266e-01, 6.25744087e-01, 1.75353419e+02, 1.77864972e+02, 9.89948407e-01, 1.70435699e-01, 1.74607699e-01, 4.05018127e+00, 4.14321944e+00, 2.10164975e+02, 7.96075785e-01, 6.65796336e-01, 2.54319799e+02, 2.56671802e+02, 5.47332859e+00, 4.74820876e+00, 4.55629000e+01, 4.59208389e+01, 1.78736630e+01, 1.87011509e+01, 1.24008945e+00, 1.23524450e+00, 4.29424875e+01, 4.22942670e+01, 1.17649976e+00, 1.10742186e+02, 6.79372969e+00, 7.02377945e+01, 1.06996459e+01, 1.15642979e+01, 6.94930595e+01, 8.04350508e+00, 1.12716845e+02, 1.48980321e+00, 1.10020728e+00, 1.57915177e+02, 8.58962601e+00, 1.10527848e+02, 1.65958764e+01, 1.70711236e+01, 1.07903998e+02, 9.93189587e+00, 1.60280945e+02, 1.44426040e+00, 1.36495128e+00, 1.10877166e+02, 7.71241028e+00, 6.94500119e+01, 1.14833800e+01, 1.07034980e+01, 6.97742062e+01, 7.15828933e+00, 1.13083453e+02, 1.32903680e+00]

ALL_FEATURE_VARIANCE = [1.42624807e+00, 1.44187489e+00, 4.65716260e-02, 4.35923158e-02, 4.81144629e-02, 4.85352385e-02, 1.51852301e+03, 1.70855741e+03, 4.92223909e+02, 5.23312148e+02, 1.83479814e-02, 2.28883989e-02, 5.16233837e-02, 4.06078882e-02, 4.87848136e+01, 4.81499447e+01, 7.11024465e+01, 6.62906094e+01, 7.45146015e+01, 6.97477054e+01, 6.95520950e+01, 6.47374900e+01, 4.06661704e-02, 4.02323006e-02, 4.65716260e-02, 4.35923158e-02, 3.87606609e+03, 3.76380490e+03, 2.07552820e-02, 7.18005080e-03, 7.42350267e-03, 3.49947789e+00, 3.74229412e+00, 2.63255731e+04, 1.62339129e-01, 2.22511575e-01, 1.72729788e+04, 1.79271869e+04, 4.15553435e+02, 3.41949984e+02, 9.49717860e+02, 1.03382229e+03, 3.35515711e+01, 3.20451091e+01, 1.51099764e+00, 1.50653646e+00, 2.62166954e+03, 2.64032609e+03, 7.57105585e+01, 3.02775231e+03, 5.09327027e+02, 3.60815278e+03, 6.29587403e+02, 6.76118212e+02, 3.66233343e+03, 6.12278063e+02, 3.07295212e+03, 1.02686948e+02, 6.86467917e+01, 5.17658589e+03, 6.62239599e+02, 7.17882399e+03, 1.09234855e+03, 1.13336417e+03, 7.12958712e+03, 7.90566502e+02, 5.22327210e+03, 1.00306928e+02, 8.82694839e+01, 3.05718218e+03, 5.73605439e+02, 3.53951592e+03, 6.59857062e+02, 6.34403556e+02, 3.69766883e+03, 5.41040296e+02, 3.04339104e+03, 9.11658088e+01]

SELECTED_FEATURES = [0,1,2,3,5,6,7,10,11,12,13,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,34,35,36,37,38,39,40,41,42,43,50,55,58,59,60,61,62,63,64,65,66,67,70,75]
TRAINED_CLASSIFIER_PATH = "SOMETHING.pkl"


class StrategoClassifier:

    self.TRAINED_CLASSIFIER_PATH = "trained_stratego_classifier.pkl"

    def __init__(self):
        self.clf = joblib.load(self.TRAINED_CLASSIFIER_PATH)

    def predict_outcome_from_features(self, feature_container):
        """generates a prediction based on the provided features. Predicts the probabilities of outcomes; blue wins(0) or red wins(1)"""
        standardized_values = standardize_feature_values(feature_container.extracted_features)
        prediction = self.clf.predict_proba(standardized_values)
        return prediction

    def standardize_feature_values(self, extracted_features):
        """standardize feature values (convert to z-scores by removing the mean and dividing by the stdev)"""
        feature_indices = sorted(extracted_features.keys())
        list_of_features = list()
        standardized_feature_values = list()
        for feature_index in SELECTED_FEATURES:
             feature_value = extracted_features[feature_index]
             feature_mean = ALL_FEATURE_MEANS[feature_index]
             feature_stdev = math.sqrt(ALL_FEATURE_VARIANCE[feature_index])
             centered_feature = feature_value - feature_mean
             z_score = centered_feature / feature_stdev
             standardized_feature_values.append(z_score)
        list_of_features.append(standardized_feature_values)
        return list_of_features

