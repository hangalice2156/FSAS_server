# FSAS_server ft.django GUILDLINE
----
## 目錄:
1. 環境設置
2. 常用指令
3. 主要架構說明
4. 其他

----

## 環境設置
- 作業系統: 我自己個人是使用windows 10 1803版本開發的，不過基本上python 在各平台上都可以使用，即使在Linux 上應該也能順利開發

- 開發工具:
    - Python 3.7.2rc1
    - pip 19.2.3
    - Django 2.1.7 
    - Pillow 6.1.0 (Needed for imagefield)
    - fcm-django 0.2.21 (Needed for fcm service)

----

## 常用指令
基本上大部分的指令都是透過`manage.py` 完成的

- 啟動伺服器: `python manage.py runserver <host>:<port>` 預設127.0.0.1:8000

- 資料庫遷移: 
    - `python manage.py makemigration` 先查看架構是否有問題，做了那些改動
    
    - `python manage.py migration` 執行資料庫遷移
    
    - 如果需要重置遷移，參照: https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html

- 其他: 請參照官方文件

----

## 架構說明
- MVT Architecture: https://medium.com/@andyludeveloper/%E7%8E%A9-django-party-3-mtv-%E6%9E%B6%E6%A7%8B-60e1188434c4
 
--------分隔線--------

    - model: 主要是資料庫的架構，在View 當中`import models` 來對資料庫進行操作，而使用者、群組以及FCMDevice 這些也都有各自的資料庫model 可以拿來使用

    - 參考資料: https://ivanjo39191.pixnet.net/blog/post/144744012-python-django-%E5%AD%B8%E7%BF%92%E7%B4%80%E9%8C%84%28%E5%9B%9B%29-%E8%B3%87%E6%96%99%E5%BA%AB%E5%8F%8A%E5%BE%8C%E5%8F%B0%E7%AE%A1%E7%90%86

--------分隔線--------

    - view: 負責處理request，以及對於request 做出response，同時可以由這裡管理資料庫。注意Django 有csrf 的保護機制，這部分前端要注意

    - https://blog.techbridge.cc/2017/02/25/csrf-introduction/

    - Firebase Cloud Message: 
        * https://firebase.google.com/docs/cloud-messaging
        * https://github.com/xtrinch/fcm-django

    - 延伸閱讀: https://developer.mozilla.org/zh-TW/docs/Web/HTTP

--------分隔線--------

    - template: 基本上大多數的東西都由前端完成，這裡可以做一些東西，方便不需要前端的狀況下也可以測試


----

## 其他注意事項

### URLS
注意存取的路徑位置，在本教學中`127.0.0.1:8000/` 是沒有東西的

### 管理員
在這個範例中

- 管理員帳號: admin
- 管理員密碼: admin14789632

後臺位置: [host]:[port]/admin (ex:`127.0.0.1:8000/admin`)

!!!注意!!! 你應該將這個帳號改為更好的帳號名稱，並更換更強的密碼
這裡只是方便使用而已

Django 的官方教學文件有教你如何創造一個superuser 以及後台管理

注意settings.py 中 `SECRET_KEY` 還有 Fcm Django 設定的 `SERVER_KEY` 要設定

### ImageField
注意settings.py 中 media root 的設定，以及資料庫的儲存路徑

### ForeignKey 以及資料庫存取
注意存取的方法以及資料庫型態的類別，各個類別間的method 都不太一樣，有一些method 的參數是query set

可以用 `|=` 運算子來合併query set

### 其他
想到再寫