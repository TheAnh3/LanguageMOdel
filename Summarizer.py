
import pandas as pd
import re
import spacy
from time import time
import sys
import codecs
import matplotlib.pyplot as plt
from matplotlib import pyplot
import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer 
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Input, LSTM, Embedding, Dense, \
    Concatenate, TimeDistributed
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping


tf.config.run_functions_eagerly(True)
tf.data.experimental.enable_debug_mode()
summary = pd.read_csv('D:/KISSAI - Python/Dataset/news_summary.csv', encoding='iso-8859-1',nrows=1000)
raw = pd.read_csv('D:/KISSAI - Python/Dataset/news_summary_more.csv', encoding='iso-8859-1',nrows=1000)
pre1 = raw.iloc[:, 0:2].copy()
pre2 = summary.iloc[:, 0:6].copy()
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


# To increase the intake of possible text values to build a reliable model
pre2['text'] = pre2['author'].str.cat(pre2['date'
       ].str.cat(pre2['read_more'].str.cat(pre2['text'
       ].str.cat(pre2['ctext'], sep=' '), sep=' '), sep=' '), sep=' ')


pre = pd.DataFrame()
pre['text'] = pd.concat([pre1['text'], pre2['text']], ignore_index=True)
pre['summary'] = pd.concat([pre1['headlines'], pre2['headlines']],ignore_index=True)
#print(pre.head(2))


# Remove non-alphabetic characters (Data Cleaning)
def text_strip(column):


   for row in column:
       row = re.sub("(\\t)", " ", str(row)).lower()
       row = re.sub("(\\r)", " ", str(row)).lower()
       row = re.sub("(\\n)", " ", str(row)).lower()


       # Remove _ if it occurs more than one time consecutively
       row = re.sub("(__+)", " ", str(row)).lower()


       # Remove - if it occurs more than one time consecutively
       row = re.sub("(--+)", " ", str(row)).lower()


       # Remove ~ if it occurs more than one time consecutively
       row = re.sub("(~~+)", " ", str(row)).lower()


       # Remove + if it occurs more than one time consecutively
       row = re.sub("(\+\++)", " ", str(row)).lower()


       # Remove . if it occurs more than one time consecutively
       row = re.sub("(\.\.+)", " ", str(row)).lower()


       # Remove the characters - <>()|&©ø"',;?~*!
       row = re.sub(r"[<>()|&©ø\[\]\'\",;?~*!]", " ", str(row)).lower()


       # Remove mailto:
       row = re.sub("(mailto:)", " ", str(row)).lower()


       # Remove \x9* in text
       row = re.sub(r"(\\x9\d)", " ", str(row)).lower()


       # Replace INC nums to INC_NUM
       row = re.sub("([iI][nN][cC]\d+)", "INC_NUM", str(row)).lower()


       # Replace CM# and CHG# to CM_NUM
       row = re.sub("([cC][mM]\d+)|([cC][hH][gG]\d+)", "CM_NUM", str(row)).lower()


       # Remove punctuations at the end of a word
       row = re.sub("(\.\s+)", " ", str(row)).lower()
       row = re.sub("(\-\s+)", " ", str(row)).lower()
       row = re.sub("(\:\s+)", " ", str(row)).lower()


       # Replace any url to only the domain name
       try:
           url = re.search(r"((https*:\/*)([^\/\s]+))(.[^\s]+)", str(row))
           repl_url = url.group(3)
           row = re.sub(r"((https*:\/*)([^\/\s]+))(.[^\s]+)", repl_url, str(row))
       except:
           pass


       # Remove multiple spaces
       row = re.sub("(\s+)", " ", str(row)).lower()


       # Remove the single character hanging between any two spaces
       row = re.sub("(\s+.\s+)", " ", str(row)).lower()


       yield row


def getText_strip(row):


       text_strip1 = text_strip(row)
       text_clean = [''.join(text_strip1)]
       return text_clean


# print(getText_strip(pre['text']))
# print(getText_strip(pre['summary']))



nlp = spacy.load('en_core_web_sm', disable=['ner', 'parser'])

# DELETE

print("Start")

