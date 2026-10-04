# 🌈 Rainbow 5.0 Discord Bot

Rainbow 5.0, çok amaçlı ve gelişmiş özelliklere sahip, Discord.py ile yazılmış modern bir Discord botudur. Sunucu yönetimi, kapsamlı moderasyon araçları ve kullanıcı dostu eğlence/araç komutları ile sunucunuzu kolayca yönetmenizi sağlar. Hem Slash (/) komutlarını hem de klasik prefix komutlarını destekler.

## 🚀 Özellikler

### 🛡️ Moderasyon (`cogs/moderation.py`)
- **Kick, Ban & Unban:** Kullanıcıları sunucudan atın veya yasaklayın (ID ile yasaklama desteği).
- **Mute / Unmute:** Belirli bir süre için kullanıcıları susturun (Örn: `10m`, `2h`, `1d`).
- **Kanal Yönetimi:** Kanalları kilitleyin (`lock`), kilidini açın (`unlock`) veya yavaş mod (`slowmode`) ayarlayın.
- **Toplu Mesaj Silme:** Kanallardaki mesajları tek komutla temizleyin (`sil` / `purge`).
- **Rol Yönetimi:** Kullanıcılara hızlıca rol verin veya rollerini alın (`rolver`, `rolal`).
- **Uyarı Sistemi:** Kullanıcılara uyarı verin, uyarı sayılarına göre otomatik rol ataması yapın ve kayıtları listeleyin.
- **Karaliste Sistemi:** İstenmeyen kullanıcıları karalisteye ekleyerek sunucudan otomatik yasaklanmalarını sağlayın.

### 🛠️ Araçlar (`cogs/tools.py`)
- **AFK Sistemi:** AFK olduğunuzu belirtin, sizi etiketleyenlere otomatik bilgi verilsin ve isminize `[AFK]` eklensin.
- **QR Kod Oluşturucu:** İstediğiniz herhangi bir metin veya bağlantıyı QR koda dönüştürün.
- **Hesap Makinesi:** Matematiksel işlemleri hızlıca Discord üzerinden yapın.
- **Arka Plan Silici:** Görsellerin arka planını yapay zeka ile saniyeler içinde temizleyin (`rembg` entegrasyonu).
- **Hava Durumu:** İstediğiniz şehrin anlık hava durumu verilerine ulaşın.
- **Bot Daveti:** Botun davet bağlantısını hızlıca paylaşın.

### ⚙️ Yönetim (`cogs/management.py`)
- **Özelleştirilebilir Prefix:** Her sunucu için özel bir prefix (önek) belirleyin.
- **Sahip Komutları:** Sadece bot kurucusunun kullanabileceği, botu yeniden başlatma (`restart`), kapatma (`botkapat`) ve sunucu listesini görme (`sunucularim`) komutları.

## 📥 Kurulum

1. Depoyu bilgisayarınıza klonlayın veya indirin.
2. Gerekli Python kütüphanelerini yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
   *(Eğer arka plan silme özelliğini kullanacaksanız `rembg` paketinin yüklü olduğundan emin olun)*
3. Proje dizininde bir `.env` dosyası oluşturun ve aşağıdaki değişkenleri doldurun:
   ```env
   DISCORD_TOKEN=senin_discord_bot_tokenin_buraya
   WEATHER_API_KEY=openweathermap_api_anahtarin
   KURUCU_ID=kendi_discord_kullanici_id_numaran
   ```
4. Botu başlatın:
   ```bash
   python rainbow5.0.py
   ```

## 📝 Notlar
- Botun sorunsuz çalışması ve Slash komutlarının senkronize olması için Discord Developer Portal üzerinden **Message Content Intent**, **Server Members Intent** ve **Presence Intent** izinlerinin açık olduğundan emin olun.
- Veriler `utils/storage.py` üzerinden JSON tabanlı olarak veya uygun bir depolama sisteminde saklanır.

## 🤝 Katkıda Bulunma
Herhangi bir hata bulursanız veya özellik eklemek isterseniz, Issues bölümünden bildirebilir veya Pull Request gönderebilirsiniz.


NOT : utils klasörüne init dosyasından konmalıdır cogsta olandan
