from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
from twilio.rest import Client
import random
import pandas as pd
import en_core_web_sm
import spacy
from google_trans_new import google_translator
import re
from word2number import w2n
 
 
 
##########################   text analysis    ##############################3

       
        
class textprocess():
    productinfo ={"warna":56,"amul":56,"nandini":58,"gokul":54,'litre':1,'kilo':1,
                 'mugdal':70,'masoordal':80,'star':120,'safola':130,'vim':10}
    
    doc = {
    'instruction':['immediately','fast','before','as soon as'],
        'offers' :['discounts'],
        'enquiry':['do' , 'are','is','if','can','what','where','when','how','many','much','show'],
        'order'  :['give','order', 'add','want'],
        "subcat" :['milk','dal','oil',"soap"],
        'product':['mugdal','toordal','harbhara','masoor','maggie'],
        'weight' :['kilo','grams','litre'],
        'company':['nesle','sunflower','amul', 'warna','nandini','sugar','gokul','star','gemini','safola','vim','wheel'],
        'price'  :['rate','price','netrate','total'],
       'quantity':["a",'1','10','2', '3','4', '5', 'one', 'two' ,'three', 'four', 'five' ,'half','per'],
      'greetings':["thank"]
        }
    text =doc['company']+doc['offers']+ doc["order"]+doc["product"]+doc["price"]+doc["quantity"]+doc['enquiry']+doc['subcat']+doc['weight']
    text=''.join(text)
    nlp = en_core_web_sm.load()
    total = {"+917666779269":0}
    cart = {"+917666779269":""}
    
    def __init__(self,cust):
        self.cust = cust

    def regex(self,senti):
        my = []
        sent = senti.split()
        print(0)
        for i in sent:
            try:
                x=re.search(i,self.text)
                my.append(x.group())
            except:
             #   print(0)
                pass
        return my
    
    def formdict(self,sent):
        ok = self.data_parts(sent )
        mp2={}
        for i in ok:
            mp = self.analysis(ok[i])
            if mp!={}:
                mp2.update(mp)
        return mp2
                
    def hinglish(self,sent,x):
        translator = google_translator()
        result = translator.translate(sent, lang_src="en",lang_tgt='mr')
        if x==1:
            return result
        elif x==2:
            final = translator.translate(result,lang_src = "mr", lang_tgt='en')
            return final
        else:
            return sent
    
    def meaning(self,word):
        for i in self.doc:
            if word in self.doc[i]:
                return i  

    def analysis(self,lis):
        book = {}
      
        for j in lis:
            
            m = self.meaning(j)
            
            if m != None:
                book[m] = j
        return book
    
    def tree_enquiry(self,mp , sr = '',flag=0):
        doc = self.doc
        print(1)
        productinfo = self.productinfo
        if 'enquiry' in mp:
            flag  += 1
            if 'subcat' in mp:
                flag+=1
                sr += mp['subcat']
                if 'company' in mp:
                    flag+=1
                    if 'price' in mp:
                        pce = productinfo[mp['company']]
                        flag+=1
                        if 'quantity' in mp:
                            net = pce * int(mp['quantity'])
                        else:
                            net = pce*1
                        if "weight" in mp:
                            return "the price of {} {} {} is {}".format(mp['quantity'],mp['weight'],mp['company'],net)
                        else:
                            return "the price of {} {} {} is {}".format(mp['quantity'],'litre',mp['company'],net)
                    else:
                        return "Yes ,your demanded item {} is available".format(mp['company'])
                else:
                    return switch1(str((doc['subcat'].index(mp['subcat']))+1))
            else:
                if 'product' in mp:
                    flag+=1
                    if 'price' in mp:
                        pce = productinfo['product']
                        flag+=1
                        if 'quantity' in mp:
                            net = pce * mp['quantity']
                        else:
                            net = pce*1
                        if "weight" in mp:
                            return "the price of {}{} is {}".format(mp['quantity'],mp['weight'],mp['product'])
                    else:
                        return "Yes ,your demanded item {} is available".format(mp['product'])
                else:
                    return "item not available in our stock"
        else:
            return self.tree_order(mp,'')
    
    def tree_order(self,mp , sr = '' ,flag=0):
        doc = self.doc
        productinfo = self.productinfo
        if 'order' in mp:
            flag  += 1
            if 'subcat' in mp:
                flag+=1
                sr += mp['subcat']
                if 'company' in mp:
                    flag+=1
                    sr=" "+mp['company']+ ' '+sr
                    pce = productinfo[mp['company']]
                    if 'quantity' in mp:
                        net = pce * int(mp['quantity'])
                    else:
                        net = pce*1
                        mp['quantity']=1
                    if "weight" in mp:
                        sr+="    " + str(mp['quantity'])+' X '+mp['weight']+"   "+str(net)
                        
                    else:
                        sr+="    " + str(mp['quantity']) +"   "+str(net)
                    self.cart[self.cust] += "\n" + sr
                    return  self.cart[self.cust] 
                else:
                    return switch1(str((doc['subcat'].index(mp['subcat']))+1))
            else:
                if 'product' in mp:
                    flag+=1
                    sr+=mp['product']
                    pce = productinfo[mp['product']]
                    if 'quantity' in mp:
                        net = pce * mp['quantity']
                    else:
                        net = pce*1
                        mp['quantity'] = 1
                    if "weight" in mp:
                        sr += '    ' + mp['quantity']+' '+mp['weight']+'    '+str(net)
                        
                    else:
                        sr += '   ' + mp['quantity']+'    '+str(net)
                    self.cart[self.cust] += "\n" + sr
                    return  self.cart[self.cust]
                else:
                    return "item not available in our stock"
        else:
             return 0

    def data_parts(self,text="give 1 litre warana milk"):
        common = {"noun":[],"verb":[],"adj":[],"digit":[],"unknown":[],"stop":[],"pronoun":[]}
        doc = self.nlp(text)
        #df = pd.DataFrame({"word":[],"noun":[],"adj":[],"verb":[],"digit":[],"punct":[],"stopword":[]})
        for token in doc:
        #    df.loc[len(df)]=[token, token.pos_=='NOUN',token.pos_=="ADJ",token.pos_=="VERB" ,token.is_digit ,token.is_punct,token.is_stop ]
            if token.pos_=="NOUN":
                common["noun"].append(token.text)
            elif token.pos_ == "PRON":
                common["pronoun"].append(token.text)
            elif token.pos_=="ADJ":
                common['adj'].append(token.text)
            elif token.pos_=="VERB":
                common['verb'].append(token.text)
            elif token.is_digit == True:
                common['digit'].append(token.text)
            elif token.is_stop == True:
                #pass
                common['stop'].append(token.text)
            elif token.is_punct == True:
                pass
            else:
                common['unknown'].append(token.text)
        return common
    
    def last(self,sent,flag=0):
        obj = self
        om = self.hinglish(sent,flag)
        pm = obj.formdict(om)
        print(pm)
        return self.tree_enquiry(pm)
         