#text = [str(doc) for doc in nlp.pipe(text_strip(pre['text']), batch_size=500)]
# print(getText_strip(pre['text']))
def process_text(texts):
    """Process a list of texts using spaCy and return a list of strings"""
    docs = list(nlp.pipe(str(texts), batch_size=500))
    return [' '.join([tok.text for tok in doc]) for doc in docs]

def process_summary(summaries):
    """Process a list of summaries using spaCy and return a list of strings"""
    docs = list(nlp.pipe(summaries, batch_size=500))
    return ['_START_ ' + ' '.join([tok.text for tok in doc]) + ' _END_' for doc in docs]

# Example usage:
# processed_text = process_text(pre['text'])
# print(processed_text)
# print('text process finish')

# processed_summary = process_summary(pre['summary'])
# print(processed_summary)
# print('summary process finish')
# print("End")

processed_text = text_strip(pre['text'])
processed_summary = text_strip(pre['summary'])
text = [str(doc) for doc in nlp.pipe(processed_text, batch_size=10)]
summary = ['_START_ '+ str(doc) + ' _END_' for doc in nlp.pipe(processed_summary, batch_size=10)]
# print(text[0])
# print(summary[0])

pre['cleaned_text'] = pd.Series(text)
pre['cleaned_summary'] = pd.Series(summary)


# Check how much % of text have 0-100 words
# cnt = 0
# for i in pre['cleaned_text']:
#     if len(i.split()) <= 100:
#         cnt = cnt + 1
# print(cnt / len(pre['cleaned_text']))

# Model to summarize the text between 0-15 words for Summary and 0-100 words for Text
max_text_len = 100
max_summary_len = 15

cleaned_text = np.array(pre['cleaned_text'])
cleaned_summary= np.array(pre['cleaned_summary'])

short_text = []
short_summary = []

for i in range(len(cleaned_text)):
    if len(cleaned_summary[i].split()) <= max_summary_len and len(cleaned_text[i].split()) <= max_text_len:
        short_text.append(cleaned_text[i])
        short_summary.append(cleaned_summary[i])
        
post_pre = pd.DataFrame({'text': short_text,'summary': short_summary})
# print(post_pre.head(2))
post_pre['summary'] = post_pre['summary'].apply(lambda x: 'sostok ' + x \
        + ' eostok')

# print(post_pre.head(2))
def Excluding_rareWords(tokenizer):
    thresh = 5
    cnt = 0
    tot_cnt = 0

    for key, value in tokenizer.word_counts.items():
        tot_cnt = tot_cnt + 1
        if value < thresh:
            cnt = cnt + 1
    print("% of rare words in vocabulary: ", (cnt / tot_cnt) * 100)

    return tot_cnt - cnt

x_tr, x_val, y_tr, y_val = train_test_split(
    np.array(post_pre["text"]),
    np.array(post_pre["summary"]),
    test_size=0.1,
    random_state=0,
    shuffle=True,
)
print (x_tr)
x_tokenizer = Tokenizer() 
y_tokenizer = Tokenizer()     
x_tokenizer.fit_on_texts(list(x_tr))
y_tokenizer.fit_on_texts(list(y_tr))

def Excluding_rareWords(tokenizer):
    thresh = 5
    cnt = 0
    tot_cnt = 0

    for key, value in tokenizer.word_counts.items():
        tot_cnt = tot_cnt + 1
        if value < thresh:
            cnt = cnt + 1
    print("% of rare words in vocabulary: ", (cnt / tot_cnt) * 100)

    return tot_cnt - cnt

def SetTokenizer(TR,VAL,string):
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(list(TR))
    tokenizer = Tokenizer(num_words = Excluding_rareWords(tokenizer)) 
    tokenizer.fit_on_texts(list(TR))

    tr_seq = tokenizer.texts_to_sequences(TR) 
    val_seq = tokenizer.texts_to_sequences(VAL)

    # Pad zero upto maximum length
    tr = pad_sequences(tr_seq,  maxlen=max_text_len, padding='post')
    val = pad_sequences(val_seq, maxlen=max_text_len, padding='post')

    # Size of vocabulary (+1 for padding token)
    voc = tokenizer.num_words + 1
    # if (condition == True):
        # return tokenizer;    
    # else:
    match string:
        case 'x_tr': 
            return tr
        case 'x_val':
            return val
        case 'y_tr':
            return tr
        case 'y_val':
            return val
        case 'x_voc':
            return voc
        case 'y_voc':
            return voc                     
    # print("Size of vocabulary in X = {}".format(voc))
        # return voc;




