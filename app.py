from flask import Flask, render_template, url_for, redirect, request, flash
import SQLServer, MailGonder, CihazBilgi, Sifreleme
import time, random
from datetime import datetime
from importlib import reload
import IndexYorum
from ButunModeller import ModelSorgula
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
app = Flask(__name__)
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/')
def index():
     reload(IndexYorum)
     Users=SQLServer.Sorgula("SELECT * FROM FuncSKUsers ORDER BY UserAdiSoyadi")
     return render_template('index.html', ToplamModel=IndexYorum.ToplamModel, RastGeleSecim=IndexYorum.Rastgele, SonProje=IndexYorum.SonProje, AbonelikPaket=IndexYorum.APaket, WSabit=IndexYorum.WSabit)
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/MesajGonder', methods=["POST"])
def AnaSayfadanMesajGonder():
     UserName = request.form.get("AdSoyad")
     UserMail = request.form.get("MailAdres")
     UserPhone = request.form.get("Telefon")
     Konu = request.form.get("Konu")
     Mesaj = request.form.get("Mesaj")

     MesajGovdesi =  f"Mesajı Gönderenin Konusu: {Konu}\n"
     MesajGovdesi =  f"Mesajı Gönderenin Adı Soyadı: {UserName}\n"
     MesajGovdesi += f"Mesajı Gönderenin Mail Adresi: {UserMail}\n"
     MesajGovdesi += f"Mesajı Gönderenin Telefonu: {UserPhone}\n"
     MesajGovdesi += f"Mesaj Tarih/Saati: {datetime.now()}\n\n"
     MesajGovdesi += f"Mesaj Gövdesi:\n\n{Mesaj}.\n"
     
     MailGonder.MailGonderme(IndexYorum.WSabit[0]["Sutun08"], f"Ana Sayfadan {UserName} Mesaj Gönderdi...", MesajGovdesi)
     return render_template("MsgMesajAlindi.html")
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route("/UyelikTalepEdildi.html", methods=["POST"])
def UyelikTalep():
     Kontrol = False
     Mukerrer = False
     Durum = request.form.get("check") 
     
     if Durum is None:
          Mesaj1="Kullanım şarlarımızı Kabul Etmelisiniz"
          Mesaj2="Aksi Halde Üyelik Talebiniz Kabul Edilmeyecektir"
          return render_template("MsgStop.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
     else:
          try:
               Sifre1 = request.form.get("Sifre1")
               Sifre2 = request.form.get("Sifre2")
               if Sifre1 == Sifre2:
                    Ad = request.form.get("Ad").upper().strip()
                    Soyad = request.form.get("Soyad").upper().strip()
                    GSMNo = request.form.get("GsmNo").upper().strip()
                    MailAdres = request.form.get("MailAdres").lower().strip()
                    UserName=request.form.get("UserName").lower().strip()
                    MailAdres=MailAdres.lower().strip()
                    Paket=request.form.get("Abonelik").upper().strip()
                    Users = SQLServer.Sorgula(f"SELECT * FROM SKUsers WHERE RTRIM(UserMailAdress)='{MailAdres}'")
                    ##Burada Blokaj kontrolleri yapılacak....
                    if len(Users) > 0:
                         if Users[0]["IsBlock"]:
                              #Bu Mail Adresi Blokeli
                              Kontrol=False
                              Mesaj1="BLOKELISINIZ"
                              Mesaj2="TEKRAR ABONE OLAMAZSINIZ"
                              return render_template("MsgStop.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
                         else:
                              #Bu Mail Adresi Kullanılıyor
                              Users = SQLServer.Sorgula(f"SELECT * FROM SKUsers WHERE RTRIM(UserMailAdress)='{MailAdres}' AND RTRIM(UserName)='{UserName}'")
                              if len(Users) > 0:
                                   Kontrol=False
                                   Mesaj1="Mail Adresi & Kullanıcı Adı Hatası"
                                   Mesaj2="Başka Bir Üye Tarafından Kullanılıyor..."
                                   return render_template("MsgStop.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
                              else:
                                   Kontrol=True
                                   Mukerrer=True

                    else:
                         Kontrol=True 
                         Mukerrer=False
                         
               else:
                    Kontrol=False
                    Mesaj="Sifreler Birbiriyle Aynı Olmalıdır..."
                    return render_template("UyeOlun.html", Mesaj=Mesaj)
          except Exception as e:
               Kontrol=False
               Mesaj="Hata Meydana Geldi. Tekrar Deneyiniz..."
               return render_template("UyeOlun.html", Mesaj=Mesaj)
          

          if Kontrol:
               #Kayıt İşlemlerine geldim
               RS = random.randint(100000, 999999)
               BirlesikAd = Ad + ' ' + Soyad
               HashPass = str(Sifreleme.VeriyiSifrele(Sifre1))
               SQL = "INSERT INTO SKUsers (IsAdmin, UserAuth, VerifyMailCode, UserAdiSoyadi, UserName, PassWord, UserGSMNumber, UserMailAdress, IsBlock, PaketAdi, OnOff, AyrilmaTarihi) "
               SQL += f"VALUES (0, '', {RS}, '{BirlesikAd}', '{UserName}', '{HashPass}', '{GSMNo}', '{MailAdres}', 0, '{Paket}', 0, '9999-01-01')"
               Durum = SQLServer.Calistir(SQL)
               if Durum:
                    Mesaj1 = "Teşekkür Ederiz"
                    Mesaj2 = "Talebinizi Aldık Sizden Abonelik Bedeli Dekontunu Bekliyoruz"
                    if Mukerrer:
                         Mesaj2 += " (Mukerrer Talep)"
                    return render_template("MsgMesajAlindi.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
               else:
                    Mesaj1="Ooops!!!"
                    Mesaj2="Beklenilmeyen Bir Hata Meydana Geldi (SQL)"
                    return render_template("MsgError.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/IndexUyeGiris.html')
def IndexUyeGiris():
     GirisYapanCihazKodu = CihazBilgi.CihazBilgisiOkuma()
     if GirisYapanCihazKodu != '':
          Sifreli = Sifreleme.VeriyiSifrele(GirisYapanCihazKodu)
          User  = SQLServer.Sorgula("SELECT * FROM SKUsers WHERE UserAuth = '" + Sifreli + "'")
          if len(User) > 0:
               if User[0]["IsBlock"]:
                    Mesaj1 = "BLOKELISINIZ"
                    Mesaj2 = "GİRİŞ YAPAMAZSINIZ"
                    return render_template("MsgStop.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
               else:
                    UserNo = User[0]["UserID"] 
                    GirisNo = AnaSayfaIlkGirisi(UserNo)
                    if GirisNo<2:
                         Users = SQLServer.Sorgula("SELECT * FROM FuncSKUser() ORDER BY DRM DESC, UserAdiSoyadi")
                    if GirisNo == 0:
                         return render_template('AdmKullanicilar.html', Users=Users)
                    elif GirisNo == 1:
                         return render_template('User.html', methods=['POST'])
                    else:
                         return render_template('UyeGiris.html')
          else:
               return render_template('UyeGiris.html')
     else:
          return redirect('index.html')
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/ButunModeller.html')
def ButunModeller():
    id = random.randint(101, 105)
    SQLGrublar = "SELECT * FROM SKGrublar WHERE GrubID IN (SELECT GrubID FROM SKModeller) ORDER BY GrubID"
    Groups = SQLServer.Sorgula(SQLGrublar)  # Assuming SQLServer.Sorgula is properly defined
    Models = ModelSorgula(id)  # Assuming ModelSorgula is properly defined
    return render_template('ButunModeller.html', Groups=Groups, Models=Models)
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/Models/<string:id>')
def GrupModelleri(id):
    SQLGrublar = "SELECT * FROM SKGrublar WHERE GrubID IN (SELECT GrubID FROM SKModeller) ORDER BY GrubID"
    Groups = SQLServer.Sorgula(SQLGrublar)  # Assuming SQLServer.Sorgula is properly defined
    Models = ModelSorgula(id)  # Assuming ModelSorgula is properly defined
    return render_template('ButunModeller.html', Groups=Groups, Models=Models)
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/Sosyal.html')
def Sosyal():
     return render_template('Sosyal.html')
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/UyeOlun.html')
def UyeOlun():
     Mesaj=""
     return render_template('UyeOlun.html',Mesaj=Mesaj)
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/KullanimSartlari.html')
def KullanimSartlari():
     return render_template('KullanimSartlari.html')
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route('/UyeGirisSonKontroller', methods=["POST"] )
def SonKontrolYorumlar():
     GirisMusaade = False
     GirisYapanCihazKodu =  CihazBilgi.CihazBilgisiOkuma()
     if GirisYapanCihazKodu != '':
          MailAdres     = request.form.get("MailAdres")
          UserName      = request.form.get("UserName")
          UserPass      = request.form.get("PassWord")
          OnayKodu      = request.form.get("OnayKodu")
          Durum = MailAdres is not None
          Durum = Durum and UserName is not None
          Durum = Durum and UserPass is not None
          Durum = Durum and OnayKodu is not None
          
          if Durum:
               UserPass      = Sifreleme.VeriyiSifrele(UserPass)
               SifreliCihaz  = Sifreleme.VeriyiSifrele(GirisYapanCihazKodu)
               AnaSorgu=f"RTRIM(UserName)='{UserName}' AND RTRIM(PassWord)='{UserPass}' AND RTRIM(UserMailAdress)='{MailAdres}'"
               
               PasswKontrol1 = SQLServer.Sorgula(f"SELECT * FROM SKUsers WHERE {AnaSorgu}") 
               CihazKontrol2 = SQLServer.Sorgula(f"SELECT * FROM SKUsers WHERE {AnaSorgu} AND RTRIM(UserAuth)='{SifreliCihaz}'") 

               if len(PasswKontrol1) == 1 and len(CihazKontrol2) == 1:
                    if not(PasswKontrol1[0]["IsBlock"]):
                         # Kullanıcı Adı ve Şifresi ve Cihaz Numarası Uyuştu. Daha  Önce Bu Cihazla Girdiğinden Atlıyoruz.
                         GirisMusaade=True
                    else:
                         Mesaj1 = "BLOKELISINIZ"
                         Mesaj2 = "GİRİŞ YAPAMAZSINIZ"
                         return render_template("MsgStop.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
               elif len(PasswKontrol1) == 0:
                    # Kullanıcı Adı ve Şifresi Uyuşmadı
                    Mesaj1 = "HATALI BİLGİ GİRİŞİ"
                    Mesaj2 = "eMail, KullanıcıAdı, Şifre ve OnayKodu Uyuşmamıştır"
                    return render_template("MsgStop.html", Mesaj1=Mesaj1, Mesaj2=Mesaj2)
               elif len(PasswKontrol1) == 1 and len(CihazKontrol2) == 0:
                    UserAuth = PasswKontrol1[0]["UserAuth"]
                    if UserAuth.strip() > "":
                         if PasswKontrol1[0]["IsBlock"] == False:
                              ## Yetkisiz Giriş Algılandı Bloke Edip Aboneliğini İptal Edeceğiz....
                              TarihZaman = datetime.now()
                              formatli_tarih = TarihZaman.strftime("%d.%m.%Y %H.%M.%S.%f")
                              #Kullanıcıya Mail Gidiyor
                              #Kullanıcıya Mail Gidiyor
                              #Kullanıcıya Mail Gidiyor
                              MailAdres = PasswKontrol1[0]["UserMailAdress"]
                              Baslik    = "Yetkisiz Cihazla Giriş Algılandı..."
                              Konu      = "Kayıtlı bulunan cihaz haricinde başka bir cihazla girişiniz algılandı...\n\n"
                              Konu     += "Sözleşme Şartları gereğince üyeliğiniz iptal edilmiştir.\n\n"
                              Konu     += F"Tarih/Saat :{formatli_tarih}"
                              MailGonder.MailGonderme(MailAdres, Baslik, Konu)
                         
                              #Admin'e Mail Gidiyor
                              #Admin'e Mail Gidiyor
                              #Admin'e Mail Gidiyor
                              Baslik    ="Kullanıcı Kaçak Girişi Algılandı ve Bloke Edildi..."
                              Konu      = "Aşağıdaki Kullanıcının Kayıtlı bulunan cihaz haricinde başka bir cihazla giriş algılandı...\n\n"
                              Konu     += "Sözleşme Şartları gereğince üyeliği iptal edilerek blokaj konulmuştur.\n\n"
                              Konu     += "Bu üyenin mail adresi ve telefon numarası kara listede saklanmaya devam edecektir.\n\n"
                              
                              Konu     += F"Kullanıcının Adı Soyadı: {PasswKontrol1[0]["UserAdiSoyadi"].strip()}\n"
                              Konu     += F"Kullanıcının UserName: {PasswKontrol1[0]["UserName"].strip()}\n"
                              Konu     += F"Kullanıcının GSM Numarası: {PasswKontrol1[0]["UserGSMNumber"].strip()}\n"
                              Konu     += F"Kullanıcının Mail Adresi: {PasswKontrol1[0]["UserMailAdress"].strip()}\n"
                              Konu     += F"Kullanıcının Üyelik Tarihi: {PasswKontrol1[0]["UyelikTalepTarihi"].strftime("%d.%m.%Y %H.%M.%S.%f")}\n"
                              Konu     += F"Kullanıcının Üyelik Paketi: {PasswKontrol1[0]["PaketAdi"].strip()}\n"
                              Konu     += F"Kullanıcının Üyelik Onay Tarihi: {PasswKontrol1[0]["UyelikOnayTarihi"].strftime("%d.%m.%Y %H.%M.%S.%f")}\n"
                              Konu     += F"Blokaj Tarihi: {formatli_tarih}\n"
                              MailGonder.MailGonderme(IndexYorum.WSabit[0]["Sutun08"], Baslik, Konu)

                              max_deneme = 50
                              deneme = 0

                              while deneme < max_deneme:
                                   try:
                                        SQLServer.Calistir(f"UPDATE SKUsers SET IsBlock=1, BlockTarihi='{TarihZaman}', OnOff=0 WHERE UserID={PasswKontrol1[0]["UserID"]}")
                                   except Exception as e:
                                        deneme += 1
                                        time.sleep(1)  
                                   else:
                                        break

                         return render_template('MsgBlocked.html')
                    else:
                         GirisMusaade=True
                        
          else:
               Mesaj1="Ooops!!!"
               Mesaj2="Bütün Satırları Doldurmalısınız"
               return render_template('MsgStop.html', Mesaj1 = Mesaj1, Mesaj2=Mesaj2)
     else:
          Mesaj1="Ooops!!!"
          Mesaj2="Cihazınız Bilgilerine Erişim İzni Vermelisiniz"
          return render_template('MsgStop.html', Mesaj1 = Mesaj1, Mesaj2=Mesaj2)
     
     if GirisMusaade:
          SQLServer.Calistir(f"Update SKUsers SET UserAuth='{SifreliCihaz}', OnOff = 1 WHERE UserID={PasswKontrol1[0]["UserID"]}")
          UserNo = PasswKontrol1[0]["UserID"]
          GirisNo = AnaSayfaIlkGirisi(UserNo)
          if GirisNo<2:
               Users = SQLServer.Sorgula("SELECT * FROM FuncSKUser() ORDER BY DRM DESC, UserAdiSoyadi")
          if GirisNo == 0:
               return render_template('AdmKullanicilar.html', methods=['POST'], Users=Users)
          elif GirisNo == 1:
               return render_template('User.html', methods=['POST'])
          else:
               return render_template('UyeGiris.html')
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
def AnaSayfaIlkGirisi(UserID):
     if UserID > 0:
          PasswKontrol1 = SQLServer.Sorgula(f"SELECT IsAdmin FROM SKUsers WHERE UserID={UserID}") 
          if PasswKontrol1[0]["IsAdmin"]:
               return 0
          elif PasswKontrol1[0]["OnOff"]:
               return 1
          else:
               return 2
     else:
          return 2
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
@app.route("/UyeAktifle/<string:id>")
def ModelAcma(id):
     return id


if __name__ == '__main__':
    # app.run(ssl_context='adhoc', debug=True)
    app.run(debug=True)
    Gecici = 1