##########################    process of chatbot   #############################

 

def finalcart(my_list,obj,cust):
    #i=0
    s = obj.cart[cust]
    si = s
    for item in my_list:
        #if item[-1] == "1":
        #i+=1
        s+= cart(item[1],item[2],item[3])
        #else:
         #   return s
    if s == si:
        pass
    else:
        obj.cart[cust] += s
    return obj.cart[cust]

def cart(x,y,z):
    dic1={"11":"amul milk","12":"warna milk","13":"gokul milk","14":"nandini milk",
          "21":"Mug dal","22":"Masoor dal","23":"Harbhara dal","24":"Toordal",
          "31":"Fortune oil","32":"Gemini oil","33":"Safola oil","34":"Star oil",
          "41":'Surfexcel soap',"42":"vim soap","43":"wheel soap","44":"tiptop soap"  }
    price_dict = {'1':{1:56,2:56,3:56,4:56},'2':{ 1:80,2:60,3:70,4:70,5:75},'3':{1:130,2:128,3:120,4:120,5:115},'4':{1:10,2:10,3:8,4:7,5:6}}
    return dic1[x+y]+"      " + z + " X " + "quan      " + str((price_dict[x][int(y)]) * int(z))

def switch0(arg0="Hi"):
    return switch1("Hi")

