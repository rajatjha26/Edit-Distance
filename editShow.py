from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from langdetect import detect
from nltk import tokenize
import re
import json

app = Flask(__name__)

@app.route('/',methods = ['GET', 'POST'])
def upload_file():
   return render_template('editShow.html')
	
@app.route('/postmethod', methods = ['GET', 'POST'])
def postmethod():
   if request.method == 'POST':
      data2 = request.form['text1']
      data1 = request.form['text2']
      lang=detect(data1)
      sentence_splitted_src=[]
      sentence_splitted_trg=[]
      result=[]
      para=1
      for para_src,para_trg in zip(data1.split("\n"),data2.split("\n")):
         sent=1
         if(lang=="en"):
            sentence_splitted_src=tokenize.sent_tokenize(para_src)
            sentence_splitted_trg=tokenize.sent_tokenize(para_trg)
         else:
            sentenceEnders = re.compile(r"""(?:(?<=[\|!?])|(?<=[\।]))\s+""",re.MULTILINE |re.UNICODE)
            sentence_splitted_src=sentenceEnders.split(para_src)
            sentence_splitted_trg=sentenceEnders.split(para_trg)
         for src_sen,trg_sen in zip(sentence_splitted_src,sentence_splitted_trg):
            word_list_rev=[]
            src_word=src_sen.split()
            trg_word=trg_sen.split()
            src_word_list = [words.lower() for words in src_word]
            trg_word_list = [words.lower() for words in trg_word]
            matrix = [[0 for x in range(len(trg_word_list) + 1)] for x in range(len(src_word_list) + 1)]

            for x in range(len(src_word_list) + 1):
               matrix[x][0] = x
            for y in range(len(trg_word_list) + 1):
               matrix[0][y] = y

            for x in range(1, len(src_word_list) + 1):
               for y in range(1, len(trg_word_list) + 1):
                  if src_word_list[x - 1] == trg_word_list[y - 1]:
                        matrix[x][y] = min(
                           matrix[x - 1][y] + 1,
                           matrix[x - 1][y - 1],
                           matrix[x][y - 1] + 1
                        )
                  else:
                        matrix[x][y] = min(
                           matrix[x - 1][y] + 1,
                           matrix[x - 1][y - 1] + 1,
                           matrix[x][y - 1] + 1
                        )
            edit_dist=matrix[len(src_word_list)][len(trg_word_list)]
            while(len(src_word_list)>0 and len(trg_word_list)>0):
               src_len=len(src_word_list)
               trg_len=len(trg_word_list)
               if(src_word_list[-1]==trg_word_list[-1]):
                  word_list_rev.append('<span class=NOOP>'+str(src_word[-1])+'</span>')
                  src_word_list.pop()
                  trg_word_list.pop()
                  src_word.pop()
                  trg_word.pop()
               else:
                  if(matrix[src_len][trg_len]==matrix[src_len-1][trg_len-1]+1):
                        word_list_rev.append('<span class=Update>'+'<span class=Remove>'+'<del>'+str(trg_word[-1])+'</del>'+'</span>'+" "+'<span class=Added>'+str(src_word[-1])+'</span>'+'</span>')
                        src_word_list.pop()
                        trg_word_list.pop()
                        src_word.pop()
                        trg_word.pop()
                  elif(matrix[src_len][trg_len]==matrix[src_len][trg_len-1]+1):
                        word_list_rev.append('<span class=Delete><del>'+str(trg_word[-1])+'</del></span>')
                        trg_word_list.pop()
                        trg_word.pop()
                  else:
                        word_list_rev.append('<span class=Insert>'+str(src_word[-1])+'</span>')
                        src_word_list.pop()
                        src_word.pop()
            if(len(src_word)>0):
               while(len(src_word)):
                  word_list_rev.append('<span class=Insert>'+str(src_word[-1])+'</span>')
                  src_word.pop()
            elif(len(trg_word)>0):
               while(len(trg_word)):
                  word_list_rev.append('<span class=Delete><del>'+str(trg_word[-1])+'</del></span>')
                  trg_word.pop()
            word_list_rev.reverse()
            sentence=""
            for word in word_list_rev:
               sentence=sentence+" "+word
            result.append({"sent":sentence,"edit_dist":"P"+str(para)+"S"+str(sent)+": "+str(edit_dist)})
            sent=sent+1
         result.append({"sent":"<hr>","edit_dist":"<br>"})
         para=para+1
      return(json.dumps(result))
		
if __name__ == '__main__':
   app.run(debug = True)