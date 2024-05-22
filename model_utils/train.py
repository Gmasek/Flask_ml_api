import os
from datetime import datetime

import IPython
import IPython.display
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
import yfinance as yf
from window_gen import *
from data_colletion import *
import keras

MAX_EPOCHS = 20

class Baseline(tf.keras.Model):
  def __init__(self, label_index=None):
    super().__init__()
    self.label_index = label_index

  def call(self, inputs):
    if self.label_index is None:
      return inputs
    result = inputs[:, :, self.label_index]
    return result[:, :, tf.newaxis]

def compile_and_fit(model, window, patience=2):
  early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                    patience=patience,
                                                    mode='min')

  model.compile(loss=tf.keras.losses.MeanSquaredError(),
                optimizer=tf.keras.optimizers.Adam(),
                metrics=[tf.keras.metrics.MeanAbsoluteError()])

  history = model.fit(window.train, epochs=MAX_EPOCHS,
                      validation_data=window.val,
                      callbacks=[early_stopping])
  return history

if __name__ == "__main__":
    df = get_indicators(get_stocks_data("GOOG","2000-01-01","2024-05-01"))
    column_indices = {name: i for i, name in enumerate(df.columns)}
    train_df,test_df,val_df = data_split(df=df)
    single_step_window = WindowGenerator(24,24,1,train_df,val_df,test_df,label_columns=["Target"])
    baseline = Baseline(label_index=column_indices['Target'])

    baseline.compile(loss=keras.losses.MeanSquaredError(),
                 metrics=[keras.metrics.MeanAbsoluteError()])

    val_performance = {}
    
    
    performance = {}
    val_performance['Baseline'] = baseline.evaluate(single_step_window.val, return_dict=True)
    performance['Baseline'] = baseline.evaluate(single_step_window.test, verbose=0, return_dict=True)
    linear = tf.keras.Sequential([ tf.keras.layers.Dense(units=1)])
    history = compile_and_fit(linear, single_step_window)
    val_performance['Linear'] = linear.evaluate(single_step_window.val, return_dict=True)
    performance['Linear'] = linear.evaluate(single_step_window.test, verbose=0, return_dict=True)