def switch1(argument): 
    mydict = {"Hi": 'जी वस्तू मागवायची आहे जस कि जर दूध हवे असेल तर 1 ,बिस्किट्स साठी 3 ,इ. याप्रमाणे आकडे निवडा ..🙂\n1: milk \n2:dal\n3:oilProducts\n4: Soap ',
              "1":"code       company       rate(inRs)\n 1            amul milk            56 \n 2            warna milk          56 \n  3            gokul milk           56 \n  4            nandini milk        54",
               "2":"Code.        Company.          Rate \n 1.             Mug.                  80/kg\n 2.             Masoor.            60/kg\n 3.            Harbhara.          70/kg \n 4.             Toordal.            70/kg \n 5.             Masoordal.       75/kg",
               "3":"Code.         Company.       Price \n  1.               Fortune          130/kg \n 2.               Gemini.          128/kg \n 3.                Safola.          120/kg \n 4.               Star.                120/kg \n 5.                Kirtigold.       115/kg",
               "4":"code       company       rate(inRs) \n 1.         surfexcel soap         10 \n 2         vim soap                  10 \n 3         wheel soap               8 \n 4         tiptop soap               7 \n 5         hamam soap            6",
             "Hi2.0": " to add next item in your cart,make your next choices \n1: milk \n2:dal\n3:oilProducts\n4: Soap ",
             }    
    
    a = "plz give correct input option number.I am still in learning phase."
    return  (mydict.get(argument, a))

    
def switch2(arg3): 
    switcher = {
            "1": "how many litres of milk do you want?", 
            "2": "how many grams or KGs of Dal you want to buy?", 
            "3": "how many Kgs of oil do you need?",
            "4": "how many soaps do you want?",
            }
    return switcher.get(arg3 , "nothing")

def urls(args):
    dic = {"1":'https://i.ibb.co/SrNmjbK/outfile.jpg',
           "2":'https://i.ibb.co/dQQsnc8/outfile.jpg',
           "3":'https://i.ibb.co/hLVx7x1/outfile.jpg',
          "4":'https://i.ibb.co/bRZD1vh/outfile.jpg'}
    return dic[args]

def switch3(arg3):
    switchof="your product has been added to your cart..\nselect the correct option-- \n 1. add next item to cart \n 2. place order and payment"
    return switchof
  
def switch4(arg4):
    dictl = {"1":switch1("Hi"),
             "2":"your order is taken by our side",
            }
    return dictl.get(arg4," I don't understand your response plz make it correct")
  
def random_response(arg):
    randomdict = {
        1:"sorry I didn't hear that ",
        2:"please specify your input in correct manner which I can understand",
        3:"plz give the correct input so I can understand.\nTo order new item just send *Hi* here" ,
        4:"Ohh I didn't see that coming make it more specific in a way I can understand",
        5:"you can simply state *Hi* for making new order"
    }
    return randomdict[arg]


def sendtxt(obj1,msg):
    return obj1

def next(a,b,cust):
    ap = textprocess(cust)
    pm = ap.last(b,0)
    if pm != 0:
        return pm
    else:
        return a.add_and_show(b,ap)

def rules():
    mp = '*WELcome to SuPeR MaRkeT* ...\n enjoy the new way of whatsapp shopping with your *trustworthy local businesses*\n\n shortkeys to place the orders ,checking prices,payments,cartlist etc...\n *CAT*-to get the list of products\n\n*CART*-to get to know about items you have added \n\n*PLACE*- confirming and go towards payments\n\n*ADD*- specifying this will help to directly add products in your cart\n\n*RATE*- rate our service out of 10\n\n*KHATA*- know your history of last 7 days orders\n\n*INST*- write specific instruction deemands for your product delivery '
    return mp

 

#################################################  CLASSES CODE FOR PROCEDURE THAT CHATBOT WILL FOLLW     ##################
    
