# Et Raf Ömrü Tahmin Sistemi (AI Tabanlı)

## Genel Bakış

Bu proje, sıcaklık ve mikrobiyal büyüme verilerini kullanarak et ürünlerinin raf ömrünü ve bozulma riskini tahmin eden yapay zeka tabanlı bir karar destek sistemidir.

Sistem, basit, anlaşılır ve ticari olarak uygulanabilir bir yapı sunar.

Kullanım alanları:
- Soğuk zincir takibi
- Gıda güvenliği yönetimi
- Stok optimizasyonu
- Erken bozulma tespiti

---

## Temel Özellikler

- Raf Ömrü Tahmini  
  Ürünün kaç gün daha güvenli kalacağını tahmin eder.

- Risk Sınıflandırması  
  Ürünleri düşük, orta, yüksek ve kritik risk olarak sınıflandırır.

- Risk Skoru (0–1 arası)  
  Teknik analiz için sayısal risk değeri üretir.

- Web Panel  
  Excel yükleyerek analiz yapma  
  Filtreleme ve görselleştirme  
  Sonuçları CSV olarak indirme

- Açıklanabilir Model  
  Basit ve güvenilir Ridge regresyon modeli kullanır.

---

## Sistem Yapısı

Girdi:
- Sıcaklık (Temperature_C)
- Gün (Day)
- Mikrobiyal yük (Total_Viable_Count)

Model:
- StandardScaler (ölçekleme)
- Ridge Regression

Çıktı:
- Tahmini kalan raf ömrü
- Risk skoru
- Risk seviyesi
- Önerilen aksiyon

---

## Veri Formatı

Excel dosyasında şu kolonlar bulunmalıdır:

Sample_ID  
Temperature_C  
Day  
Total_Viable_Count  

---

## Kurulum

Gerekli paketleri yüklemek için:

pip install streamlit pandas scikit-learn openpyxl matplotlib

---

## Çalıştırma

Uygulamayı başlatmak için:

streamlit run app.py

---

## Deploy (Render)

1. Projeyi GitHub’a yükle  
2. Render platformuna gir  
3. Yeni Web Service oluştur  
4. Aşağıdaki ayarları gir  

Build Command:
pip install -r requirements.txt

Start Command:
python -m streamlit run app.py --server.port=10000 --server.address=0.0.0.0

---

## Çıktı Açıklaması

Tahmini Kalan Gün:
Ürünün kaç gün daha dayanacağını gösterir.

Risk Skoru:
0 güvenli, 1 yüksek risk anlamına gelir.

Risk Seviyesi:
Kullanıcı dostu sınıflandırma sağlar.

Önerilen Aksiyon:
Operasyonel karar için öneri üretir.

---

## Ticari Değer

Bu sistem:

- Gıda israfını azaltır  
- Riskli ürünleri erken tespit eder  
- Lojistik ve stok kararlarını iyileştirir  
- Gıda güvenliğini artırır  

---

## Sınırlamalar

- Simüle veri kullanılmıştır  
- Sabit eşik değeri varsayılmıştır  
- Gerçek saha verisi ile henüz test edilmemiştir  

---

## Geliştirme Planı

- IoT sensör entegrasyonu  
- Gerçek zamanlı izleme  
- API servisi  
- Mobil uygulama  
- Gelişmiş modelleme  

---

## Sonuç

Bu proje, basit ve açıklanabilir modellerin gerçek dünyadaki gıda güvenliği problemlerine etkili çözümler sunabileceğini göstermektedir.