def removeEmpty(y):
    ind = []

    for i in range(len(y)):
        cnt = 0
        for j in y[i]:
            if j != 0:
                cnt = cnt + 1
            if cnt == 2:
                ind.append(i)

    return ind

x_voc = SetTokenizer(x_tr,x_val,'x_voc')
y_voc = SetTokenizer(x_tr,x_val,'y_voc')
x_training =  SetTokenizer(x_tr,x_val,'x_tr')
y_training = SetTokenizer(y_tr,y_val,'y_tr')
x_validation = SetTokenizer(y_tr,y_val,'x_val')
y_validation = SetTokenizer(y_tr,y_val,'y_val')
print("x_tr before SetTokenizer() " + str(x_training))
print("y_tr before SetTokenizer() " + str(y_training))
# ind_tr = removeEmpty(y_training)
# ind_val = removeEmpty(y_validation)
# x_tr = np.delete(x_training, ind_tr, axis=0)
# y_tr = np.delete(y_training, ind_tr, axis=0)
# x_val = np.delete(x_validation, ind_val, axis=0)
# y_val = np.delete(y_validation, ind_val, axis=0)
print(x_tr,y_tr,x_val,y_val)
print("Shape of x_tr:", x_tr.shape)
print("Shape of y_tr:", y_tr.shape)
print("Shape of x_val:", x_val.shape)
print("Shape of y_val:", y_val.shape)

latent_dim = 300
embedding_dim = 200

# Encoder
encoder_inputs = Input(shape=(max_text_len, ))

# Embedding layer
enc_emb = Embedding(x_voc, embedding_dim,
                    trainable=True)(encoder_inputs)

# Encoder LSTM 1
encoder_lstm1 = LSTM(latent_dim, return_sequences=True,
                     return_state=True, dropout=0.4,
                     recurrent_dropout=0.4)
(encoder_output1, state_h1, state_c1) = encoder_lstm1(enc_emb)

# Encoder LSTM 2
encoder_lstm2 = LSTM(latent_dim, return_sequences=True,
                     return_state=True, dropout=0.4,
                     recurrent_dropout=0.4)
(encoder_output2, state_h2, state_c2) = encoder_lstm2(encoder_output1)

# Encoder LSTM 3
encoder_lstm3 = LSTM(latent_dim, return_state=True,
                     return_sequences=True, dropout=0.4,
                     recurrent_dropout=0.4)
(encoder_outputs, state_h, state_c) = encoder_lstm3(encoder_output2)

# Set up the decoder, using encoder_states as the initial state
decoder_inputs = Input(shape=(None, ))

# Embedding layer
dec_emb_layer = Embedding(y_voc, embedding_dim, trainable=True)
dec_emb = dec_emb_layer(decoder_inputs)
# Decoder LSTM
decoder_lstm = LSTM(latent_dim, return_sequences=True,
                    return_state=True, dropout=0.4,
                    recurrent_dropout=0.2)
(decoder_outputs, decoder_fwd_state, decoder_back_state) = \
    decoder_lstm(dec_emb, initial_state=[state_h, state_c])

# Dense layer
decoder_dense = TimeDistributed(Dense(y_voc, activation='softmax'))
decoder_outputs = decoder_dense(decoder_outputs)



# Define the model
model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

model.summary()

model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy',run_eagerly=True)
es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=2)
history = model.fit(
    [x_training, y_training[:, :-1]],
    y_training.reshape(y_training.shape[0], y_training.shape[1], 1)[:, 1:],
    epochs=1,
    callbacks=[es],
    batch_size=32,
    validation_data=([x_validation, y_validation[:, :-1]],
                     y_validation.reshape(y_validation.shape[0], y_validation.shape[1], 1)[:
                     , 1:]),
    )
