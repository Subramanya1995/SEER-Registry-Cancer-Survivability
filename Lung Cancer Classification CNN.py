# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 01:11:06 2020

@author: dshre
"""

import pandas as pd

lung_cancer=pd.read_csv('final_respiratory_cancer.csv',index_col=0)

lung_cancer.replace(to_replace={'MAR_STAT':9,'RACE1V':99,'AGE_DX':999,'SEQ_NUM':99,
                                  'Lateral':9,'GRADE':9,'DX_CONF':9,'CSEXTEN':999,
                                  'CSLYMPHN':999,'DAJCCT':88,'DAJCCN':88,'DAJCCM':88,
                                  'SURGSCOF':9,'SURGSITF':9,'NO_SURG':9,'AGE_1REC':99,
                                  'RAC_RECA':9,'RAC_RECY':9,'HST_STGA':9,'INTPRIM':9,
                                  'ERSTATUS':9,'PRSTATUS':9,'SRV_TIME_MON':9999,'SRV_TIME_MON_FLAG':9,
                                  'HER2':9,'BRST_SUB':9,'MALIGCOUNT':99,'BENBORDCOUNT':99,
                                  'RAD_SURG':9},value=pd.np.nan,inplace=True)

lung_cancer.replace({'EOD10_PN':{95:pd.np.nan,96:pd.np.nan,97:pd.np.nan,98:pd.np.nan,99:pd.np.nan},
                       'EOD10_NE':{95:pd.np.nan,96:pd.np.nan,97:pd.np.nan,98:pd.np.nan,99:pd.np.nan},
                       'CSTUMSIZ':{990:0,991:10,992:20,993:30,994:40,995:50,996:pd.np.nan,997:pd.np.nan,998:pd.np.nan,
                                   999:pd.np.nan,888:pd.np.nan},
                       'DAJCCSTG':{88:pd.np.nan,90:pd.np.nan,99:pd.np.nan},
                       'DSS1977S':{8:pd.np.nan,9:pd.np.nan},'SURGPRIF':{90:pd.np.nan,98:pd.np.nan,99:pd.np.nan},
                       'ADJTM_6VALUE':{88:pd.np.nan,99:pd.np.nan},'ADJNM_6VALUE':{88:pd.np.nan,99:pd.np.nan},
                       'ADJM_6VALUE':{88:pd.np.nan,99:pd.np.nan},'ADJAJCCSTG':{88:pd.np.nan,90:pd.np.nan,99:pd.np.nan}
                       },inplace=True)

lung_cancer.dropna(axis=0,how='any',subset=['YEAR_DX','SRV_TIME_MON'],inplace=True)

columns=lung_cancer.isna().sum(axis=0)/len(lung_cancer)

columns_list=list(columns[columns<0.2].index)

lung_cancer=lung_cancer.filter(items=columns_list,axis=1)

stats=lung_cancer.describe().loc['50%']
catg=lung_cancer.mode()

drop_cols=['MDXRECMP','YEAR_DX','CSVFIRST','CSVLATES','CSVCURRENT','ICCC3WHO',
           'ICCC3XWHO','CODPUB','CODPUBKM','STAT_REC','IHSLINK','VSRTSADX','ODTHCLASS',
           'CSTSEVAL','CSRGEVAL','CSMTEVAL','ST_CNTY','SRV_TIME_MON','SRV_TIME_MON_FLAG',
           '1year_survival','5year_survival']
catg_cols=['REG','MAR_STAT','RACE1V','SEX','PRIMSITE','LATERAL','BEHO2V', 'BEHO3V',
           'DX_CONF','REPT_SRC','CSMETSDX','DAJCCT','DAJCCN','DAJCCM','DAJCCSTG','DSS1977S',
           'SCSSM2KO','SURGPRIF','SURGSCOF','SURGSITF','NO_SURG','TYPE_FU','AGE_1REC','SITERWHO',
           'ICDOTO9V','ICDOT10V','BEHTREND','HISTREC','HISTRECB','CS0204SCHEMA','RAC_RECA',
           'RAC_RECY','ORIGRECB','HST_STGA','FIRSTPRM','SUMM2K','AYASITERWHO','LYMSUBRWHO',
           'INTPRIM','CSSCHEMA','ANNARBOR','RADIATNR','RAD_SURG','CHEMO_RX_REC']
num_cols=['AGE_DX','YR_BRTH','SEQ_NUM','EOD10_NE','CSEXTEN','CSLYMPHN','HISTO2V',
          'HISTO3V','CS1SITE','CS25SITE','REC_NO','MALIGCOUNT','BENBORDCOUNT']

values=dict()
for i in catg_cols:
    values[i]=catg[i][0]
for i in num_cols:
    values[i]=stats[i]

lung_cancer.fillna(value=values,inplace=True)

lung_cancer['survival_classes']=lung_cancer.apply(lambda row: 
    '<=6months' if (row.SRV_TIME_MON<=6) 
    else ('0.5-2yrs'  if (row.SRV_TIME_MON<=24) else '>2yrs'),axis=1)

from numpy.random import seed
from tensorflow import set_random_seed
import numpy as np

from sklearn.model_selection import train_test_split
#from sklearn.naive_bayes import MultinomialNB
#from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.utils import resample

from sklearn.preprocessing import LabelEncoder
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense, Conv1D, Dropout, Flatten
from sklearn.utils import class_weight
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
'''
data=lung_cancer[lung_cancer['YEAR_DX'].between(2004,2010)].drop(columns=drop_cols+['survival_classes'])
target=lung_cancer[lung_cancer['YEAR_DX'].between(2004,2010)]['survival_classes']
data=pd.get_dummies(data,prefix=catg_cols,columns=catg_cols,drop_first=False)

class_weights = dict(enumerate(class_weight.compute_class_weight('balanced',
                                             pd.np.unique(target),target)))
'''
data=lung_cancer[lung_cancer['YEAR_DX'].between(2004,2010)].drop(columns=drop_cols)
low_survival=data[data['survival_classes']=='<=6months']
mid_survival=data[data['survival_classes']=='0.5-2yrs']
high_survival=data[data['survival_classes']=='>2yrs']

mid_survival=resample(mid_survival,replace=True,n_samples=len(low_survival),random_state=21)
high_survival=resample(high_survival,replace=True,n_samples=len(low_survival),random_state=21)

data_upsampled=pd.concat([low_survival,mid_survival,high_survival],axis=0)
    
data=data_upsampled.drop(columns=['survival_classes'])
target=data_upsampled['survival_classes']
data=pd.get_dummies(data,prefix=catg_cols,columns=catg_cols,drop_first=False)

train_data,test_data,train_target,test_target=train_test_split(data,target,test_size=0.2,random_state=101)

scaler=StandardScaler()
train_data=pd.DataFrame(scaler.fit_transform(train_data),index=train_data.index,columns=train_data.columns)
test_data=pd.DataFrame(scaler.transform(test_data),index=test_data.index,columns=test_data.columns)

train_data=train_data.reshape(train_data.shape[0],1,train_data.shape[1])
test_data=test_data.reshape(test_data.shape[0],1,test_data.shape[1])

encoder = LabelEncoder()
encoder.fit(train_target)
encoded_train_target = encoder.transform(train_target)
dummy_train_target = np_utils.to_categorical(encoded_train_target)

encoded_test_target=encoder.transform(test_target)
dummy_test_target = np_utils.to_categorical(encoded_test_target)

seed(100)
set_random_seed(100)

model=Sequential()
    
model.add(Conv1D(50, 1, input_shape=train_data.shape[1:], activation='relu'))
model.add(Dropout(0.2))
model.add(Conv1D(20, 1, activation='relu'))
model.add(Dropout(0.2))
model.add(Flatten())
model.add(Dense(dummy_train_target.shape[1], activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

hist=model.fit(train_data, dummy_train_target, epochs=30, batch_size=100, verbose=1, validation_data=(test_data,dummy_test_target))

_, accuracy = model.evaluate(train_data, dummy_train_target)
_, test_accuracy = model.evaluate(test_data, dummy_test_target)

print('Train Accuracy=',accuracy)
print('Test Accuracy=',test_accuracy)

epoch_num = np.arange(0, 30)
plt.figure()
plt.plot(epoch_num, hist.history["loss"], label="train_loss")
plt.plot(epoch_num, hist.history["val_loss"], label="val_loss")
plt.plot(epoch_num, hist.history["acc"], label="train_acc")
plt.plot(epoch_num, hist.history["val_acc"], label="val_acc")
plt.title("Training Loss and Accuracy")
plt.xlabel("Epoch #")
plt.ylabel("Loss/Accuracy")
plt.legend()
plt.savefig('Lung Cancer CNN Epoch Plot')

#y_hat_train = model.predict(pos_train_data1, verbose=1)
y_hat_train_class = model.predict_classes(train_data, verbose=1)
#y_hat_train_dummy = np_utils.to_categorical(y_hat_train_class)

#y_hat_test = model.predict(pos_test_data1, verbose=1)
y_hat_test_class = model.predict_classes(test_data, verbose=1)
#y_hat_test_dummy = np_utils.to_categorical(y_hat_test_class)
print('Training Set Performance')
conf_matrix_ann = confusion_matrix(encoder.inverse_transform(encoded_train_target), encoder.inverse_transform(y_hat_train_class))
print(conf_matrix_ann)

cr_ann = classification_report(encoder.inverse_transform(encoded_train_target), encoder.inverse_transform(y_hat_train_class))
print(cr_ann)

print('Test Set Performance')
conf_matrix_ann = confusion_matrix(encoder.inverse_transform(encoded_test_target), encoder.inverse_transform(y_hat_test_class))
print(conf_matrix_ann)

cr_ann = classification_report(encoder.inverse_transform(encoded_test_target), encoder.inverse_transform(y_hat_test_class))
print(cr_ann)
