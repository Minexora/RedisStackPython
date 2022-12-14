# Redis Stack
Dataları json olarak cachelemek için kullanılmaktadır. İçerisinde search hizmetide barındırmaktadır.

## Redis Stack'i Yüklemek 
Redis Stack'i  yüklemek için docker'ın ve docker-compose'un yüklü olması gerekmektedir. Docker ve docker-compose yüklendikten sonra aşağıdaki komut yazılarak redis ve insight kurulumu gerçekleştirilir.
```bash
docker-compose up -d # docker compose daki servisleri ayağı kaldır anlamına gelir. '-d' detach modda açılması gerektiğini söyler.
```
Kurulumları gerçekleştirildikten sonra [http://localhost:8001/](http://localhost:8001/) adresine gidilerek redis kayıtları kontrol edilebilir. Redis volume üretmesi beklenmektedir bu sayede kayıtlar silinmez.

## Python Script
Redis için yazılan script **main.py** adlı dosyada yer almaktadır. Herhangi bir projede sınıf import edilerek doğrudan kullanılabilir. Projenin gereklilikleri;

- .env dosyası kök klasörede oluşturulmalıdır. .env dosyasında redis bilgileri yer almaktadır. Aşağıdaki gibi eklenebilir
    ```.env
    RedisHost=localhost
    RedisPort=6379
    ```
- Requirements yüklemek için aşağıdaki komutlar çalıştırılır.
    ```bash
    python3 -m venv venv # virtual evironmet oluşturmak için kullanılır.
    source /venv/bin/activate # Linux ve Mac için virtual evironmet aktif etmek için kullanılır.
    pip install -r req.txt # Gerekli olan tooların yüklenmesi için kullanılır.
    ```