class sub1():

    cart_df = {"+917666779269":pd.DataFrame({"+917666779269":[]})}
    mainDB={"+917666779269":[]}
    pot1 = {"+917666779269":[]}          
    pot  = {"+917666779269":[]}           
    
    def __init__(self,cust):
        self.cust=cust
        
    def add_and_show(self,arg,obj): 
        if arg in ["Hi","hi"]:
            self.pot[self.cust] = ["hi"]
            return  sendtxt(switch1("Hi"),self.cust)
        else:
            if arg == "cat":
                self.pot[self.cust] = ["hi"]
                if self.pot1[self.cust]==[]:   # this is for helping new user
                    return switch1("Hi")
                else:
                    return switch("Hi2.0")
            elif arg=="cart":
                sp = obj.cart[self.cust]
                if sp=="" and self.pot1[self.cust]==[]:
                     return "your cart is empty \njust send *Hi* and add items in your cart"
                else:
                     return "your cart till now\n" + finalcart(self.pot1[self.cust],obj,self.cust)
                    
            elif arg =="place":
                    #self.pot1[self.cust].append(self.pot[self.cust])
                    self.mainDB[self.cust].append(self.pot[self.cust])
                    mpl = obj.cart[self.cust]
                    self.pot[self.cust] = []
                    self.pot1[self.cust]=[]
                    if mpl == "":
                        return sendtxt("you cannot place the order as you dont have any items in your cart",self.cust )
                    else:
                        obj.cart[self.cust]=""
                        return "thanks for shopping with us\n" + mpl
            elif arg in ["1","2","3","4","5"]:
                self.pot[self.cust].append(arg)
                pot = self.pot[self.cust]
                if len(pot) == 2:
                    if pot[-1] in "1234":
                        return urls(pot[-1])#switch1(pot[-1])]
                    else:
                        return sendtxt("plz give the correct input sdo I can understand.",self.cust) 
                elif len(pot) == 3:
                    if pot[-1] in "12345":
                        return sendtxt(switch2(pot[-2]),self.cust)
                    else:
                        return sendtxt("plz give the correct input sdo I can understand.",self.cust)
    
                elif len(pot) == 4:
                    if len(pot)==4:
                        #self.pot[self.cust] = []
                        self.pot1[self.cust].append(self.pot[self.cust])
                        return sendtxt(switch3(pot[-1]),self.cust)
                elif len(pot)==5:
                    if pot[-1]=="1":
                        #self.pot1[self.cust].append(self.pot[self.cust])
                        self.pot[self.cust] = ["hi"]
                        return sendtxt(switch1("Hi2.0") , self.cust)
                    elif pot[-1] == "2":
                        #self.pot1[self.cust].append(self.pot[self.cust])
                        self.mainDB[self.cust].append(self.pot[self.cust])
                        mpl = finalcart(self.pot1[self.cust],obj,self.cust)
                        self.pot[self.cust] = []
                        self.pot1[self.cust]=[]
                        #
                        return sendtxt("Thank you for shopping with us.....\nyour ordered items are--\nno.      item name    Netrate\n" + mpl ,self.cust)
                        #return col_to_str(self.cart_df[self.cust].iloc[:,-1])
                    else:
                        return  sendtxt("plz give the correct input sdo I can understand.",self.cust) 
                else:
                    self.pot[self.cust].pop(-1)
                    return sendtxt("plz give the correct input so I can understand.\nTo order new item just send *Hi* here",self.cust) 

            else:# type(arg) == str:
                self.pot[self.cust].append(arg)
                pot = self.pot[self.cust]
                if len(pot)==4:
                    return sendtxt(switch3(pot[-1]),self.cust)
                else:
                    self.pot[self.cust].pop(-1)
                    return sendtxt(random_response(random.randint(1,5)),self.cust)
                
contacts  = {'+917666779269':sub1('+917666779269')}

def sms_reply(msg,remote_number = "+917666779269"):
     
    am = msg.lower()  

    if remote_number in contacts:
        contacts[remote_number].cart_df[remote_number].loc[len(contacts[remote_number].cart_df[remote_number].index) , remote_number] = am
        print(remote_number)
        mk=next(contacts[remote_number],am,remote_number)
        
    else:
        contacts[remote_number]=sub1(remote_number)
        contacts[remote_number].pot[remote_number]=[]
        contacts[remote_number].pot1[remote_number]=[]
        contacts[remote_number].mainDB[remote_number]=[]
        contacts[remote_number].cart_df={remote_number:pd.DataFrame({remote_number:[]})}
        contacts[remote_number].cart_df[remote_number].loc[len(contacts[remote_number].cart_df[remote_number].index) , remote_number] = am
        #mk = next(contacts[remote_number],am)
        mk = rules()
    return str(mk)