pyplot.plot(history.history['loss'], label='train')
pyplot.plot(history.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()

reverse_target_word_index = y_tokenizer.index_word
reverse_source_word_index = x_tokenizer.index_word
target_word_index = y_tokenizer.word_index

# Inference Models

# Encode the input sequence to get the feature vector
encoder_model = Model(inputs=encoder_inputs, outputs=[encoder_outputs,
                      state_h, state_c])

# Decoder setup

# Below tensors will hold the states of the previous time step
decoder_state_input_h = Input(shape=(latent_dim, ))
decoder_state_input_c = Input(shape=(latent_dim, ))
decoder_hidden_state_input = Input(shape=(max_text_len, latent_dim))

# Get the embeddings of the decoder sequence
dec_emb2 = dec_emb_layer(decoder_inputs)

# To predict the next word in the sequence, set the initial states to the states from the previous time step
(decoder_outputs2, state_h2, state_c2) = decoder_lstm(dec_emb2,
        initial_state=[decoder_state_input_h, decoder_state_input_c])

# A dense softmax layer to generate prob dist. over the target vocabulary
decoder_outputs2 = decoder_dense(decoder_outputs2)

# Final decoder model
decoder_model = Model([decoder_inputs] + [decoder_hidden_state_input,
                      decoder_state_input_h, decoder_state_input_c],
                      [decoder_outputs2] + [state_h2, state_c2])
def decode_sequence(input_seq):
    
    # Encode the input as state vectors.
    (e_out, e_h, e_c) = encoder_model.predict(input_seq)

    # Generate empty target sequence of length 1
    target_seq = np.zeros((1, 1))

    # Populate the first word of target sequence with the start word.
    target_seq[0, 0] = target_word_index['sostok']

    stop_condition = False
    decoded_sentence = ''

    while not stop_condition:
        (output_tokens, h, c) = decoder_model.predict([target_seq]
                + [e_out, e_h, e_c])

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_token = reverse_target_word_index[sampled_token_index]

        if sampled_token != 'eostok':
            decoded_sentence += ' ' + sampled_token

        # Exit condition: either hit max length or find the stop word.
        if sampled_token == 'eostok' or len(decoded_sentence.split()) \
            >= max_summary_len - 1:
            stop_condition = True

        # Update the target sequence (of length 1)
        target_seq = np.zeros((1, 1))
        target_seq[0, 0] = sampled_token_index

        # Update internal states
        (e_h, e_c) = (h, c)

    return decoded_sentence

# To convert sequence to summary
def seq2summary(input_seq):
    newString = ''
    for i in input_seq:
        if i != 0 and i != target_word_index['sostok'] and i \
            != target_word_index['eostok']:
            newString = newString + reverse_target_word_index[i] + ' '

    return newString


# To convert sequence to text
def seq2text(input_seq):
    newString = ''
    for i in input_seq:
        if i != 0:
            newString = newString + reverse_source_word_index[i] + ' '

    return newString

reverse_target_word_index[0] = '<PAD>'

for i in range(0, 19):
    print ('Review:', seq2text(x_training[i]))
    print ('Original summary:', seq2summary(y_training[i]))
    print ('Predicted summary:', decode_sequence(x_training[i].reshape(1,
           max_text_len)))
    print ('\n')
print('finish')
# def Graph():  
#     text_count = []
#     summary_count = []

#     for sent in pre['cleaned_text']:
#         text_count.append(len(sent.split()))
    
#     for sent in pre['cleaned_summary']:
#         summary_count.append(len(sent.split()))
#     graph_df = pd.DataFrame() 
#     graph_df['text'] = text_count
#     graph_df['summary'] = summary_count

#     graph_df.hist(bins = 5)
#     plt.show()



# summary = ['_START_ '+ str(doc) + ' _END_' for doc in nlp.pipe(processed_summary, batch_size=500)]

#DELETE


# # Process text as batches and yield Doc objects in order
# if processed_text is not None:
#     text = []
#     for doc in nlp.pipe(processed_text, batch_size=500):
#         text.append(str(doc))

# else:
#     text = []
# #summary = ['_START_ '+ str(doc) + ' _END_' for doc in nlp.pipe(processed_summary, batch_size=500)]


# print(summary[0])